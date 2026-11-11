# -*- coding: utf-8 -*-
"""Tira de quadros do hero sumi: python tools/ver_sumi.py [peça] [tempos...] -> ../_ref/sumi-tira.jpg"""
import base64, io, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent
M = json.loads((S / 'tools/pinceladas.json').read_text(encoding='utf8'))
b64 = lambda f: base64.b64encode((S / 'assets/hero' / f).read_bytes()).decode()
pec = [[b64(p['s'] + '.bin'), 'data:image/webp;base64,' + b64(p['s'] + '.webp')] for p in M['pecas']]
pc = int(sys.argv[1]) if len(sys.argv) > 1 else 0
ts = [float(x) for x in sys.argv[2:]] or [.3, .6, .9, 1.2, 1.5, 1.8, 2.1, 2.5, 3.2, 6.9]
TW, TH = 400, 600


def abre(p, w, h):
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(); g.set_content('<canvas id=c></canvas>')
    g.add_script_tag(content=(S / 'assets/js/sumi.js').read_text(encoding='utf8'))
    g.evaluate("""async([a,m,w,h])=>{const ps=[];for(const [bn,im] of a){const u=Uint8Array.from(atob(bn),c=>c.charCodeAt(0));
      const i=new Image();i.src=im;await i.decode();ps.push({bin:u.buffer,img:i})}
      window.Pr=sumi(document.getElementById('c'),ps,m,{guardar:true,tam:[w,h],laco:true})}""", [pec, M, w, h])
    return b, g


if __name__ == '__main__':
    with sync_playwright() as p:
        b, g = abre(p, TW, TH)
        F = Image.new('RGB', (TW * len(ts), TH))
        for k, t in enumerate(ts):
            d = g.evaluate(f"(Pr.desenha({pc * 5.5 + t},1),document.getElementById('c').toDataURL('image/jpeg',.9))")
            F.paste(Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))), (k * TW, 0))
        b.close()
    F.save(S.parent / '_ref/sumi-tira.jpg', quality=85)
