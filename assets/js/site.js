(function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduz = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cel = function () { return innerWidth <= 860; };
  var WA = '34622688505';

  /* topo e menu */
  var topo = $('#topo'), mb = $('.menu-bt'), menu = $('#menu');
  function rola() { topo.classList.toggle('solido', scrollY > 30); }
  addEventListener('scroll', rola, { passive: true }); rola();
  function abre(v) {
    menu.hidden = !v; document.body.style.overflow = v ? 'hidden' : '';
    mb.setAttribute('aria-expanded', v); mb.setAttribute('aria-label', v ? 'Cerrar menú' : 'Abrir menú');
  }
  mb.addEventListener('click', function () { abre(mb.getAttribute('aria-expanded') !== 'true'); });
  $$('#menu a').forEach(function (a) { a.addEventListener('click', function () { abre(false); }); });
  addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) abre(false); });

  /* hero: sumi, cada pintura se forma a pincel */
  var LAM = window.LAM || [], NOMES = LAM.map(function (l) { return l.s; });
  var P = 5.5, N = NOMES.length, CICLO = P * N;
  var hero = $('.hero'), lamina = $('.lamina'), tit = $('.l-tit');
  var ultI = -1;
  function marca(t) {
    var i = Math.floor(t / P) % N;
    if (i !== ultI) {
      ultI = i; tit.style.opacity = 0;
      setTimeout(function () { tit.textContent = (LAM[i] || {}).t || ''; tit.style.opacity = 1; }, 200);
    }
  }
  function estatico() {
    $('.l-poster').src = 'assets/hero/hannya.webp';
    tit.textContent = (LAM[0] || {}).t || '';
  }
  function iniciaGL() {
    if (!window.sumi || !N || !window.fetch) return false;
    var teste = document.createElement('canvas').getContext('webgl2');
    if (!teste) return false;
    var cv = $('.l-gl'), V = '?v=1';
    var carrega = function (src) { return new Promise(function (ok, erro) { var im = new Image(); im.decoding = 'async'; im.onload = function () { ok(im); }; im.onerror = erro; im.src = src; }); };
    var bin = function (src) { return fetch(src).then(function (r) { if (!r.ok) throw r.status; return r.arrayBuffer(); }); };
    var H, t0 = 0, vis = true, raf = 0;
    function quadro(ts) {
      if (!t0) t0 = ts;
      var t = (ts - t0) / 1000;
      H.desenha(t, devicePixelRatio || 1); marca(t);
      raf = vis ? requestAnimationFrame(quadro) : 0;
    }
    fetch('assets/hero/pinceladas.json' + V).then(function (r) { return r.json(); }).then(function (meta) {
      return Promise.all(NOMES.map(function (n) {
        return Promise.all([bin('assets/hero/' + n + '.bin' + V), carrega('assets/hero/' + n + '.webp' + V)]).then(function (x) { return { bin: x[0], img: x[1] }; });
      })).then(function (pecas) {
        try { H = window.sumi(cv, pecas, meta); } catch (e) { H = null; }
        if (!H) { if (videoTentado) estatico(); else iniciaVideo(); return; }
        lamina.classList.add('gl');
        new IntersectionObserver(function (es) {
          vis = es[0].isIntersecting;
          if (vis && !raf) { t0 = 0; raf = requestAnimationFrame(quadro); }
        }).observe(lamina);
        raf = requestAnimationFrame(quadro);
      });
    }).catch(function () { if (videoTentado) estatico(); else iniciaVideo(); });
    return true;
  }
  var videoTentado = false;
  function iniciaVideo() {
    if (videoTentado) return; videoTentado = true;
    var v = $('.l-video');
    v.src = 'assets/video/sumi.mp4?v=2'; v.preload = 'auto';
    var p = v.play();
    // iPhone em modo de economia recusa o autoplay: aí o shader assume
    if (p && p.catch) p.catch(function () { if (!lamina.classList.contains('gl') && !iniciaGL()) estatico(); });
    // o video abre com a hannya nascendo do papel limpo; o laco volta ao inicio do tigre, que comeca com a hannya pronta
    v.addEventListener('ended', function () { v.currentTime = P; v.play().catch(function () {}); });
    v.addEventListener('playing', function () { lamina.classList.add('vd'); }, { once: true });
    v.addEventListener('error', function () { if (!iniciaGL()) estatico(); });
    (function laco() { if (!v.paused && lamina.classList.contains('vd')) marca(v.currentTime % CICLO); requestAnimationFrame(laco); })();
    document.addEventListener('visibilitychange', function () { if (!document.hidden && lamina.classList.contains('vd')) v.play().catch(function () {}); });
  }
  if (reduz) estatico();
  else if (matchMedia('(pointer: coarse)').matches || cel()) iniciaVideo();
  else if (!iniciaGL()) iniciaVideo();
  requestAnimationFrame(function () { hero.classList.add('pronto'); });

  /* surgir ao rolar */
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('vis'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px' }) : null;
  function observa(el) { if (io && !reduz) io.observe(el); else el.classList.add('vis'); }
  $$('.rev, .cab').forEach(observa);

  /* trabajos */
  var TRAB = window.TRAB || [], ROT = { color: 'A color', negro: 'En negro', espalda: 'Espalda o pecho' };
  var grade = $('#grade'), mais = $('#mais'), filtro = 'todos', limite = cel() ? 10 : 12, lista = [];
  function monta() {
    lista = TRAB.filter(function (x) { return filtro === 'todos' || x.c === filtro; });
    grade.innerHTML = '';
    lista.slice(0, limite).forEach(function (x, i) {
      var li = document.createElement('li'); li.className = 'card';
      li.innerHTML = '<button type="button" data-i="' + i + '"><span class="card-f"><img src="assets/img/trab/' + x.s + '-p.webp" alt="' + x.t + ', tatuaje ' + ROT[x.c].toLowerCase() + '" width="540" height="675" loading="lazy" decoding="async"></span>' +
        '<span class="card-t">' + x.t + '</span><span class="card-c">' + ROT[x.c] + '</span></button>';
      grade.appendChild(li); observa(li);
    });
    mais.parentNode.hidden = lista.length <= limite;
  }
  $$('.filtro').forEach(function (b) {
    b.addEventListener('click', function () {
      filtro = b.dataset.f; limite = cel() ? 10 : 12;
      $$('.filtro').forEach(function (o) { o.classList.toggle('on', o === b); o.setAttribute('aria-pressed', o === b); });
      monta();
    });
  });
  mais.addEventListener('click', function () { limite += cel() ? 10 : 12; monta(); });
  monta();

  /* lightbox */
  var lb = $('#lb'), lbImg = $('.lb-f img'), lbCap = $('.lb-f figcaption'), atual = 0, foco = null;
  function mostra(i) {
    atual = (i + lista.length) % lista.length; var x = lista[atual];
    lbImg.src = 'assets/img/trab/' + x.s + '.webp'; lbImg.alt = x.t; lbCap.textContent = x.t;
  }
  grade.addEventListener('click', function (e) {
    var b = e.target.closest('button[data-i]'); if (!b) return;
    foco = b; mostra(+b.dataset.i); lb.hidden = false; document.body.style.overflow = 'hidden'; $('.lb-x').focus();
  });
  function fecha() { lb.hidden = true; document.body.style.overflow = ''; if (foco) foco.focus(); }
  $('.lb-x').addEventListener('click', fecha);
  $('.lb-a').addEventListener('click', function () { mostra(atual - 1); });
  $('.lb-p').addEventListener('click', function () { mostra(atual + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) fecha(); });
  addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') fecha(); else if (e.key === 'ArrowLeft') mostra(atual - 1); else if (e.key === 'ArrowRight') mostra(atual + 1);
  });
  var tx = 0;
  lb.addEventListener('touchstart', function (e) { tx = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) { var d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 50) mostra(atual + (d < 0 ? 1 : -1)); });

  /* disponibles */
  var disp = $('#disp');
  (window.DISP || []).forEach(function (x) {
    var li = document.createElement('li'); li.className = 'dp rev';
    var msg = encodeURIComponent('Hola Alessandro, me interesa el diseño disponible "' + x.t + '". ¿Podemos hablar?');
    li.innerHTML = '<span class="dp-f"><img src="assets/img/disp/' + x.s + '.webp" alt="' + x.t + ', ' + x.d.toLowerCase() + '" width="900" height="1125" loading="lazy" decoding="async"></span>' +
      '<h3>' + x.t + '</h3><p>' + x.d + '</p><a class="bt bt-fio-c" href="https://wa.me/' + WA + '?text=' + msg + '" target="_blank" rel="noopener">Lo quiero</a>';
    disp.appendChild(li); observa(li);
  });

  /* nav ativa */
  var links = $$('.nav a');
  var io2 = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) links.forEach(function (a) { a.classList.toggle('ativo', a.getAttribute('href') === '#' + e.target.id); }); });
  }, { rootMargin: '-45% 0px -50% 0px' });
  $$('main section[id]').forEach(function (s) { io2.observe(s); });

  /* formulário → WhatsApp */
  $('#form').addEventListener('submit', function (e) {
    e.preventDefault();
    var f = e.target, v = function (n) { var el = f.elements[n]; return (el && el.value || '').trim(); }, msg = $('.form-msg');
    if (!v('nombre') || !v('idea')) { msg.textContent = 'Pon tu nombre y cuéntame la idea.'; return; }
    msg.textContent = '';
    var t = 'Hola Alessandro, soy ' + v('nombre') + '.\n\nIdea: ' + v('idea') +
      (v('zona') ? '\nZona: ' + v('zona') : '') + (v('tam') ? '\nTamaño: ' + v('tam') : '') + '\nAcabado: ' + v('acabado');
    open('https://wa.me/' + WA + '?text=' + encodeURIComponent(t), '_blank', 'noopener');
  });
})();
