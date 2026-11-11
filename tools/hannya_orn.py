"""Hannya em estêncil para o fundo do hero (mesma ideia do Harrib): recorta a máscara da pintura do Alessandro
e deixa só a tinta (linhas, olhos, boca, contorno) num alfa puro.
Saída: assets/img/hannya-orn.webp (preto + alfa).  Uso: python tools/hannya_orn.py [--ver]"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[1]
src = cv2.imread(str(R / 'assets/hero/hannya.webp'), cv2.IMREAD_COLOR)
src = cv2.resize(src, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
f = src.astype(np.float32) / 255
b, g, r = f[..., 0], f[..., 1], f[..., 2]
hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV).astype(np.float32)
H, S, V = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
lum = .299 * r + .587 * g + .114 * b

# rosto: cinza azulado; chifres: laranja/marrom
rosto = ((b - r) > .055) & (V > .28) & (V < .85) & (S < .45)
chifre = (H > 4) & (H < 22) & (S > .35) & (V > .3)
dente = (H > 14) & (H < 30) & (S > .45) & (V > .55)


def maior(m, k_close, n=1):
    m = cv2.morphologyEx(m.astype(np.uint8) * 255, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_close, k_close)))
    k, lab, st, _ = cv2.connectedComponentsWithStats(m)
    ordem = np.argsort(-st[1:, cv2.CC_STAT_AREA])[:n] + 1
    return np.isin(lab, ordem)


face = maior(rosto, 41)
horns = maior(chifre & (np.arange(src.shape[0])[:, None] < src.shape[0] * .45), 15, 2)
sil = (face | horns | (dente & cv2.dilate(face.astype(np.uint8), np.ones((61, 61))).astype(bool))).astype(np.uint8) * 255
sil = cv2.morphologyEx(sil, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71)))
# fecha os buracos (olhos, boca, testa preta)
cont, _ = cv2.findContours(sil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
sil = np.zeros_like(sil)
for c in cont:
    if cv2.contourArea(c) > 4000:
        cv2.drawContours(sil, [c], -1, 255, -1)
# tira a franja preta das nuvens que o fechamento colou na borda
sil = cv2.morphologyEx(sil, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 45)))
sil = cv2.erode(sil, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
sil = cv2.GaussianBlur(sil, (0, 0), 1.5) / 255.0

# tinta: escuro vira preto cheio, cinza do rosto some, vermelho da boca/olho vira meio-tom
tinta = np.clip((.40 - lum) / .16, 0, 1)
verm = ((H < 8) | (H > 168)) & (S > .45)
tinta = np.maximum(tinta, verm * .55)
# sombra do rosto em retícula grossa de pincel: só os cinzas mais fundos
tinta = np.maximum(tinta, np.clip((.47 - lum) / .1, 0, 1) * .5 * face)
# contorno da máscara
borda = cv2.morphologyEx((sil > .5).astype(np.uint8), cv2.MORPH_GRADIENT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
tinta = np.maximum(tinta, cv2.GaussianBlur(borda.astype(np.float32), (0, 0), 1.2))
a = np.clip(tinta * sil, 0, 1)
# dois tons, como estêncil: tinta cheia e um meio-tom chapado
a = np.where(a > .62, 1.0, np.where(a > .22, .42, 0.0)).astype(np.float32)
a = cv2.GaussianBlur(a, (0, 0), .9)

ys, xs = np.where(a > .05)
a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
im = Image.fromarray((a * 255).astype(np.uint8))
im.thumbnail((900, 900), Image.LANCZOS)
o = Image.merge('LA', (Image.new('L', im.size, 0), im))
(R / 'assets/img').mkdir(exist_ok=True)
o.save(R / 'assets/img/hannya-orn.webp', quality=84, method=6)
print('hannya-orn', im.size)
if '--ver' in sys.argv:
    v = Image.new('RGB', im.size, (239, 231, 217))
    v.paste((20, 18, 16), mask=im)
    v.save(sys.argv[-1])
