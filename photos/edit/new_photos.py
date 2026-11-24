import cv2, numpy as np
from lama import inpaint
from upright import rotH, lean, inner_crop
import colour as C
U='/root/.claude/uploads/7abb9dae-ca94-57ca-8def-12ed6a733fcc/'
lsd = cv2.createLineSegmentDetector()
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

def keep_sat_light(src):
    """Brightening that keeps colour strength (same as the cover photo)."""
    sky=src.astype(np.float32)/255
    Y=(0.114*sky[...,0]+0.587*sky[...,1]+0.299*sky[...,2])
    base=cv2.GaussianBlur(Y,(0,0),30)
    gain=1+0.55*np.clip(0.45-base,0,0.45)/0.45
    Y2=np.clip(Y*gain,0,1)**0.93
    k=0.9; over=Y2>k; Y2[over]=k+(1-k)*np.tanh((Y2[over]-k)/(1-k))
    out=np.clip(sky*(Y2/np.maximum(Y,1e-3))[...,None],0,1)
    hsv=cv2.cvtColor((out*255).astype(np.uint8),cv2.COLOR_BGR2HSV).astype(np.float32); s=hsv[...,1]/255
    hsv[...,1]=np.clip((s+0.22*s*(1-s))*255,0,255)
    out=cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2BGR)
    blur=cv2.GaussianBlur(out,(0,0),1.6); return cv2.addWeighted(out,1.25,blur,-0.25,0)

def rects(shape, rs, lines=(), dil=7):
    m=np.zeros(shape[:2],np.uint8)
    for x0,y0,x1,y1 in rs: cv2.rectangle(m,(x0,y0),(x1,y1),255,-1)
    for pts,wd in lines: cv2.polylines(m,[np.array(pts)],False,255,wd)
    return cv2.dilate(m,np.ones((dil,dil),np.uint8))

def save(name, img): cv2.imwrite(f'new/{name}.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 93])
checks={}
import sys
which=sys.argv[1:]

# cover photo: house number on the mailbox
if not which or 'cover' in which:
    b=cv2.imread('out/house-old-bin4.png'); m=rects(b.shape,[(1238,951,1272,970)],dil=3)
    b5=inpaint(b,m,pad=60); cv2.imwrite('out/house-old-bin5.png',b5); checks['cover']=(b,b5,(1180,900,1320,1010))

# street view with driveway
if not which or 'street' in which:
    im=cv2.imread(U+'01583849-image.jpg'); m=rects(im.shape,[(1078,698,1102,714)],dil=3)
    c=inpaint(im,m,pad=60); checks['street']=(im,c,(1000,600,1250,800)); save('house-driveway',keep_sat_light(c))

# front door close-up
if not which or 'door' in which:
    im=cv2.imread(U+'bb4c4e07-image.jpg'); m=rects(im.shape,[(1296,798,1416,856)],dil=3)
    c=inpaint(im,m,pad=80); checks['door']=(im,c,(1100,650,1500,1000)); save('front-door',keep_sat_light(c))

# desk close-up (IMG_9489): cables under the desk
if not which or 'desk' in which:
    im=cv2.imread(U+'3edd4fda-image.jpg')
    m=rects(im.shape,[(1059,1097,1079,1117)],[([(1091,961),(1120,1008),(1115,1048),(1080,1072),(1048,1078)],7),
        ([(1103,975),(1093,1027),(1083,1067),(1075,1107)],7),([(1053,1070),(1061,1099),(1075,1115)],7),
        ([(1056,1008),(1075,1012),(1093,1016)],6),
        ([(1040,1100),(1032,1160),(1028,1215),(1038,1248),(1020,1255),(995,1250),(988,1210),(1000,1160)],7),([(1045,1172),(1040,1205),(1034,1230),(1026,1250)],9)],dil=7)
    c=inpaint(im,m,pad=200); checks['desk']=(im,c,(900,940,1200,1300))
    C.MODE['desk-closeup']='walls'; up,info=auto_upright(c,800); print('desk',info); save('desk-closeup',C.colour(up,'desk-closeup'))

# dining towards living room (IMG_9578): coasters, envelope, router on the TV stand
if not which or 'dining2' in which:
    im=cv2.imread(U+'0c58f675-image.jpg')
    m=rects(im.shape,[(86,852,156,908),(160,846,266,892),(1776,848,1840,898)],[([(1831,884),(1850,890),(1861,920)],5)],dil=5)
    c=inpaint(im,m,pad=200); checks['dining2']=(im,c,(60,820,300,920))
    C.MODE['dining-living']='walls'; up,info=auto_upright(c,1450); print('dining2',info); save('dining-living',C.colour(up,'dining-living'))

# kitchen and dining, landscape (IMG_9513): table items, trash can, clutter left of the sink, device right of the stove
if not which or 'kitchen2' in which:
    im=cv2.imread(U+'26ff065e-image.jpg')
    m=rects(im.shape,[(1436,814,1498,864),(1478,846,1580,890),(1150,810,1218,874),(362,682,440,722),(1022,676,1084,732),(1037,641,1057,661)],
        [([(376,660),(379,676),(382,692)],6),([(1047,645),(1042,665),(1046,685),(1050,702)],9)],dil=5)
    c=inpaint(im,m,pad=200); checks['kitchen2']=(im,c,(1130,790,1600,900)); checks['kitchen2b']=(im,c,(340,640,1080,740))
    C.MODE['kitchen-dining']='walls'; up,info=auto_upright(c,760); print('kitchen2',info); save('kitchen-dining',C.colour(up,'kitchen-dining'))

# hallway to the bathroom: nothing to remove
if not which or 'hall' in which:
    im=cv2.imread(U+'4a2d6af5-image.jpg'); C.MODE['hallway']='walls'; up,info=auto_upright(im,1100); print('hall',info); save('hallway',C.colour(up,'hallway'))

# living room towards entry and TV (IMG_9569): white box on the TV stand, cables at the side table
if not which or 'tv' in which:
    im=cv2.imread(U+'3d76fe60-image.jpg')
    m=rects(im.shape,[(776,672,818,694),(300,948,376,1012)],dil=5)
    c=inpaint(im,m,pad=200); checks['tv']=(im,c,(250,640,850,1020))
    C.MODE['living-entry']='walls'; up,info=auto_upright(c,760); print('tv',info); save('living-entry',C.colour(up,'living-entry'))

for k,(a,b,(x0,y0,x1,y1)) in checks.items():
    p=np.hstack([a[y0:y1,x0:x1],b[y0:y1,x0:x1]]); s=min(2.0,1100/p.shape[1]); cv2.imwrite(f'new/chk_{k}.jpg',cv2.resize(p,None,fx=s,fy=s))
