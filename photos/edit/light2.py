import cv2, numpy as np


def stats(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0] / 255
    neutral = (L > np.percentile(L, 40)) & (L < 0.95)
    a, b = lab[..., 1][neutral].mean() - 128, lab[..., 2][neutral].mean() - 128
    return dict(median_L=round(float(np.median(L)), 3), p95=round(float(np.percentile(L, 95)), 3),
                cast_a=round(float(a), 1), cast_b=round(float(b), 1))


def light2(img, target=0.67, wb=0.85, warmth=3.0, shadows=0.45, vibrance=0.12, outdoor=False, ref='walls', ref_b=None):
    """Real-estate style: neutral white walls, brighter mid-tones, lifted shadows, protected highlights.
    wb      share of the colour cast on bright neutral surfaces that is removed
    warmth  b* added back afterwards (a little warmth looks inviting)
    target  median lightness after the tone curve"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0] / 255
    # 1) white balance from bright, low-chroma pixels (walls, ceiling)
    chroma = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    sel = (L > np.percentile(L, 40)) & (L < 0.97) & (chroma < 30)
    if ref == 'ceiling':   # the ceiling is white: neutralise it, the cream walls follow
        top = np.zeros_like(sel); top[:int(L.shape[0] * 0.22)] = True
        sel = top & (L > 0.55) & (L < 0.97) & (chroma < 25)
        warmth = 1.0 if ref_b is None else ref_b
        wb = 1.0
    elif ref == 'cream':   # no ceiling in frame: bring the walls to the cream measured in the other photos
        warmth = ref_b; wb = 1.0
    if outdoor:   # sky and siding are not a white reference outdoors
        wb = 0.3
    if sel.sum() > 500:
        lab[..., 1] -= wb * (lab[..., 1][sel].mean() - 128)
        lab[..., 2] -= wb * (lab[..., 2][sel].mean() - 128 - warmth)
    # 2) mid-tone brightness: gamma so the median reaches the target (never darker, at most gamma 0.6)
    med = float(np.median(L))
    g = np.clip(np.log(target) / np.log(max(med, 1e-3)), 0.6, 1.0)
    L2 = L ** g
    # 3) local shadow lift: brighten where the neighbourhood is dark
    base = cv2.GaussianBlur(L2, (0, 0), 25)
    L2 = L2 + shadows * (1 - L2) * np.clip(0.55 - base, 0, 0.55) / 0.55 * L2 ** 0.5
    # 4) highlight shoulder so windows and lamps do not clip harder
    k = 0.92
    over = L2 > k
    L2[over] = k + (1 - k) * np.tanh((L2[over] - k) / (1 - k))
    lab[..., 0] = np.clip(L2 * 255, 0, 255)
    out = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    # 5) vibrance: boost low-saturation colours more than saturated ones
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    s = hsv[..., 1] / 255
    hsv[..., 1] = np.clip((s + vibrance * s * (1 - s)) * 255, 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    # 6) mild sharpening
    blur = cv2.GaussianBlur(out, (0, 0), 1.6)
    return cv2.addWeighted(out, 1.3, blur, -0.3, 0)
