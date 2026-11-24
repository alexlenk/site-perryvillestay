import cv2, numpy as np, torch
from lama import model
def lama_full(img, m):
    H,W=img.shape[:2]; PH,PW=(8-H%8)%8,(8-W%8)%8
    im=np.pad(cv2.cvtColor(img,cv2.COLOR_BGR2RGB),((0,PH),(0,PW),(0,0)),mode='reflect'); mm=np.pad((m>0).astype(np.float32),((0,PH),(0,PW)),mode='reflect')
    with torch.inference_mode(): r=model()(torch.from_numpy(im).permute(2,0,1)[None].float()/255,torch.from_numpy(mm)[None,None])[0].permute(1,2,0).numpy()
    return cv2.cvtColor(np.clip(r*255,0,255).astype(np.uint8)[:H,:W],cv2.COLOR_RGB2BGR)
def inpaint_lowres(img, m, sc=0.5, seed=1):
    """Inpaint the whole image at reduced resolution (better global structure for big masks), add matching grain."""
    small=cv2.resize(img,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA); ms=cv2.resize(m,(small.shape[1],small.shape[0]),interpolation=cv2.INTER_NEAREST)
    r=cv2.resize(lama_full(small,ms),(img.shape[1],img.shape[0]),interpolation=cv2.INTER_CUBIC)
    noise=(img.astype(np.float32)-cv2.GaussianBlur(img,(0,0),1.5).astype(np.float32)).std()
    r=np.clip(r.astype(np.float32)+np.random.default_rng(seed).normal(0,noise,r.shape),0,255).astype(np.uint8)
    a=cv2.GaussianBlur(cv2.dilate(m,np.ones((5,5))).astype(np.float32)/255,(9,9),0)[...,None]
    return (img*(1-a)+r*a).astype(np.uint8)
