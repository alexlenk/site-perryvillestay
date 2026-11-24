import cv2, sys
def gc(path,x0,y0,x1,y1,s,step,out):
    im=cv2.imread(path); c=cv2.resize(im[y0:y1,x0:x1],None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
    for x in range((x0//step+1)*step,x1,step):
        X=int((x-x0)*s); big=x%(step*5)==0; cv2.line(c,(X,0),(X,c.shape[0]),(0,0,255) if big else (0,200,0),1)
        if big: cv2.putText(c,str(x),(X+2,14),0,0.45,(0,0,255),1)
    for y in range((y0//step+1)*step,y1,step):
        Y=int((y-y0)*s); big=y%(step*5)==0; cv2.line(c,(0,Y),(c.shape[1],Y),(255,0,0) if big else (0,200,0),1)
        if big: cv2.putText(c,str(y),(2,Y-2),0,0.45,(255,0,0),1)
    cv2.imwrite(out,c)
if __name__=='__main__':
    a=sys.argv; gc(a[1],*map(int,a[2:6]),float(a[6]),int(a[7]),a[8])
