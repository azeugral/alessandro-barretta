# -*- coding: utf-8 -*-
"""Tira de quadros do hero para conferir: python tools/ver_prensa.py [peça] -> ../_ref/prensa-tira.jpg"""
import base64, io, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent
L = json.loads((S / 'tools/laminas.json').read_text(encoding='utf8'))
du = lambda f, m: f'data:{m};base64,' + base64.b64encode((S / 'assets/hero' / f).read_bytes()).decode()
lam = [[du(l['s'] + '.webp', 'image/webp'), du(l['s'] + '-p.png', 'image/png'), l['cores']] for l in L]
pc = int(sys.argv[1]) if len(sys.argv) > 1 else 0
ts = [.3, 1.2, 2.0, 2.8, 3.6, 4.4, 5.2, 6.0, 7.0, 8.5]
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(); g.set_content('<canvas id=c></canvas>')
    g.add_script_tag(content=(S / 'assets/js/prensa.js').read_text(encoding='utf8'))
    g.evaluate("""async(a)=>{const Ld=async s=>{const m=new Image();m.src=s;await m.decode();return m};const ls=[];
      for(const l of a){ls.push([await Ld(l[0]),await Ld(l[1]),l[2]])} window.Pr=prensa(document.getElementById('c'),ls,{guardar:true,tam:[400,600]})}""", lam)
    F = Image.new('RGB', (400 * len(ts), 600))
    for k, t in enumerate(ts):
        d = g.evaluate(f"(Pr.desenha({pc * 9 + t},1),document.getElementById('c').toDataURL('image/jpeg',.9))")
        F.paste(Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))), (k * 400, 0))
    b.close()
F.save(S.parent / '_ref/prensa-tira.jpg', quality=85)
