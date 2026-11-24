import cv2, numpy as np
from lama import inpaint
def lawn_strip(width, height, v0=840, v1=1500, x0=570, x1=1200, ov=60):
    S=cv2.imread('new/june_noshadow.png')[v0:v1,x0:x1].astype(np.float32)   # real June 2026 lawn
    tiles=[]; w=0
    while w < width*1.05+ov:
        tiles.append(S); w+=S.shape[1]-ov                                     # no mirroring: mowing stripes stay parallel
    out=tiles[0]; seams=[]
    for t in tiles[1:]:
        a=np.linspace(0,1,ov)[None,:,None]
        seams.append(out.shape[1]-ov/2)
        out=np.concatenate([out[:,:-ov],out[:,-ov:]*(1-a)+t[:,:ov]*a,t[:,ov:]],1)
    sc=width/out.shape[1]
    return cv2.resize(out,(width,height),interpolation=cv2.INTER_CUBIC),[s*sc for s in seams]
def replace(img, polys, ytop, ybot, power=1.0, sigma=40, chroma=0.8, feather=5, band=50):
    h,w=img.shape[:2]
    strip,seams=lawn_strip(w, ybot-ytop)
    new=img.astype(np.float32).copy(); new[ytop:ybot]=strip
    m=np.zeros((h,w),np.uint8)
    for p in polys: cv2.fillPoly(m,[np.array(p,np.int32)],255)
    mf=(m>0).astype(np.float32)
    Lo=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(np.float32); Lt=cv2.cvtColor(np.clip(new,0,255).astype(np.uint8),cv2.COLOR_BGR2LAB).astype(np.float32)
    den=np.maximum(cv2.GaussianBlur(mf,(0,0),sigma),1e-3)
    lowO=cv2.GaussianBlur(Lo[...,0]*mf,(0,0),sigma)/den; lowT=cv2.GaussianBlur(Lt[...,0]*mf,(0,0),sigma)/den
    o=Lt.copy(); o[...,0]=np.clip(Lt[...,0]*(np.maximum(lowO,1)/np.maximum(lowT,1))**power,0,255)
    o[...,1:]=128+(Lt[...,1:]-128)*chroma
    res=cv2.cvtColor(np.clip(o,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR)
    a=cv2.GaussianBlur(mf,(0,0),feather)[...,None]
    out=(img*(1-a)+res*a).astype(np.uint8)
    # AI smoothing: LaMa repaints a narrow band over each tile seam inside the lawn (and the lawn edge)
    sm=np.zeros((h,w),np.uint8)
    for s in seams:
        if 0<s<w: cv2.rectangle(sm,(int(s-band/2),ytop),(int(s+band/2),ybot),255,-1)
    sm=cv2.bitwise_and(sm,cv2.erode(m,np.ones((15,15),np.uint8)))
    return inpaint(out,sm,pad=220), seams
