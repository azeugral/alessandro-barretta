import cv2, numpy as np, json
im=cv2.imread('src.png'); HSV=np.load('hsv.npy'); H,S,V=HSV[...,0],HSV[...,1],HSV[...,2]
f=im.astype(np.float32)/255; b,g,r=f[...,0],f[...,1],f[...,2]
k=lambda n: cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
grey=((b-r)>.05)&(V>.3)&(S<.4)
white=(V>.6)&(S<.25)
cor=(S>.35)&(V>.3)
bar=cv2.dilate((white|grey).astype(np.uint8),k(5))|cv2.dilate(cor.astype(np.uint8),k(17))
for (x1,y1,x2,y2) in json.load(open('barreiras.json')): cv2.line(bar,(x1,y1),(x2,y2),1,9)
n,lab,st,_=cv2.connectedComponentsWithStats((1-bar).astype(np.uint8),connectivity=4)
s=1/.35
pick=lambda x,y: lab==lab[int(y*s),int(x*s)]
lobos=pick(370,185)|pick(480,240)|pick(540,380)
lobos=cv2.dilate(lobos.astype(np.uint8),k(9)).astype(bool)
# rosto
nf,lf,sf,_=cv2.connectedComponentsWithStats(cv2.morphologyEx(grey.astype(np.uint8),cv2.MORPH_CLOSE,k(9)))
face=lf==(1+np.argmax(sf[1:,cv2.CC_STAT_AREA]))
# chifres
nc,lc,_,_=cv2.connectedComponentsWithStats(cor.astype(np.uint8))
horns=np.zeros_like(face)
for (x,y) in [(290,130),(560,200)]:
    horns|=lc==lc[int(y*s),int(x*s)]
marrom=(((H<28)|(H>170))&(S>.22)&(V>.08)|((S>.08)&(V>.14)&((b-r)<.0)))&~((S>.5)&(V>.5)&((H<8)|(H>168)))
for _ in range(60):
    nh=horns|(cv2.dilate(horns.astype(np.uint8),k(5)).astype(bool)&marrom)
    if (nh==horns).all(): break
    horns=nh
horns=cv2.morphologyEx(horns.astype(np.uint8),cv2.MORPH_CLOSE,k(15)).astype(bool)
# contorno branco que abraça os lóbulos
wl=white&cv2.dilate(lobos.astype(np.uint8),k(31)).astype(bool)
u=(face|lobos|horns|wl).astype(np.uint8)
for (x0,y0,x1,y1) in [(205,315,305,410),(130,515,430,690)]:
    X0,Y0,X1,Y1=[int(v*s) for v in (x0,y0,x1,y1)]
    w=np.zeros_like(u); w[Y0:Y1,X0:X1]=face[Y0:Y1,X0:X1]
    pts=cv2.findNonZero(w)
    if pts is not None: cv2.fillConvexPoly(u,cv2.convexHull(pts),1)
u=cv2.morphologyEx(u,cv2.MORPH_CLOSE,k(21))
# fecha buracos (olhos, boca, narinas)
cs,_=cv2.findContours(u,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
sil=np.zeros_like(u)
for c in cs:
    if cv2.contourArea(c)>3000: cv2.drawContours(sil,[c],-1,1,-1)
np.save('sil.npy',sil); np.save('horns.npy',horns); np.save('face.npy',face)
v=im.copy(); v[sil==0]=(v[sil==0]*.25).astype(np.uint8)
cv2.imwrite('sil.jpg',cv2.resize(v,None,fx=.35,fy=.35))
