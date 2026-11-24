import cv2, numpy as np
def rotH(w,h,f,pitch,roll):
    K=np.array([[f,0,w/2],[0,f,h/2],[0,0,1]])
    p,r=np.radians(pitch),np.radians(roll)
    Rx=np.array([[1,0,0],[0,np.cos(p),-np.sin(p)],[0,np.sin(p),np.cos(p)]])
    Rz=np.array([[np.cos(r),-np.sin(r),0],[np.sin(r),np.cos(r),0],[0,0,1]])
    return K@Rz@Rx@np.linalg.inv(K)
def lean(H,seg):
    p=cv2.perspectiveTransform(np.array([seg],np.float64),H)[0]; (x1,y1),(x2,y2)=p
    return np.degrees(np.arctan2(x2-x1,y2-y1))
def fit(w,h,f,segs):
    best=None
    for pitch in np.arange(-20,20.01,0.25):
        for roll in np.arange(-4,4.01,0.25):
            H=rotH(w,h,f,pitch,roll); e=sum(lean(H,s)**2 for s in segs)
            if best is None or e<best[0]: best=(e,pitch,roll)
    return best
def inner_crop(H,w,h,aspect):
    # map source border, find largest centred rect of given aspect inside the warped quad
    m=np.zeros((h,w),np.uint8)
    warped=cv2.warpPerspective(np.full((h,w),255,np.uint8),H,(w,h))
    for s in np.arange(1.0,0.3,-0.01):
        cw,ch=int(w*s),int(w*s/aspect)
        if ch>h: continue
        for cy in range(h//2-ch//2-60,h//2-ch//2+61,10):
            x0,y0=(w-cw)//2,cy
            if y0<0 or y0+ch>h: continue
            if warped[y0:y0+ch,x0:x0+cw].min()==255: return x0,y0,cw,ch
def light(img, lift=0.18, warm=-3, gamma=0.92):
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(np.float32)
    L=lab[...,0]/255
    L=L**gamma
    L=L+lift*(1-L)*np.exp(-((L-0.25)/0.22)**2)*0.5   # shadow lift
    lab[...,0]=np.clip(L*255,0,255)
    lab[...,2]=lab[...,2]+warm                          # less yellow
    out=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR)
    blur=cv2.GaussianBlur(out,(0,0),2); return cv2.addWeighted(out,1.35,blur,-0.35,0)  # mild sharpening
