import cv2, numpy as np, torch
torch.set_num_threads(4)
_model = None


def model():
    global _model
    if _model is None:
        _model = torch.jit.load('/tmp/claude-0/models/big-lama.pt', map_location='cpu').eval()
    return _model


def inpaint(img, mask, pad=160):
    """img BGR uint8, mask uint8 (255 = remove). Inpaints each blob in a window around it."""
    out = img.copy(); h, w = mask.shape
    n, lab, stats, _ = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8))
    for i in range(1, n):
        x, y, bw, bh, _ = stats[i]
        x0, y0 = max(x - pad, 0), max(y - pad, 0); x1, y1 = min(x + bw + pad, w), min(y + bh + pad, h)
        sub = out[y0:y1, x0:x1].copy(); m = (lab[y0:y1, x0:x1] == i).astype(np.float32)
        H, W = sub.shape[:2]; PH, PW = (8 - H % 8) % 8, (8 - W % 8) % 8
        im = np.pad(cv2.cvtColor(sub, cv2.COLOR_BGR2RGB), ((0, PH), (0, PW), (0, 0)), mode='reflect')
        mm = np.pad(m, ((0, PH), (0, PW)), mode='reflect')
        ti = torch.from_numpy(im).permute(2, 0, 1)[None].float() / 255; tm = torch.from_numpy(mm)[None, None]
        with torch.inference_mode():
            r = model()(ti, tm)[0].permute(1, 2, 0).numpy()
        r = cv2.cvtColor(np.clip(r * 255, 0, 255).astype(np.uint8)[:H, :W], cv2.COLOR_RGB2BGR)
        a = cv2.GaussianBlur(cv2.dilate(m, np.ones((5, 5))), (9, 9), 0)[..., None]
        out[y0:y1, x0:x1] = (r * a + sub * (1 - a)).astype(np.uint8)
    return out
