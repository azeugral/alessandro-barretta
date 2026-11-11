# -*- coding: utf-8 -*-
"""Auditoria responsiva: 13 tamanhos; procura transbordo lateral e elementos fora do eixo no celular.
Uso: python tools/auditar.py [url]"""
import sys
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8766/'
TAM = [(320, 640), (360, 740), (375, 812), (390, 844), (414, 896), (430, 932), (768, 1024), (820, 1180), (844, 390), (1024, 768), (1280, 800), (1440, 900), (1920, 1080)]
JS = """() => {
  document.querySelectorAll('.rev,.card,.cab').forEach(e => e.classList.add('vis'));
  const W = document.documentElement.clientWidth, fora = [], torto = [];
  for (const e of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (e.closest('[hidden],.lb,.menu,.saltar,svg')) continue;
    const r = e.getBoundingClientRect(); if (!r.width) continue;
    if (r.right > W + 1 || r.left < -1) fora.push((e.className || e.tagName) + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
  }
  const eixo = ['.marca', '.lamina', '.l-pie', '.nombre-w', '.nombre-s', '.hero-sub', '.hero-bts', '.cab', '.filtros', '.grade', '.disp', '.pasos', '.sobre-foto', '.sobre-txt h2', '.datos', '.eventos', '.estudio', '.form', '.envio .bt', '.rodape-s', '.rodape-w', '.links', '.rodape-pe'];
  if (W < 860) for (const s of eixo) {
    for (const e of document.querySelectorAll(s)) { const r = e.getBoundingClientRect(); if (!r.width) continue;
      const d = (r.left + r.right) / 2 - W / 2; if (Math.abs(d) > 1.5) torto.push(s + ' ' + d.toFixed(1)); }
  }
  return {sw: document.documentElement.scrollWidth, W, fora: fora.slice(0, 8), torto};
}"""
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    ruim = 0
    for w, h in TAM:
        m = w < 860 or h < 520
        g = b.new_page(viewport={'width': w, 'height': h}, is_mobile=m, has_touch=m, device_scale_factor=1)
        g.goto(URL, wait_until='load'); g.wait_for_timeout(500)
        r = g.evaluate(JS)
        ok = r['sw'] <= r['W'] and not r['fora'] and not r['torto']
        ruim += not ok
        print(f"{w}x{h}", 'ok' if ok else 'PROBLEMA', '' if ok else r)
        g.close()
    b.close()
print('tudo certo' if not ruim else f'{ruim} tamanhos com problema')
