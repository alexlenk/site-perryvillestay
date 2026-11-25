import cv2, numpy as np, sys
def blue_sky(img, gain=2.3, darken=12):
    """Make a pale sky bluer: scale its blue chroma (clouds stay white because their chroma is ~0),
    slight darkening towards the top for depth. Sky = bright pixels with a blue cast, connected to the top edge."""
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(np.float32); L=lab[...,0]; b=lab[...,2]-128; a=lab[...,1]-128
    h,w=L.shape
    cand=((b<-7)&(L>165)).astype(np.uint8)*255
    cand=cv2.morphologyEx(cand,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lb,st,_=cv2.connectedComponentsWithStats(cand); m=np.zeros_like(cand)
    for i in range(1,n):
        if st[i,1]<5 and st[i,4]>5000: m[lb==i]=255           # connected to the top edge
    # include cloud pixels enclosed by sky (bright, low chroma) so they get the depth gradient too
    hole=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((25,25),np.uint8)); m=cv2.bitwise_or(m,cv2.bitwise_and(hole,((L>190)&(np.abs(b)<8)).astype(np.uint8)*255))
    wgt=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),1.2)
    ys=np.where(m.any(1))[0]; ybot=ys.max() if len(ys) else h
    t=np.clip(1-np.arange(h)/max(ybot,1),0,1)[:,None]          # 1 at the top, 0 at the lowest sky pixel
    nb=b*(1+(gain-1)*wgt); na=a*(1+0.3*(gain-1)*wgt)
    nL=L-darken*t*wgt
    lab[...,0]=nL; lab[...,1]=na+128; lab[...,2]=nb+128
    return cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR), m
if __name__=='__main__':
    im=cv2.imread(sys.argv[1]); out,m=blue_sky(im); cv2.imwrite(sys.argv[2],out,[cv2.IMWRITE_JPEG_QUALITY,93]); cv2.imwrite(sys.argv[2]+'.mask.png',m)
