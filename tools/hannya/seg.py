import cv2, numpy as np, sys
SRC=r"C:/Users/dslru/Documents/PROJETOS LRGZ/Alessandro Barretta/_ref/ig/061.1.jpg"
im=cv2.imread(SRC)[300:1650,150:1200]  # crop
im=cv2.resize(im,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
im=cv2.bilateralFilter(im,9,40,7)
f=im.astype(np.float32)/255; b,g,r=f[...,0],f[...,1],f[...,2]
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(np.float32); H,S,V=hsv[...,0],hsv[...,1]/255,hsv[...,2]/255
np.save('hsv.npy',np.dstack([H,S,V])); cv2.imwrite('src.png',im)
grey=((b-r)>.05)&(V>.3)&(S<.4)
white=(V>.72)&(S<.18)
black=V<.22
red=((H<9)|(H>165))&(S>.5)&(V>.35)
gold=(H>=9)&(H<26)&(S>.45)&(V>.45)
viz=np.zeros_like(im); viz[black]=(40,40,40); viz[white]=(255,255,255); viz[grey]=(200,160,120); viz[red]=(0,0,220); viz[gold]=(0,170,230)
cv2.imwrite('classes.jpg',cv2.resize(viz,None,fx=.35,fy=.35))
