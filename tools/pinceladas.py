# -*- coding: utf-8 -*-
"""Hero "sumi": cada pintura do Alessandro se forma por pinceladas, como num sumi-e.
1) aguada (nijimi): manchas grandes e diluidas que sangram no papel;
2) pinceladas cada vez mais finas que seguem o fluxo da pintura, com pincel seco (kasure) no fim do traco;
3) o contorno preto, em tracos longos e caligraficos, por ultimo.
Saida: assets/hero/<peca>.bin (Uint16 x 10 por pincelada) + tools/pinceladas.json
Uso: python tools/pinceladas.py"""
import json, math
from pathlib import Path
import numpy as np, cv2
from PIL import Image

S = Path(__file__).resolve().parent.parent
L = json.loads((S / 'tools/laminas.json').read_text(encoding='utf8'))
W, H, PAD = 640, 960, 48
PAPEL = np.array([.937, .906, .851], np.float32)

# raio, espacamento, limiar de diferenca, comprimento (x raio), tipo
CAMADAS = [(46, .78, -1, (3.0, 5.0)), (20, .85, .012, (3.6, 6.5)), (10.5, .9, .024, (3.6, 7.0)),
           (5.8, .95, .036, (3.6, 7.0)), (3.2, .9, .055, (3.4, 6.5))]
INI = [0, .3, .68, 1.06, 1.42, 1.75]; DUR = [.7, .7, .68, .64, .6, .8]
TMAX = 4.0


def ruido(h, w, esc, sem):
    r = np.random.default_rng(sem).random((h // esc + 3, w // esc + 3)).astype(np.float32)
    return cv2.resize(r, (w + esc * 2, h + esc * 2), interpolation=cv2.INTER_CUBIC)[esc:esc + h, esc:esc + w]


def gera(slug, sem):
    rng = np.random.default_rng(sem)
    img = np.asarray(Image.open(S / f'assets/hero/{slug}.webp').convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.
    lum = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)[..., 0] / 100.

    def tensor(sig):
        gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
        jxx = cv2.GaussianBlur(gx * gx, (0, 0), sig); jyy = cv2.GaussianBlur(gy * gy, (0, 0), sig); jxy = cv2.GaussianBlur(gx * gy, (0, 0), sig)
        raiz = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2)
        coer = (raiz / (jxx + jyy + 1e-6)) ** 2 * np.clip((jxx + jyy) * 60, 0, 1)
        a = .5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2
        return np.cos(2 * a), np.sin(2 * a), coer

    pot = ruido(H, W, 200, sem + 5) + .4 * ruido(H, W, 100, sem + 6)
    sw = np.arctan2(cv2.Sobel(pot, cv2.CV_32F, 0, 1, ksize=5), cv2.Sobel(pot, cv2.CV_32F, 1, 0, ksize=5)) + np.pi / 2

    def campo(sig):
        vx = np.zeros((H, W), np.float32); vy = np.zeros_like(vx); pes = np.zeros_like(vx)
        for k in (1, 2.2, 4.5):
            cx, sx, co = tensor(sig * k); vx += cx * co; vy += sx * co; pes += co
        fraco = np.clip(1 - pes * 1.4, 0, 1) * .35
        vx += np.cos(2 * sw) * fraco; vy += np.sin(2 * sw) * fraco
        return .5 * np.arctan2(vy, vx)

    def am(a, x, y):
        return a[min(H - 1, max(0, int(y))), min(W - 1, max(0, int(x)))]

    def traca(ang, x, y, comp, passo, mask=None):
        pts = [(x, y)]
        for sgn in (1, -1):
            cx, cy = x, y; d0 = None
            for _ in range(int(comp / 2 / passo)):
                a = am(ang, cx, cy); dx, dy = math.cos(a), math.sin(a)
                if d0 is None: dx, dy = dx * sgn, dy * sgn
                elif dx * d0[0] + dy * d0[1] < 0: dx, dy = -dx, -dy
                cx += dx * passo; cy += dy * passo; d0 = (dx, dy)
                if not (-PAD * .5 <= cx < W + PAD * .5 and -PAD * .5 <= cy < H + PAD * .5): break
                if mask is not None and not am(mask, cx, cy): break
                if sgn > 0: pts.append((cx, cy))
                else: pts.insert(0, (cx, cy))
        return pts[0], pts[len(pts) // 2], pts[-1]

    ests = []
    prev = np.broadcast_to(PAPEL, img.shape).copy()
    for li, (r, esp, lim, cmp) in enumerate(CAMADAS):
        ang = campo(max(2.2, r * .45))
        alvo = cv2.GaussianBlur(img, (0, 0), max(.7, r * .35))
        if li == 0: alvo = alvo * .72 + PAPEL * .28          # aguada: a cor diluida
        dif = np.linalg.norm(cv2.GaussianBlur(alvo - prev, (0, 0), r * .6), axis=2)
        passo = r * esp
        gy, gx = np.mgrid[passo / 2 - PAD * .3:H + PAD * .3:passo, passo / 2 - PAD * .3:W + PAD * .3:passo]
        gx = gx + rng.uniform(-.5, .5, gx.shape) * passo; gy = gy + rng.uniform(-.5, .5, gy.shape) * passo
        n0 = len(ests)
        for x, y in zip(gx.ravel(), gy.ravel()):
            if lim > 0 and am(dif, x, y) < lim: continue
            p0, pm, p2 = traca(ang, x, y, r * rng.uniform(*cmp), max(1., r / 2.5))
            c = alvo[min(H - 1, max(0, int(pm[1]))), min(W - 1, max(0, int(pm[0])))].copy()
            c = np.clip(c * rng.uniform(.96, 1.04) + rng.normal(0, .01, 3), 0, 1)
            p1 = (2 * pm[0] - (p0[0] + p2[0]) / 2, 2 * pm[1] - (p0[1] + p2[1]) / 2)
            ests.append((p0, p1, p2, r * rng.uniform(.82, 1.0), c, li, x, y))
        prev = alvo
        print(slug, 'camada', li, 'r', r, len(ests) - n0, flush=True)

    # contorno: tinta escura e fina (some na abertura morfologica), tracada ao longo da linha
    escuro = (lum < .26).astype(np.uint8)
    aberto = cv2.morphologyEx(escuro, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    linha = cv2.dilate(escuro & (1 - aberto), np.ones((3, 3), np.uint8))
    ang = campo(1.6)
    tomado = np.zeros((H, W), np.uint8)
    ys, xs = np.nonzero(linha)
    ordem = rng.permutation(len(xs))
    n0 = len(ests)
    for k in ordem:
        x, y = float(xs[k]) + .5, float(ys[k]) + .5
        if tomado[int(y), int(x)]: continue
        p0, pm, p2 = traca(ang, x, y, rng.uniform(22, 46), 1.5, linha)
        if math.hypot(p2[0] - p0[0], p2[1] - p0[1]) < 6: continue
        cv2.line(tomado, (int(p0[0]), int(p0[1])), (int(pm[0]), int(pm[1])), 1, 5)
        cv2.line(tomado, (int(pm[0]), int(pm[1])), (int(p2[0]), int(p2[1])), 1, 5)
        c = np.clip(img[int(pm[1]) % H, int(pm[0]) % W] * .8, 0, 1)
        p1 = (2 * pm[0] - (p0[0] + p2[0]) / 2, 2 * pm[1] - (p0[1] + p2[1]) / 2)
        ests.append((p0, p1, p2, rng.uniform(2.6, 3.6), c, 5, x, y))
    print(slug, 'contorno', len(ests) - n0, flush=True)

    # tempo: o pincel desce do topo, com acaso; o contorno vai em ondas pela folha
    d = np.zeros((len(ests), 10), np.uint16)
    qx = lambda v: np.uint16(np.clip((v + PAD) / (W + 2 * PAD), 0, 1) * 65535)
    qy = lambda v: np.uint16(np.clip((v + PAD) / (H + 2 * PAD), 0, 1) * 65535)
    for i, (p0, p1, p2, w, c, li, x, y) in enumerate(ests):
        var = (y / H) * .6 + abs(x / W - .5) * .2 + rng.uniform(0, .4)
        t0 = INI[li] + var * DUR[li]
        d[i] = [qx(p0[0]), qy(p0[1]), qx(p1[0]), qy(p1[1]), qx(p2[0]), qy(p2[1]),
                np.uint16(min(1, w / 56) * 65535), np.uint16(min(1, t0 / TMAX) * 65535),
                int(c[0] * 255) | (int(c[1] * 255) << 8), int(c[2] * 255) | (li << 8)]
    d = d[np.argsort(d[:, 9] >> 8, kind='stable')]
    (S / f'assets/hero/{slug}.bin').write_bytes(d.tobytes())
    print(slug, 'total', len(d), round(len(d) * 20 / 1e3), 'KB')
    return len(d)


meta = {'W': W, 'H': H, 'pad': PAD, 'wmax': 56, 'tmax': TMAX, 'pecas': []}
for i, l in enumerate(L):
    meta['pecas'].append({'s': l['s'], 't': l['t'], 'n': gera(l['s'], 11 + i)})
for f in ('tools/pinceladas.json', 'assets/hero/pinceladas.json'):
    json.dump(meta, open(S / f, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
