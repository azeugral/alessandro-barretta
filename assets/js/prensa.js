/* Hero "xilogravura": cada pintura do Alessandro é impressa como um ukiyo-e, plancha por plancha,
   sobre papel washi. A cor entra chapada, com o veio da madeira e um leve deslize até o registro;
   as planchas se sobrepõem e o detalhe da pintura original sobe junto com as últimas (forma completa em ~3,5 s). Depois a tinta sai e vem a próxima.
   prensa(canvas, laminas[[imgCor, imgPlanchas, cores[6]]], {guardar, tam}) -> {P, n, K, fase(t), desenha(t, dpr)} */
(function () {
  var P = 7.5, K = 6, T0 = .3, DL = .38, DUR = .75;
  var VS = 'attribute vec2 p;varying vec2 vv;void main(){vv=p*.5+.5;vv.y=1.-vv.y;gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;varying vec2 vv;',
    'uniform sampler2D C,L;uniform vec3 cor[6];uniform float s,P,T0,DL,DUR;uniform vec2 res;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}',
    'float fb(vec2 p){float a=.5,r=0.;for(int k=0;k<4;k++){r+=a*n(p);p=p*2.07+vec2(3.1,7.7);a*=.5;}return r;}',
    'float ease(float x){x=clamp(x,0.,1.);return 1.-pow(1.-x,3.);}',
    'float pid(vec2 u){return floor(texture2D(L,u).r*255./40.+.5);}',
    'vec3 corDe(float i){vec3 c=cor[0];for(int k=1;k<6;k++){if(abs(float(k)-i)<.5)c=cor[k];}return c;}',
    'float veioDe(vec2 u,float i){return fb(vec2(u.x*2.2,u.y*60.)+vec2(0.,fb(u*3.)*4.)+i*5.3);}',
    'void main(){',
    ' vec2 u=vv;',
    // papel washi: base quente, fibras longas e pintas
    ' float fib=fb(u*vec2(16.,24.)+fb(u*5.)*3.)*.75+fb(u*vec2(40.,160.)+fb(u*9.+4.)*6.)*.25;',
    ' vec3 papel=vec3(.937,.906,.851)*(.965+.05*fib)-step(.9965,h(floor(u*res*.5)))*.06;',
    // planchas sobrepostas: cada uma começa antes da anterior terminar e desliza até o registro
    ' vec3 o=papel; vec3 pf=mix(vec3(1.),papel/.92,.35);',
    ' float id=pid(u), veio=veioDe(u,id);',
    ' for(int k=0;k<6;k++){',
    '  float fk=float(k); float e=clamp((s-T0-fk*DL)/DUR,0.,1.);',
    '  if(e<=0.) continue;',
    '  vec2 dk=(vec2(h(vec2(fk,1.)),h(vec2(2.,fk)))-.5)*.026;',
    '  vec2 uo=u+dk*(1.-ease(e));',
    '  if(abs(pid(uo)-fk)>.5) continue;',
    '  float g=veioDe(uo,fk); float c=smoothstep(g-.22,g+.22,ease(e)*1.5-.25);',
    '  o=mix(o,corDe(fk)*(.9+.12*g)*pf,c*.97);',
    ' }',
    // o detalhe da pintura original sobe junto com as últimas planchas, num degradê macio pelo veio
    ' float dd=smoothstep(T0+4.2*DL,T0+5.*DL+DUR+.55,s);',
    ' float dm=smoothstep(veio-.3,veio+.3,dd*1.6-.3);',
    ' vec3 orig=texture2D(C,u).rgb*(.97+.04*fib);',
    ' o=mix(o,orig,dm);',
    // saída: a tinta é lavada e volta o papel
    ' float sa=smoothstep(P-.95,P-.1,s);',
    ' float lv=fb(u*3.5+7.)*.8+fb(u*vec2(6.,40.))*.2; float sm=smoothstep(lv-.2,lv+.2,sa*1.6-.3);',
    ' o=mix(o,papel,sm);',
    // borda levemente sombreada e grão
    ' vec2 w=u-.5; o*=1.-.1*pow(length(w*vec2(1.3,1.))*1.5,3.);',
    ' o+=(h(u*res+fract(s)*37.)-.5)*.014;',
    ' gl_FragColor=vec4(o,1.);}'
  ].join('\n');

  window.prensa = function (cv, lam, op) {
    op = op || {};
    var gl = cv.getContext('webgl', { antialias: false, alpha: false, preserveDrawingBuffer: !!op.guardar, powerPreference: 'low-power' });
    if (!gl) return null;
    function sh(tp, src) { var o = gl.createShader(tp); gl.shaderSource(o, src); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(o); return o; }
    var pr = gl.createProgram();
    gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr); gl.useProgram(pr);
    var bf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    var lp = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(lp); gl.vertexAttribPointer(lp, 2, gl.FLOAT, false, 0, 0);
    function tex(img, perto) {
      var t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
      var f = perto ? gl.NEAREST : gl.LINEAR;
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, f); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, f);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      return t;
    }
    var T = lam.map(function (l) { return [tex(l[0]), tex(l[1], true), [].concat.apply([], l[2])]; });
    var U = {}; ['C', 'L', 'cor', 's', 'P', 'T0', 'DL', 'DUR', 'res'].forEach(function (k) { U[k] = gl.getUniformLocation(pr, k); });
    gl.uniform1i(U.C, 0); gl.uniform1i(U.L, 1); gl.uniform1f(U.P, P); gl.uniform1f(U.T0, T0); gl.uniform1f(U.DL, DL); gl.uniform1f(U.DUR, DUR);
    var n = T.length;
    function fase(t) {
      var i = Math.floor(t / P) % n, s = t - Math.floor(t / P) * P;
      return { i: i, s: s, plancha: Math.max(-1, Math.min(K, Math.floor((s - T0) / DL))) };
    }
    return {
      P: P, n: n, K: K, T0: T0, DL: DL, DUR: DUR, fase: fase,
      desenha: function (t, dpr) {
        var r = cv.getBoundingClientRect(); dpr = Math.min(dpr || 1, 2);
        var W = op.tam ? op.tam[0] : Math.max(2, Math.round(r.width * dpr)), H = op.tam ? op.tam[1] : Math.max(2, Math.round(r.height * dpr));
        if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
        var f = fase(t), c = T[f.i];
        gl.viewport(0, 0, W, H);
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, c[0]);
        gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, c[1]);
        gl.uniform3fv(U.cor, c[2]); gl.uniform1f(U.s, f.s); gl.uniform2f(U.res, W, H);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      }
    };
  };
})();
