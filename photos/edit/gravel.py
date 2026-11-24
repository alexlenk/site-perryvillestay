import cv2, numpy as np
def clean_gravel(img, poly, s_small=12, s_large=70, strength=1.0):
    """Even out dark dirt patches and tyre ruts in gravel: lift spots that are darker than their wider
    surroundings (mid-scale), keep the large sun/shade pattern and the stone texture."""
    h,w=img.shape[:2]
    m=np.zeros((h,w),np.uint8); cv2.fillPoly(m,[np.array(poly)],255); mf=(m>0).astype(np.float32)
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(np.float32); L=lab[...,0]
    den=lambda s: np.maximum(cv2.GaussianBlur(mf,(0,0),s),1e-3)
    bs=cv2.GaussianBlur(L*mf,(0,0),s_small)/den(s_small); bl=cv2.GaussianBlur(L*mf,(0,0),s_large)/den(s_large)
    lift=np.clip(bl-bs,0,None)*strength                    # only brighten dark patches
    lab[...,0]=np.clip(L+lift*(L/np.maximum(bs,1)),0,255)
    # remove the brownish dirt tint: pull chroma of the patches towards the gravel's average
    for c in (1,2):
        avg=cv2.GaussianBlur(lab[...,c]*mf,(0,0),s_large)/den(s_large)
        k=np.clip(lift/20,0,1)
        lab[...,c]=lab[...,c]*(1-k)+avg*k
    out=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR)
    a=cv2.GaussianBlur(mf,(0,0),4)[...,None]
    return (img*(1-a)+out*a).astype(np.uint8)
