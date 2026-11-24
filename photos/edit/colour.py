import cv2, numpy as np
from light2 import light2

WALL_B = 7.0      # cream walls (b* in CIELAB, positive = yellow)
CEIL_B = 1.5      # white ceiling, a touch of warmth

# ceiling outlines in the straightened photos (traced on a grid)
CEILING = {
    'kitchen':       [(0, 0), (1733, 0), (1733, 310), (1400, 320), (1100, 380), (900, 400), (560, 390), (470, 370), (0, 350)],
    'living-dining': [(0, 0), (1634, 0), (1634, 40), (1450, 290), (1430, 400), (1180, 415), (870, 405), (860, 420), (0, 470)],
    'bedroom-desk':  [(0, 0), (1753, 0), (1753, 70), (1180, 205), (600, 200), (150, 110), (0, 100)],
    'bed':           [(0, 0), (1733, 0), (1733, 60), (1640, 105), (1100, 250), (200, 235), (0, 200)],
    'bathroom':      [(0, 0), (1230, 0), (1230, 50), (800, 500), (200, 495), (190, 300), (0, 290)],
}
# how the colour is anchored per photo
MODE = {'kitchen': 'walls+ceiling', 'living-dining': 'walls+ceiling', 'bedroom-desk': 'walls+ceiling', 'bed': 'walls+ceiling',
        'bathroom': 'ceiling',          # sage-green walls: only the ceiling is a white reference
        'dining': 'walls', 'living-room': 'walls',   # no ceiling in frame
        'shower': 'white',              # white tiles
        'house': 'outdoor'}


def _sel_neutral(lab, extra):
    L = lab[..., 0] / 255; ch = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    return extra & (L > 0.5) & (L < 0.96) & (ch < 30)


def colour(img, name):
    mode = MODE[name]
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32); h, w = lab.shape[:2]
    ceil = np.zeros((h, w), np.uint8)
    if name in CEILING: cv2.fillPoly(ceil, [np.array(CEILING[name])], 255)
    band = np.zeros((h, w), bool); band[int(h * .2):int(h * .7)] = True
    if mode in ('walls', 'walls+ceiling'):
        s = _sel_neutral(lab, band & (ceil == 0))
        lab[..., 1] -= lab[..., 1][s].mean() - 128.5
        lab[..., 2] -= lab[..., 2][s].mean() - 128 - WALL_B
    elif mode == 'ceiling':
        s = _sel_neutral(lab, ceil > 0)
        lab[..., 1] -= lab[..., 1][s].mean() - 128
        lab[..., 2] -= lab[..., 2][s].mean() - 128 - CEIL_B
    elif mode == 'white':
        s = _sel_neutral(lab, np.ones((h, w), bool)) & (lab[..., 0] > 180)
        lab[..., 1] -= lab[..., 1][s].mean() - 128
        lab[..., 2] -= lab[..., 2][s].mean() - 128 - 1.0
    elif mode == 'outdoor':
        pass
    if mode == 'walls+ceiling':
        # local: pull the (lamp-warmed) ceiling to white, feathered, sparing coloured lamp glow
        s = _sel_neutral(lab, ceil > 0)
        da, db = lab[..., 1][s].mean() - 128, lab[..., 2][s].mean() - 128 - CEIL_B
        ch = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
        wgt = cv2.GaussianBlur(ceil.astype(np.float32) / 255, (0, 0), 12) * np.clip((40 - ch) / 15, 0, 1)
        lab[..., 1] -= wgt * da; lab[..., 2] -= wgt * db
    out = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    return light2(out, wb=0, warmth=0, outdoor=(mode == 'outdoor'))


def measure(img, name):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32); h, w = lab.shape[:2]
    ceil = np.zeros((h, w), np.uint8)
    if name in CEILING: cv2.fillPoly(ceil, [np.array(CEILING[name])], 255)
    band = np.zeros((h, w), bool); band[int(h * .2):int(h * .7)] = True
    sw = _sel_neutral(lab, band & (ceil == 0)); sc = _sel_neutral(lab, ceil > 0)
    f = lambda s: (round(float(lab[..., 1][s].mean() - 128), 1), round(float(lab[..., 2][s].mean() - 128), 1)) if s.sum() else None
    return {'walls a/b': f(sw), 'ceiling a/b': f(sc)}
