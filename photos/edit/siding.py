import cv2, numpy as np
def clean_siding(img, strength=0.6, sat_max=45, vmin=120):
    """Lighten dirt streaks/stains on white siding and foundation, remove their yellow-green tint.
    Keeps the horizontal lap lines: stains are found as areas darker than the wider wall, at a scale larger than the lap lines."""
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(np.float32); hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    white=((hsv[...,1]<sat_max)&(hsv[...,2]>vmin)).astype(np.uint8)*255
    white=cv2.morphologyEx(white,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lb,st,_=cv2.connectedComponentsWithStats(white); m=np.zeros_like(white)
    for i in range(1,n):
        if st[i,4]>20000: m[lb==i]=255                       # only large wall areas
    m=cv2.erode(m,np.ones((7,7),np.uint8))                    # stay off the edges of frames and posts
    mf=(m>0).astype(np.float32); den=lambda s: np.maximum(cv2.GaussianBlur(mf,(0,0),s),1e-3)
    L=lab[...,0]
    # smooth along the laps (horizontal) so lap shadows don't count as dirt
    Lh=cv2.blur(L*mf,(41,5))/np.maximum(cv2.blur(mf,(41,5)),1e-3)   # masked: dark frames/posts do not leak into the wall
    small=cv2.GaussianBlur(Lh*mf,(0,0),6)/den(6); big=cv2.GaussianBlur(Lh*mf,(0,0),60)/den(60)
    lift=np.clip(big-small,0,None)*strength
    lab[...,0]=np.clip(L+lift,0,255)
    for c in (1,2):   # pull stain tint towards the wall's own colour
        ref=cv2.GaussianBlur(lab[...,c]*mf,(0,0),60)/den(60); k=np.clip(lift/12,0,1)*0.8
        lab[...,c]=lab[...,c]*(1-k)+ref*k
    out=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR)
    a=cv2.GaussianBlur(mf,(0,0),2)[...,None]
    return (img*(1-a)+out*a).astype(np.uint8)
