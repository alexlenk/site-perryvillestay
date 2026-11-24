import cv2, numpy as np
from lama import inpaint
img = cv2.imread('/root/.claude/uploads/7abb9dae-ca94-57ca-8def-12ed6a733fcc/11b621e1-image.jpg'); h, w = img.shape[:2]
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 1) care tag (worked well)
tag = np.zeros((h, w), np.uint8)
cv2.fillPoly(tag, [np.array([(1240, 1107), (1257, 1115), (1255, 1200), (1232, 1201), (1215, 1190), (1200, 1160), (1202, 1135)])], 255)
tag = cv2.dilate(tag, np.ones((9, 9), np.uint8))

# 2) printer: bigger polygon incl. contact shadow
pr = np.zeros((h, w), np.uint8)
cv2.fillPoly(pr, [np.array([(1612, 1068), (1672, 1008), (1822, 1068), (1832, 1130), (1812, 1200), (1770, 1204), (1612, 1150)])], 255)
pr = cv2.dilate(pr, np.ones((15, 15), np.uint8))

# 3) cables traced by hand on a 5x zoom
cab = np.zeros((h, w), np.uint8)
for pts in [[(816,801),(824,808),(831,818),(833,830),(830,842),(822,850),(812,855),(802,858),(794,860)],   # white cable
            [(818,810),(816,820),(814,832),(810,844),(809,856),(808,868),(806,879)],                           # black cable
            [(793,860),(798,870),(804,878)],                                                                   # short cable
            [(783,882),(784,892),(786,904),(788,920),(790,934),(789,950),(786,962)],                           # loop, right strand
            [(761,924),(760,940),(760,950),(762,960),(766,964)]]:                                              # loop, left strand
    cv2.polylines(cab, [np.array(pts)], False, 255, 4)
cv2.rectangle(cab, (798, 870), (810, 882), 255, -1)                                                            # plug
cab = cv2.dilate(cab, np.ones((5, 5), np.uint8))

mask = np.maximum(np.maximum(tag, pr), cab)
cv2.imwrite('bed_mask.png', mask)
out = inpaint(img, mask, pad=220)
cv2.imwrite('bed_clean.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 95])


def z(im, a, b, c, d):
    return cv2.resize(im[b:d, a:c], None, fx=2, fy=2)


def ov(im):
    o = im.copy(); cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); cv2.drawContours(o, cs, -1, (0, 0, 255), 1); return o


cv2.imwrite('cmp_printer.jpg', np.hstack([z(ov(img), 1560, 980, 1860, 1230), z(out, 1560, 980, 1860, 1230)]))
cv2.imwrite('cmp_cable.jpg', np.hstack([z(ov(img), 700, 780, 880, 1000), z(out, 700, 780, 880, 1000)]))
