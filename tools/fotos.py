# -*- coding: utf-8 -*-
"""Gera as fotos do site a partir do IG baixado (../_ref/ig) e o assets/js/dados.js.
Portfólio em 4:5 (1080x1350 e miniatura 540x675), diseños disponibles, retrato do Sobre.
Uso: python tools/fotos.py"""
import json
from pathlib import Path
from PIL import Image, ImageOps
S = Path(__file__).resolve().parent.parent
IG = S.parent / '_ref/ig'
(S / 'assets/img/trab').mkdir(parents=True, exist_ok=True)
(S / 'assets/img/disp').mkdir(parents=True, exist_ok=True)

# (arquivo, categoria, título, foco vertical 0..1)
TRAB = [
    ('086.1', 'color', 'Hannya', .5), ('005.1', 'negro', 'Pantera', .45), ('024.1', 'color', 'Namakubi', .5),
    ('068.1', 'color', 'Kitsune', .45), ('128.1', 'espalda', 'Espalda de dragón y hannya', .4), ('089.1', 'color', 'Geisha con hannya', .45),
    ('042.1', 'color', 'Tigre', .5), ('077.1', 'negro', 'Pantera mariposa', .5), ('018.1', 'color', 'Dragón', .45),
    ('072.1', 'color', 'Fudō Myōō', .45), ('027.1', 'espalda', 'Espalda en proceso', .45), ('019.1', 'color', 'Kappa', .5),
    ('069.1', 'color', 'Serpiente', .5), ('064.1', 'color', 'Pantera y mano', .5), ('023.1', 'color', 'Peonías', .5),
    ('074.1', 'negro', 'Caballo de ajedrez', .5), ('057.1', 'espalda', 'Pecho: Kintarō y koi', .45), ('168.1', 'color', 'Namakubi y daga', .5),
    ('070.1', 'color', 'Calavera en llamas', .45), ('025.1', 'negro', 'Sirena', .5), ('159.1', 'color', 'Geisha', .45),
    ('166.1', 'espalda', 'Espalda de dragón', .45), ('145.1', 'color', 'Hannya', .5), ('082.1', 'negro', 'Pantera', .5),
    ('087.1', 'color', 'Melocotón', .5), ('058.1', 'color', 'Tennin', .45), ('169.1', 'color', 'Santa Muerte', .45),
    ('036.1', 'espalda', 'Espalda en proceso', .45), ('123.1', 'color', 'Corazón y golondrina', .5), ('032.1', 'negro', 'Caballero', .45),
    ('066.1', 'color', 'Montaña y peonía', .45), ('151.1', 'espalda', 'Espalda a color', .45), ('116.1', 'color', 'Hannya', .5),
    ('078.1', 'negro', 'Dados', .5), ('136.1', 'color', 'Mariposa calavera', .5), ('125.9', 'color', 'Tigre', .5),
]
DISP = [
    ('061.1', 'Hannya entre ondas', 'Pintura · diseño para tatuar', (170, 110, 1300, 1805)),
    ('150.1', 'Tigre solitario', 'Acuarela y tinta · original a la venta', (170, 110, 1290, 1790)),
    ('029.1', 'Hannya para brazo', 'Proyecto de brazo completo', None),
    ('031.1', 'Kintarō y koi', 'Tinta china y acuarela en papel de arroz', None),
    ('121.1', 'Fudō para espalda', 'Proyecto de espalda', None),
    ('003.1', 'Yūrei', 'Kakejiku (pergamino japonés)', None),
    ('132.3', 'Dama y calavera', 'Diseño en negro', None),
    ('132.4', 'Tigre', 'Diseño en negro', None),
    ('132.5', 'Segador', 'Diseño en negro', None),
    ('132.6', 'Dama', 'Diseño en negro', None),
    ('132.2', 'Peonía', 'Diseño en negro', None),
    ('132.8', 'Dama y pantera', 'Diseño en negro', None),
]


def corta(im, r, fy=.5):
    w, h = im.size
    if w / h > r:
        nw = round(h * r); x = (w - nw) // 2; return im.crop((x, 0, x + nw, h))
    nh = round(w / r); y = int(min(max(fy * h - nh / 2, 0), h - nh)); return im.crop((0, y, w, y + nh))


dados = {'trab': [], 'disp': []}
for f, c, t, fy in TRAB:
    im = ImageOps.exif_transpose(Image.open(IG / f'{f}.jpg')).convert('RGB')
    im = corta(im, .8, fy)
    s = f.replace('.', '-')
    im.resize((1080, 1350), Image.LANCZOS).save(S / f'assets/img/trab/{s}.webp', quality=84, method=6)
    im.resize((540, 675), Image.LANCZOS).save(S / f'assets/img/trab/{s}-p.webp', quality=80, method=6)
    dados['trab'].append({'s': s, 'c': c, 't': t})
for f, t, d, box in DISP:
    im = ImageOps.exif_transpose(Image.open(IG / f'{f}.jpg')).convert('RGB')
    if box: im = im.crop(box)
    im = corta(im, .8, .5)
    s = f.replace('.', '-')
    im.resize((900, 1125), Image.LANCZOS).save(S / f'assets/img/disp/{s}.webp', quality=84, method=6)
    dados['disp'].append({'s': s, 't': t, 'd': d})
# retrato do Sobre
im = Image.open(IG / '108.1.jpg').convert('RGB').crop((140, 0, 783, 804))
im.resize((864, 1080), Image.LANCZOS).save(S / 'assets/img/alessandro.webp', quality=86, method=6)
lam = json.loads((S / 'tools/laminas.json').read_text(encoding='utf8'))
(S / 'assets/js/dados.js').write_text('window.TRAB=' + json.dumps(dados['trab'], ensure_ascii=False) + ';\nwindow.DISP=' +
                                      json.dumps(dados['disp'], ensure_ascii=False) + ';\nwindow.LAM=' + json.dumps(lam, ensure_ascii=False) + ';\n', encoding='utf8')
print(len(dados['trab']), len(dados['disp']))
