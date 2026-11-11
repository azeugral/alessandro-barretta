import numpy as np, potrace, cv2, time
out=np.load('out.npy').astype(np.float32)
# suaviza o serrilhado antes de traçar
sm=cv2.GaussianBlur(out,(0,0),1.6)>.5
t=time.time()
bm=potrace.Bitmap(~sm)
pl=bm.trace(turdsize=6,turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,alphamax=1.1,opticurve=True,opttolerance=.3)
f=lambda p:f"{p[0]:.1f} {p[1]:.1f}" if isinstance(p,tuple) else f"{p.x:.1f} {p.y:.1f}"
d=[]
for c in pl:
    d.append("M"+f(c.start_point))
    for sg in c.segments:
        if sg.is_corner: d.append("L"+f(sg.c)+"L"+f(sg.end_point))
        else: d.append("C"+f(sg.c1)+" "+f(sg.c2)+" "+f(sg.end_point))
    d.append("Z")
h,w=out.shape
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><path fill-rule="evenodd" d="{"".join(d)}"/></svg>'
open('hannya.svg','w').write(svg)
print(len(pl),'curvas',len(svg)//1024,'KB',round(time.time()-t,1),'s')
