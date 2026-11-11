# -*- coding: utf-8 -*-
"""Recorta as pinturas dele no formato ōban (2:3) e separa cada uma em planchas de cor (k-means em Lab),
como uma xilogravura ukiyo-e: cada plancha é impressa por vez no hero.
Saída: assets/hero/<slug>.webp (cor) e <slug>-p.png (índice da plancha no canal R, 0..N-1, ordem de impressão).
Uso: python tools/laminas.py"""
import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter
from skimage.color import rgb2lab

def kmeans(X, k, it=30, seed=1):
    r = np.random.default_rng(seed); C = X[r.choice(len(X), 1)]
    for _ in range(k - 1):  # k-means++
        d = ((X[:, None] - C[None]) ** 2).sum(-1).min(1); C = np.vstack([C, X[r.choice(len(X), p=d / d.sum())]])
    for _ in range(it):
        lb = ((X[:, None] - C[None]) ** 2).sum(-1).argmin(1)
        C = np.array([X[lb == j].mean(0) if (lb == j).any() else C[j] for j in range(k)])
    return C
S = Path(__file__).resolve().parent.parent
IG = S.parent / '_ref/ig'
W, H, K = 800, 1200, 6
LAM = [  # slug, arquivo, recorte, título
    ('hannya', '061.1', (170, 110, 1300, 1805), 'Hannya'),
    ('tigre', '150.1', (170, 110, 1290, 1790), 'Tigre solitario'),
    ('amaterasu', '030.1', (230, 160, 2850, 4090), 'Amaterasu'),
    ('loto', '007.1', (300, 200, 2720, 3830), 'Calavera y loto'),
]
info = []
for slug, f, box, tit in LAM:
    im = Image.open(IG / f'{f}.jpg').convert('RGB').crop(box).resize((W, H), Image.LANCZOS)
    im.save(S / f'assets/hero/{slug}.webp', quality=90, method=6)
    a = np.asarray(im.resize((W // 4, H // 4)), np.float32) / 255
    lab = rgb2lab(a).reshape(-1, 3)
    C = kmeans(lab, K)
    full = rgb2lab(np.asarray(im, np.float32) / 255).reshape(-1, 3)
    lb = np.concatenate([((full[i:i+200000, None] - C[None]) ** 2).sum(-1).argmin(1) for i in range(0, len(full), 200000)]).reshape(H, W)
    # ordem de impressão: do mais claro ao mais escuro (o preto, a plancha-chave, por último)
    ordem = np.argsort(-C[:, 0])
    rank = np.zeros(K, int); rank[ordem] = np.arange(K)
    idx = rank[lb].astype(np.uint8)
    # suaviza ruído de 1 px (moda 3x3)
    idx = np.asarray(Image.fromarray(idx * 40).filter(ImageFilter.ModeFilter(3))) // 40
    Image.fromarray((idx * 40).astype(np.uint8)).save(S / f'assets/hero/{slug}-p.png', optimize=True)
    from skimage.color import lab2rgb
    cores = [[round(float(v), 3) for v in lab2rgb(C[o][None, None, :])[0, 0]] for o in ordem]
    info.append({'s': slug, 't': tit, 'cores': cores})
    print(slug, [round(C[o][0]) for o in ordem])
(S / 'tools/laminas.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf8')
