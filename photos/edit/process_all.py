import cv2, numpy as np, sys
from lama import inpaint
from lama_lowres import inpaint_lowres
from upright import rotH, lean, inner_crop, light

U = '/root/.claude/uploads/7abb9dae-ca94-57ca-8def-12ed6a733fcc/'
lsd = cv2.createLineSegmentDetector()


def poly(m, pts):
    cv2.fillPoly(m, [np.array(pts)], 255)


def dark_in(img, pts, thr=80, close=21):
    """Dark pixels (black objects, cables) inside a polygon, closed and dilated."""
    region = np.zeros(img.shape[:2], np.uint8); poly(region, pts)
    v = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[..., 2]
    m = ((v < thr) & (region > 0)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    return cv2.dilate(m, np.ones((9, 9), np.uint8))


def auto_upright(img, f, share=0.7):
    """Fit pitch/roll so long near-vertical lines become vertical; apply `share` of the pitch."""
    h, w = img.shape[:2]
    L = lsd.detect(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))[0][:, 0]
    segs = []
    for x1, y1, x2, y2 in L:
        l = np.hypot(x2 - x1, y2 - y1); a = np.degrees(np.arctan2(x2 - x1, y2 - y1)); a = (a + 90) % 180 - 90
        if l > h * 0.1 and abs(a) < 20: segs.append([(x1, y1), (x2, y2)])
    best = None
    for p in np.arange(-20, 20.01, 0.5):
        for r in np.arange(-3, 3.01, 0.5):
            H = rotH(w, h, f, p, r); e = [min(lean(H, s) ** 2, 25) for s in segs]   # clipped: robust to non-vertical lines
            e = sum(e)
            if best is None or e < best[0]: best = (e, p, r)
    _, p, r = best
    for s in np.arange(share, -0.01, -0.05):      # keep at least 85 % of the width
        H = rotH(w, h, f, p * s, r)
        x0, y0, cw, ch = inner_crop(H, w, h, w / h)
        if cw / w >= 0.85: break
    wp = cv2.warpPerspective(img, H, (w, h), flags=cv2.INTER_CUBIC)
    return wp[y0:y0 + ch, x0:x0 + cw], (p, r, round(s, 2), len(segs), round(cw / w, 2))


jobs = {}

# kitchen (IMG_9503): camera on the fridge, towel/clutter and charger cable left of the sink
def kitchen(img):
    m = np.zeros(img.shape[:2], np.uint8)
    poly(m, [(90, 434), (148, 434), (148, 496), (90, 496)])
    poly(m, [(1136, 708), (1228, 708), (1228, 750), (1136, 750)])
    cv2.polylines(m, [np.array([(1184, 668), (1192, 690), (1200, 716)])], False, 255, 7)
    return cv2.dilate(m, np.ones((7, 7), np.uint8))
jobs['kitchen'] = (U + '8de75834-image.jpg', kitchen, 760)

# open living/kitchen (IMG_9565): TV stand in the foreground (the TV itself is cropped off), keypad
def livingdining(img):
    m = np.zeros(img.shape[:2], np.uint8)
    poly(m, [(0, 940), (70, 1000), (145, 1095), (300, 1295), (320, 1512), (0, 1512)])
    return m
jobs['living-dining'] = (U + '2512033c-image.jpg', livingdining, 760)

# living room (IMG_9566): nothing to remove
jobs['living-room'] = (U + 'f6ddc7c8-image.jpg', None, 1450)

# bedroom with closet (IMG_9492): printer, care tag
def bed(img):
    m = np.zeros(img.shape[:2], np.uint8)
    poly(m, [(1005, 930), (1095, 918), (1158, 948), (1158, 1038), (1015, 1042), (1000, 990)])
    poly(m, [(1022, 1222), (1078, 1222), (1078, 1352), (1022, 1352)])
    return cv2.dilate(m, np.ones((11, 11), np.uint8))
jobs['bed'] = (U + '8d82d17c-image.jpg', bed, 760)

# dining (IMG_9514): coasters and envelope on the table
def dining(img):
    m = np.zeros(img.shape[:2], np.uint8)
    poly(m, [(950, 970), (1034, 970), (1034, 1050), (950, 1050)])
    poly(m, [(1008, 1018), (1150, 1018), (1150, 1076), (1008, 1076)])
    return cv2.dilate(m, np.ones((13, 13), np.uint8))
jobs['dining'] = (U + '6d28b7f6-image.jpg', dining, 1450)

# bathroom (IMG_9499): hair dryer, its cable and plug
def bathroom(img):
    m = dark_in(img, [(1290, 1310), (1390, 1310), (1390, 1430), (1360, 1520), (1460, 1640), (1460, 1840),
                      (1380, 1900), (1150, 1900), (1080, 1790), (1080, 1640), (1150, 1500), (1290, 1490)], close=7)
    poly(m, [(1306, 1430), (1354, 1430), (1354, 1500), (1306, 1500)])   # cable label
    cv2.ellipse(m, (1115, 1683), (48, 62), 0, 0, 360, 255, -1)          # gold ring of the dryer
    poly(m, [(1322, 1316), (1380, 1316), (1380, 1410), (1322, 1410)])   # plug
    return m
jobs['bathroom'] = (U + '5e4cd524-image.jpg', bathroom, 1100)

# shower (IMG_9498): nothing to remove
jobs['shower'] = (U + '7cf0a005-image.jpg', None, 1100)

# house (IMG_2490), Easter decorations already removed by patching
jobs['house'] = ('house-spring-clean.jpg', None, 1450)
jobs['bedroom-desk'] = ('bed_clean.jpg', None, 800)   # printer, tag and cables already removed

only = sys.argv[1:] or list(jobs)
for name in only:
    src, fn, f = jobs[name]
    img = cv2.imread(src)
    if name == 'living-dining':
        img = img[:, 200:]            # drop the TV at the left edge
    if fn:
        m = fn(img); cv2.imwrite(f'out/{name}-mask.png', m)
        img = inpaint_lowres(img, m, 0.5) if name == 'living-dining' else inpaint(img, m, pad=320)
    up, info = (img, 'not straightened') if name == 'shower' else auto_upright(img, f)
    cv2.imwrite(f'out/{name}-raw.png', up)
    out = light(up)
    cv2.imwrite(f'out/{name}.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 93])
    print(name, 'pitch/roll/segments/kept width', info)
