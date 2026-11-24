import cv2, numpy as np, sys
exec(open('new_photos.py').read().split("checks={}")[0])
checks={}
def poly(shape, ps, dil=7):
    m=np.zeros(shape[:2],np.uint8)
    for p in ps: cv2.fillPoly(m,[np.array(p)],255)
    return cv2.dilate(m,np.ones((dil,dil),np.uint8))
which=sys.argv[1:]
def want(k): return not which or k in which

if want('coffee'):
    im=cv2.imread(U+'d0aaa402-image.jpg'); save('coffee-station',keep_sat_light(im))
if want('bed'):
    im=cv2.imread(U+'6cd4b6c5-image.jpg'); C.MODE['bed-closeup']='walls'; up,info=auto_upright(im,760); print('bed',info); save('bed-closeup',C.colour(up,'bed-closeup'))
if want('dishes'):
    save('dishes',keep_sat_light(cv2.imread(U+'5cb65d03-image.jpg')))
if want('bowls'):
    save('bowls-containers',keep_sat_light(cv2.imread(U+'b1b1d2de-image.jpg')))
if want('bath'):
    im=cv2.imread(U+'9c588e03-image.jpg')
    m=poly(im.shape,[[(850,1150),(890,1082),(915,1076),(1162,1116),(1195,1133),(1184,1230),(1140,1234),(1000,1204),(858,1180)],
        [(286,486),(328,486),(328,614),(286,614)],[(1426,516),(1462,516),(1462,644),(1426,644)],
        [(1172,1940),(1208,1904),(1442,1900),(1470,1928),(1512,1960),(1512,2016),(1176,2016)]],dil=9)
    c=inpaint(im,m,pad=260); checks['bath']=(im,c,(800,1020,1260,1280)); checks['bath2']=(im,c,(250,450,360,650))
    C.MODE['bathroom-towels']='white'; up,info=auto_upright(c,1100); print('bath',info); save('bathroom-towels',C.colour(up,'bathroom-towels'))
if want('lawn'):
    im=cv2.imread(U+'e6cb93fa-image.jpg')
    m=poly(im.shape,[[(150,372),(345,372),(352,552),(150,552)],[(783,256),(838,256),(838,282),(783,282)]],dil=7)
    c=inpaint(im,m,pad=260); checks['lawn']=(im,c,(60,300,420,620)); checks['lawn2']=(im,c,(740,220,880,320))
    up,info=auto_upright(c,1100); print('lawn',info); save('porch-lawn',keep_sat_light(up))
for k,(a,b,(x0,y0,x1,y1)) in checks.items():
    p=np.hstack([a[y0:y1,x0:x1],b[y0:y1,x0:x1]]); s=min(2.5,1100/p.shape[1]); cv2.imwrite(f'new/chk_{k}.jpg',cv2.resize(p,None,fx=s,fy=s))
