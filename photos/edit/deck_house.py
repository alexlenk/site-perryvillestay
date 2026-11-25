import cv2, numpy as np
from splash import clean_splash
from siding import clean_siding
im=cv2.imread('new/deck2_final.jpg'); h,w=im.shape[:2]
hsv0=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
# protected: everything left of the post (stairs and rails), the front rail crossing the wall, and strongly coloured wood (posts)
prot=np.zeros((h,w),np.uint8)
prot[:, :1175]=255
cv2.fillPoly(prot,[np.array([(790,1300),(935,1300),(1290,1932),(1068,1932)])],255)
strong=((hsv0[...,0]>=3)&(hsv0[...,0]<=26)&(hsv0[...,1]>115)).astype(np.uint8)*255
strong=cv2.morphologyEx(strong,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
n,lb,st,_=cv2.connectedComponentsWithStats(strong)
for i in range(1,n):
    if st[i,4]>8000: prot[lb==i]=255
prot=cv2.dilate(prot,np.ones((7,7),np.uint8))
a=cv2.GaussianBlur(prot.astype(np.float32)/255,(0,0),1.5)[...,None]
pts=np.array([(400,1885),(1100,1862),(1395,1818),(1405,1708),(1600,1680),(1800,1640),(1900,1620),(1990,1585),(2015,1560)],float)
line=lambda x: float(np.interp(x,pts[:,0],pts[:,1])) if 400<=x<=2015 else None
s1=clean_splash(im,line,SATMAX=120,ref_off=(250,150),ramp=(180,70),ground_y=lambda x: line(x)+4)
f=s1.astype(np.float32); hsv=cv2.cvtColor(s1,cv2.COLOR_BGR2HSV)
fm=np.zeros((h,w),np.uint8)
cv2.fillPoly(fm,[np.array([(1405,1712),(1600,1684),(1800,1644),(1900,1624),(1990,1590),(1990,1640),(1800,1700),(1600,1760),(1405,1810)])],255)
fm[(hsv[...,0]>30)&(hsv[...,1]>60)]=0; fm[prot>0]=0
fmf=(fm>0).astype(np.float32); S=20; den=np.maximum(cv2.GaussianBlur(fmf,(0,0),S),1e-3)
low=np.stack([cv2.GaussianBlur(f[...,c]*fmf,(0,0),S)/den for c in range(3)],-1)
g=np.array([150.,170.,176.])/np.maximum(low,1); out=f*(1+(g-1)*0.75*fmf[...,None])
b=cv2.GaussianBlur(fmf,(0,0),2)[...,None]
s2=np.clip(f*(1-b)+out*b,0,255).astype(np.uint8)
s3=clean_siding(s2,strength=0.8)
s3=(s3*(1-a)+clean_siding(im,strength=0.8)*a).astype(np.uint8)   # protected area: only the gentle stain lift (wall above), wood untouched by it
cv2.imwrite('new/deck4.jpg',s3,[cv2.IMWRITE_JPEG_QUALITY,93])
def lab(x,l):
    cv2.putText(x,l,(10,34),0,1,(255,255,255),5); cv2.putText(x,l,(10,34),0,1,(20,20,20),2); return x
z=lambda x: x[1450:1900,850:2050].copy()
top=np.vstack([lab(z(im),'before'),lab(z(s3),'after')])
cv2.imwrite('new/splash_ab.jpg',cv2.resize(top,None,fx=0.8,fy=0.8))
full=cv2.resize(s3,(top.shape[1],int(s3.shape[0]*top.shape[1]/s3.shape[1])))
cv2.imwrite('approval-deck3.jpg',np.vstack([top,np.full((8,top.shape[1],3),255,np.uint8),full]),[cv2.IMWRITE_JPEG_QUALITY,86])
