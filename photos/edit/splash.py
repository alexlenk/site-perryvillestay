import cv2, numpy as np
def clean_splash(img, top_line, SATMAX=60, ref_off=(230,120), ramp=(160,60), found_line=None, ground_y=None, strength=0.95):
    """Remove the dirt splashed up from the ground onto the lowest siding boards (and the foundation):
    per column, bring the low-frequency colour of the dirty band to the colour of the clean siding above it.
    Fine detail (lap lines, texture) is kept. top_line(x) = y where the splash zone ends (siding bottom / foundation top)."""
    h,w=img.shape[:2]; f=img.astype(np.float32)
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    wall=((hsv[...,1]<SATMAX)&(hsv[...,2]>95)).astype(np.float32)
    wall=cv2.erode(wall,np.ones((5,5),np.uint8))
    den=np.maximum(cv2.GaussianBlur(wall,(0,0),6),1e-3)
    low=np.stack([cv2.GaussianBlur(f[...,c]*wall,(0,0),6)/den for c in range(3)],-1)
    out=f.copy()
    ys=np.arange(h)[:,None]
    for x in range(w):
        yl=top_line(x)
        if yl is None: continue
        r0,r1=int(yl-ref_off[0]),int(yl-ref_off[1])
        col=f[r0:r1,x][wall[r0:r1,x]>0]
        if len(col)<20: continue
        ref=np.median(col,0)
        y0=int(yl-ramp[0]); yb=int(ground_y(x)) if ground_y else h
        for y in range(max(y0,0),min(yb,h)):
            if wall[y,x]==0: continue
            wgt=min(1,(y-y0)/ramp[1])*strength
            g=ref/np.maximum(low[y,x],1)
            gp=(ref/np.maximum(f[y,x],1)).max()          # guard: wood/rails are far darker and more orange than dirty siding
            wgt*=float(np.clip((2.3-gp)/0.3,0,1))
            out[y,x]=f[y,x]*(1+(g-1)*wgt)
    return np.clip(out,0,255).astype(np.uint8)
