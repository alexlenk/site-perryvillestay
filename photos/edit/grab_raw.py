import sys, cv2, colour as C
_orig=C.colour
def wrapped(img,name):
    cv2.imwrite(f'out/{name}-raw.png',img); return _orig(img,name)
C.colour=wrapped
script,args=sys.argv[1],sys.argv[2:]
sys.argv=[script]+args
exec(open(script).read(),{'__name__':'__main__'})
