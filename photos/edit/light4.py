import cv2, numpy as np
def light4(img, target=0.64, shadows=0.5, knee=0.78, vibrance=0.18, **_):
    """Brightening that keeps colour strength: scale R,G,B by the same factor (no washed-out colours),
    lift shadows locally, and compress highlights early so windows keep detail."""
    f=img.astype(np.float32)/255
    Y=0.114*f[...,0]+0.587*f[...,1]+0.299*f[...,2]
    med=float(np.median(Y)); g=np.clip(np.log(target)/np.log(max(med,1e-3)),0.65,1.0)
    Y2=Y**g
    base=cv2.GaussianBlur(Y2,(0,0),25)
    Y2=Y2+shadows*(1-Y2)*np.clip(0.5-base,0,0.5)/0.5*np.sqrt(Y2)
    over=Y2>knee; Y2[over]=knee+(1-knee)*np.tanh((Y2[over]-knee)/(1-knee))       # soft roll-off: windows keep texture
    # local highlight recovery: where the neighbourhood is very bright (windows), bring some local contrast back
    bb=cv2.GaussianBlur(Y2,(0,0),8); w=np.clip((bb-0.82)/0.1,0,1)
    Y2=Y2+w*0.6*(Y2-bb)-w*0.05
    Yn=np.clip(Y2,0,1)[...,None]
    ratio=(Yn[...,0]/np.maximum(Y,1e-3))[...,None]
    # colour (chroma) scales with the brightening, but capped so dark shadows do not turn into neon colour noise
    chroma=cv2.GaussianBlur(f-Y[...,None],(0,0),1.2)
    out=Yn+chroma*np.minimum(ratio,1.35)
    # if a channel would clip, shrink towards luminance instead of clipping (keeps hue)
    mx=out.max(2,keepdims=True)
    k=np.where(mx>1,(1-Yn)/np.maximum(mx-Yn,1e-4),1.0); out=Yn+(out-Yn)*k
    out=(np.clip(out,0,1)*255).astype(np.uint8)
    hsv=cv2.cvtColor(out,cv2.COLOR_BGR2HSV).astype(np.float32); s=hsv[...,1]/255
    hsv[...,1]=np.clip((s+vibrance*s*(1-s))*255,0,255)
    out=cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2BGR)
    blur=cv2.GaussianBlur(out,(0,0),1.6); return cv2.addWeighted(out,1.25,blur,-0.25,0)
