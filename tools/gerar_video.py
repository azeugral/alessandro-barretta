# -*- coding: utf-8 -*-
"""Grava o hero (grabado plancha a plancha) em MP4 para o celular: 720x1080 (2:3), 4 lâminas x 9 s = 36 s,
30 fps, loop perfeito. Também faz a capa 1200x630. Uso: python tools/gerar_video.py"""
import base64, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent
L = json.loads((S / 'tools/laminas.json').read_text(encoding='utf8'))
W, H, FPS, P = 720, 1080, 30, 9.0
du = lambda f, m: f'data:{m};base64,' + base64.b64encode((S / 'assets/hero' / f).read_bytes()).decode()
lam = [[du(l['s'] + '.webp', 'image/webp'), du(l['s'] + '-p.png', 'image/png'), l['cores']] for l in L]
(S / 'assets/video').mkdir(exist_ok=True)
saida = S / 'assets/video/grabado.mp4'
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(); g.set_content('<canvas id=c></canvas>')
    g.add_script_tag(content=(S / 'assets/js/prensa.js').read_text(encoding='utf8'))
    g.evaluate(f"""async(a)=>{{const Ld=async s=>{{const m=new Image();m.src=s;await m.decode();return m}};const ls=[];
      for(const l of a){{ls.push([await Ld(l[0]),await Ld(l[1]),l[2]])}} window.Pr=prensa(document.getElementById('c'),ls,{{guardar:true,tam:[{W},{H}]}})}}""", lam)
    n = int(round(P * len(lam) * FPS))
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                           '-c:v', 'libx264', '-preset', 'slow', '-crf', '28', '-pix_fmt', 'yuv420p', '-tune', 'film',
                           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-g', str(FPS * 2),
                           '-movflags', '+faststart', '-an', str(saida)], stdin=subprocess.PIPE)
    for k in range(n):
        d = g.evaluate(f"(Pr.desenha({k / FPS},1),document.getElementById('c').toDataURL('image/jpeg',.94))")
        ff.stdin.write(base64.b64decode(d.split(',', 1)[1]))
        if k % 270 == 0: print(k, '/', n, flush=True)
    ff.stdin.close(); ff.wait(); b.close()

# capa 1200x630: papel, a hannya e o tigre prontos lado a lado com o nome entre eles
papel = Image.new('RGB', (1200, 630), (239, 231, 217))
for x, s in [(150, 'hannya'), (750, 'tigre')]:
    im = Image.open(S / f'assets/hero/{s}.webp').convert('RGB').resize((300, 450), Image.LANCZOS)
    papel.paste(im, (x, 90))
papel.save(S / 'assets/img/capa.jpg', quality=88)
print('mp4', round(saida.stat().st_size / 1e6, 2), 'MB')
