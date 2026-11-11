# -*- coding: utf-8 -*-
"""Grava o hero (sumi, pintura a pincel) em MP4 para o celular: 720x1080 (2:3), 4 peças x 5,5 s = 22 s,
30 fps, loop perfeito. Também faz a capa 1200x630. Uso: python tools/gerar_video.py"""
import base64, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent
W, H, FPS, P = 720, 1080, 30, 5.5
import sys; sys.path.insert(0, str(S / 'tools'))
from ver_sumi import abre, M
(S / 'assets/video').mkdir(exist_ok=True)
saida = S / 'assets/video/sumi.mp4'
with sync_playwright() as p:
    b, g = abre(p, W, H)
    n = int(round(P * len(M['pecas']) * FPS))
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
