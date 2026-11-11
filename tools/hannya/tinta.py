import cv2, numpy as np
im=cv2.imread('src.png'); HSV=np.load('hsv.npy'); H,S,V=HSV[...,0],HSV[...,1],HSV[...,2]
sil=np.load('sil.npy').astype(bool); horns=np.load('horns.npy'); face=np.load('face.npy')
f=im.astype(np.float32)/255; b,g,r=f[...,0],f[...,1],f[...,2]
lum=.299*r+.587*g+.114*b
k=lambda n: cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
# encolhe 1 px a silhueta e suaviza a borda
silm=cv2.erode(sil.astype(np.uint8),k(3)).astype(bool)
# 1) tinta cheia: preto da pintura
ink=lum<.30
# 2) vermelho forte da boca vira tinta (dentes ficam papel)
s=1/.35
boca=np.zeros_like(sil); boca[int(515*s):int(690*s),int(130*s):int(430*s)]=True
ink|=boca&((H<9)|(H>165))&(S>.55)
# 3) pontilhismo: sombra do rosto e dos chifres
yy,xx=np.mgrid[0:im.shape[0],0:im.shape[1]].astype(np.float32)
P=22.0; a=np.deg2rad(45)
u=(xx*np.cos(a)+yy*np.sin(a))*2*np.pi/P; v=(-xx*np.sin(a)+yy*np.cos(a))*2*np.pi/P
tela=.5+.25*(np.cos(u)+np.cos(v))  # 0..1
dface=np.clip((.53-lum)/.16,0,1)**1.3*.6
dhorn=np.clip((.58-lum)/.34,0,1)**1.2*.85
d=np.where(horns,dhorn,np.where(face,dface,0))
dots=(d>tela)&(face|horns)&~ink
out=(ink|dots)&silm
# contorno da máscara inteira
borda=cv2.morphologyEx(silm.astype(np.uint8),cv2.MORPH_GRADIENT,k(9)).astype(bool)&silm
out|=borda
# limpa poeira
out=cv2.morphologyEx(out.astype(np.uint8),cv2.MORPH_OPEN,k(3))
n,lab,st,_=cv2.connectedComponentsWithStats(out)
small=np.isin(lab,np.where(st[:,cv2.CC_STAT_AREA]<10)[0]); out[small]=0
ys,xs=np.where(out); pad=12
out=out[ys.min()-pad:ys.max()+pad, xs.min()-pad:xs.max()+pad]
np.save('out.npy',out)
cv2.imwrite('out.png',(1-out)*255)
print(out.shape)
pv=np.full(out.shape+(3,),(217,231,239),np.uint8); pv[out>0]=(17,19,21)
cv2.imwrite('prev.jpg',cv2.resize(pv,None,fx=.42,fy=.42,interpolation=cv2.INTER_AREA))
