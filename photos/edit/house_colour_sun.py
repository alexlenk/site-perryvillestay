import cv2, numpy as np
sky=cv2.imread('out/house-old-bin0.png').astype(np.float32)/255          # bin, wires, glare already fixed; no other colour changes
orig=cv2.imread('/tmp/claude-0/airbnb/big_2560.jpg')
Y=(0.114*sky[...,0]+0.587*sky[...,1]+0.299*sky[...,2])
# brightness curve: lift shadows and mid-tones, leave highlights
base=cv2.GaussianBlur(Y,(0,0),30)
gain=1+0.55*np.clip(0.45-base,0,0.45)/0.45            # up to +55 % in dark areas (shaded lawn, porch)
Y2=np.clip(Y*gain,0,1)
Y2=Y2**0.93                                           # a little overall lift
k=0.9; over=Y2>k; Y2[over]=k+(1-k)*np.tanh((Y2[over]-k)/(1-k))
ratio=(Y2/np.maximum(Y,1e-3))[...,None]
out=np.clip(sky*ratio,0,1)                            # same RGB proportions -> colours keep their strength
# vibrance: more for muted colours, less for already strong ones
hsv=cv2.cvtColor((out*255).astype(np.uint8),cv2.COLOR_BGR2HSV).astype(np.float32); s=hsv[...,1]/255
hsv[...,1]=np.clip((s+0.22*s*(1-s))*255,0,255)
out=cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2BGR)
blur=cv2.GaussianBlur(out,(0,0),1.6); out=cv2.addWeighted(out,1.25,blur,-0.25,0)
cv2.imwrite('out/house-old-final.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,93])
prev=cv2.imread('out/house-old-final-nosun.jpg')
tiles=[cv2.resize(x,(800,600)) for x in (orig,prev,out)]
for im,l in zip(tiles,['Airbnb now','without sun','with sun']): cv2.putText(im,l,(12,36),0,1.1,(255,255,255),6); cv2.putText(im,l,(12,36),0,1.1,(30,30,30),2)
cv2.imwrite('house-sun-compare.jpg',np.hstack(tiles),[cv2.IMWRITE_JPEG_QUALITY,88])
regions={'sky top':(0,200,0,2560),'grass front':(1500,1900,1200,2400),'lawn right':(1180,1300,1900,2500),'house wall':(1050,1150,900,1300)}
for n,(y0,y1,x0,x1) in regions.items():
  r=[]
  for im in (orig,prev,out):
    h=cv2.cvtColor(im[y0:y1,x0:x1],cv2.COLOR_BGR2HSV).reshape(-1,3).mean(0); r.append(f'sat {h[1]:5.1f} val {h[2]:5.1f}')
  print(f'{n:12s} orig: {r[0]} | previous: {r[1]} | new: {r[2]}')
