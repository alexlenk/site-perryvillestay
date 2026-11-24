import cv2, numpy as np
from lama import inpaint
b=cv2.imread('out/house-old-bin0.png'); o=cv2.imread('/tmp/claude-0/airbnb/big_2560.jpg'); r=b.copy()
# 1) our house wall between the corner trim and the porch post: siding + gravel strip, cloned from right of the post (same height)
r[1032:1192,463:523]=o[1032:1192,588:648]
# 2) corner trim: continue the visible trim downwards
trim=o[990:1030,452:463]
for y in range(1030,1172): r[y,452:463]=trim[(y-1030)%40]
r[1172:1192,452:463]=o[1172:1192,577:588]
# 3) gap left of the corner: continue the neighbour's foundation and lawn from just left of it
r[1040:1205,402:452]=b[1040:1205,352:402]
# soften the seams
seam=np.zeros(b.shape[:2],np.uint8)
for x in (402,452,463): cv2.line(seam,(x,1035),(x,1205),255,5)
cv2.line(seam,(402,1192),(523,1192),255,7); cv2.line(seam,(402,1036),(523,1036),255,3)
fin=inpaint(r,seam,pad=80)
cv2.imwrite('out/house-old-bin4.png',fin)
x0,y0,x1,y1=300,900,720,1300
cv2.imwrite('hole2.jpg',cv2.resize(np.hstack([o[y0:y1,x0:x1],b[y0:y1,x0:x1],fin[y0:y1,x0:x1]]),None,fx=1.3,fy=1.3))
