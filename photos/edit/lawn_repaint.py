import cv2, numpy as np, torch
from lama import model
def checker(shape,lawn,off,s=64,shift=0):
    h,w=shape[:2]; m=np.zeros((h,w),np.uint8)
    for y in range(-shift,h,s):
        for x in range(-shift,w,s):
            if (((x+shift)//s)+((y+shift)//s))%2==off: m[max(y,0):y+s,max(x,0):x+s]=255
    return cv2.bitwise_and(m,lawn)
def run(im,m,win=640):
    out=im.copy(); h,w=m.shape
    for x0 in range(0,w,win):
        sub=np.zeros_like(m); sub[:,x0:x0+win]=m[:,x0:x0+win]
        if not sub.any(): continue
        ys,_=np.where(sub>0)
        X0,X1=max(x0-160,0),min(x0+win+160,w); Y0,Y1=max(ys.min()-160,0),min(ys.max()+160,h)
        S=out[Y0:Y1,X0:X1]; M=(sub[Y0:Y1,X0:X1]>0).astype(np.float32)
        H,W=S.shape[:2]; PH,PW=(8-H%8)%8,(8-W%8)%8
        t=np.pad(cv2.cvtColor(S,cv2.COLOR_BGR2RGB),((0,PH),(0,PW),(0,0)),mode='reflect'); mm=np.pad(M,((0,PH),(0,PW)),mode='reflect')
        with torch.inference_mode(): r=model()(torch.from_numpy(t).permute(2,0,1)[None].float()/255,torch.from_numpy(mm)[None,None])[0].permute(1,2,0).numpy()
        r=cv2.cvtColor(np.clip(r*255,0,255).astype(np.uint8)[:H,:W],cv2.COLOR_RGB2BGR)
        out[Y0:Y1,X0:X1][M>0]=r[M>0]
    return out
def repaint(img,polys,erode=9):
    lawn=np.zeros(img.shape[:2],np.uint8)
    for p in polys: cv2.fillPoly(lawn,[np.array(p)],255)
    lawn=cv2.erode(lawn,np.ones((erode,erode),np.uint8))
    return run(run(img,checker(img.shape,lawn,0)),checker(img.shape,lawn,1))
