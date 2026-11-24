import cv2, numpy as np
from lama import inpaint

img = cv2.imread('/tmp/claude-0/airbnb/big_2560.jpg'); h, w = img.shape[:2]   # Airbnb cover photo, 2560 x 1920
m = np.zeros((h, w), np.uint8)
cv2.fillPoly(m, [np.array([(333, 1058), (390, 1040), (523, 1040), (523, 1215), (470, 1234), (372, 1230), (358, 1150), (336, 1075)])], 255)  # trash bin
cv2.rectangle(m, (194, 1084), (302, 1160), 255, -1)                                    # neighbour's AC unit
band = np.zeros((h, w), np.uint8); cv2.line(band, (0, 428), (505, 693), 255, 70)    # power line(s): thin dark lines near the traced wire
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
m[(band > 0) & (bh > 12)] = 255
cv2.line(m, (0, 428), (505, 693), 255, 9)
m = cv2.dilate(m, np.ones((7, 7), np.uint8))
cv2.imwrite('out/house-old-mask.png', m)
clean = inpaint(img, m, pad=320)
cv2.imwrite('out/house-old-clean.png', clean)

c = img.copy(); cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); cv2.drawContours(c, cs, -1, (0, 0, 255), 3)
box = (0, 380, 760, 1300)
x0, y0, x1, y1 = box
cv2.imwrite('out/house-old-zoom.jpg', cv2.resize(np.hstack([c[y0:y1, x0:x1], clean[y0:y1, x0:x1]]), None, fx=0.8, fy=0.8))
