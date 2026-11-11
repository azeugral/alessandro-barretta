/* Hero "sumi" (WebGL2): cada pintura do Alessandro se forma por pinceladas sobre papel washi.
   Aguada que sangra (nijimi), pinceladas que afinam com pincel seco no fim (kasure), contorno caligrafico por ultimo;
   a pintura original assenta por baixo e a proxima ja comeca a ser pintada sobre ela, que se dissolve (sem pausa).
   sumi(canvas, pecas[{bin: ArrayBuffer, img: Image}], meta, {guardar, tam, laco}) -> {P, n, desenha(t, dpr)} */
(function () {
  var P = 5.5, FIM = 2.75;
  var VS = [
    '#version 300 es',
    'precision highp float;',
    'layout(location=0) in vec4 aA; layout(location=1) in vec4 aB; layout(location=2) in uvec2 aC;',
    'uniform float uT, uW, uH, uPad, uWmax, uTmax;',
    'out vec2 vUV; out vec3 vCor; out float vPr, vSem, vCam, vSeco;',
    'vec2 bez(vec2 a,vec2 b,vec2 c,float u){float k=1.-u;return k*k*a+2.*k*u*b+u*u*c;}',
    'vec2 dbez(vec2 a,vec2 b,vec2 c,float u){return 2.*(1.-u)*(b-a)+2.*u*(c-b);}',
    'void main(){',
    ' vec2 esc=vec2(uW,uH)+2.*uPad;',
    ' vec2 p0=aA.xy*esc-uPad, p1=aA.zw*esc-uPad, p2=aB.xy*esc-uPad;',
    ' float w=aB.z*uWmax, t0=aB.w*uTmax, cam=float(aC.y>>8u);',
    ' float dur=cam>4.5?.42:.24+.04*(4.-cam);',
    ' float pr=clamp((uT-t0)/dur,0.,1.); pr=1.-pow(1.-pr,2.2);',
    ' float seco=clamp((uT-t0-dur)/.7,0.,1.);',
    ' int i=gl_VertexID/2; float lado=float(gl_VertexID%2)*2.-1.;',
    ' float u=float(i)/10., us=u*pr;',
    ' vec2 p=bez(p0,p1,p2,us), d=normalize(dbez(p0,p1,p2,us)+1e-5), n=vec2(-d.y,d.x);',
    // pressao do pincel: encosta cheio no comeco e levanta no fim; o contorno afina nas duas pontas
    ' float corpo=cam>4.5? .25+.75*pow(sin(3.14159*clamp(u,.0,1.)),.55) : .55+.45*sqrt(sin(3.14159*clamp(mix(.12,.94,u),0.,1.)));',
    ' if(cam<.5) corpo*=1.+.14*seco;',  // a aguada se espalha um pouco no papel enquanto seca
    ' p+=n*lado*w*.5*corpo;',
    ' if(pr<=0.) p=vec2(-9999.);',
    ' gl_Position=vec4(p.x/uW*2.-1., 1.-p.y/uH*2., 0., 1.);',
    ' vUV=vec2(us,lado); vPr=pr; vCam=cam; vSeco=seco;',
    ' vCor=vec3(float(aC.x&255u),float(aC.x>>8u),float(aC.y&255u))/255.;',
    ' vSem=fract(sin(dot(aA.xy+aB.xy,vec2(127.1,311.7)))*43758.5453);',
    '}'].join('\n');
  var FS = [
    '#version 300 es',
    'precision highp float;',
    'in vec2 vUV; in vec3 vCor; in float vPr, vSem, vCam, vSeco; out vec4 o;',
    'uniform float uT; uniform vec2 uRes;',
    'float h2(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float n2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h2(i),h2(i+vec2(1,0)),f.x),mix(h2(i+vec2(0,1)),h2(i+vec2(1,1)),f.x),f.y);}',
    'float h(float x){return fract(sin(x*91.345)*47453.5453);}',
    'float vn(float x){float i=floor(x),f=fract(x);f=f*f*(3.-2.*f);return mix(h(i),h(i+1.),f);}',
    'float vn2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);',
    ' float a=h(i.x+i.y*57.),b=h(i.x+1.+i.y*57.),c=h(i.x+(i.y+1.)*57.),d=h(i.x+1.+(i.y+1.)*57.);return mix(mix(a,b,f.x),mix(c,d,f.x),f.y);}',
    'void main(){',
    ' float s=vUV.x, v=vUV.y, sem=vSem*100.;',
    ' float fr=11.+9.*vSem;',
    ' float cer=vn(v*fr+sem)*.6+vn(v*fr*2.6+sem*1.7)*.4;',            // cerdas do pincel
    ' float cer2=vn2(vec2(v*fr*1.4+sem,s*4.));',
    ' float ini=smoothstep(0.,.04+.08*cer2,s);',
    ' float fim=smoothstep(vPr,vPr-.05-.14*cer2,s);',
    ' float a;',
    // primeiro o sumi: o valor da pintura em tinta preta diluida; depois a cor escorre por cima em manchas (nijimi)
    ' float lu=dot(vCor,vec3(.3,.59,.11));',
    ' vec3 tinta=mix(vec3(.075,.07,.068),vec3(.93,.9,.85),pow(lu,.85));',
    ' vec2 q=gl_FragCoord.xy/uRes;',
    ' float ag=n2(q*vec2(3.,4.5)+1.7)*.65+n2(q*vec2(9.,13.))*.35;',
    ' float ce=clamp((uT-1.35)/1.3,0.,1.);',
    ' float mc=smoothstep(ag-.12,ag+.12,ce*1.35-.15);',
    ' vec3 c=mix(tinta,vCor,mc);',
    ' if(vCam<.5){',                                                 // aguada (nijimi): borda mole e franja escura onde a agua para
    '  float r=abs(v)+(vn2(vec2(s*5.+sem,v*3.))-.5)*.35;',
    '  a=(1.-smoothstep(.45,1.,r))*ini*fim*.82;',
    '  c*=1.-.1*smoothstep(.55,.8,r)*smoothstep(1.,.85,r);',
    ' } else {',
    '  float kas=(vCam>4.5?.45:.3+.08*vCam)+.2*vSem;',                  // pincel seco (kasure): a tinta acaba no fim do traco
    '  float seca=smoothstep(.4,1.,s)*kas;',
    '  float borda=1.-smoothstep(.72-.3*cer,1.,abs(v));',
    '  a=borda*ini*fim*(1.-step(cer,seca*1.15)*.92);',
    '  float rel=vn(v*fr+sem+.35)-vn(v*fr+sem-.35);',
    '  c=c*(.92+.14*cer)+rel*.035;',
    '  c*=1.-.07*(1.-smoothstep(0.,.18,s));',                          // poca de tinta onde o pincel encosta
    ' }',
    ' c*=mix(.86,1.,vSeco);',                                          // tinta molhada mais escura, clareia ao secar
    ' if(a<.01) discard;',
    ' o=vec4(c*a,a);',
    '}'].join('\n');
  var VQ = '#version 300 es\nin vec2 p;out vec2 uv;void main(){uv=p*.5+.5;uv.y=1.-uv.y;gl_Position=vec4(p,0.,1.);}';
  var FQ = [
    '#version 300 es',
    'precision highp float;',
    'in vec2 uv; out vec4 o; uniform sampler2D C, C2; uniform float s, modo, P, FIM, tem; uniform vec2 res;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}',
    'float fb(vec2 p){float a=.5,r=0.;for(int k=0;k<4;k++){r+=a*n(p);p=p*2.07+vec2(3.1,7.7);a*=.5;}return r;}',
    'void main(){',
    ' vec2 u=uv;',
    ' float fib=fb(u*vec2(16.,24.)+fb(u*5.)*3.)*.75+fb(u*vec2(40.,160.)+fb(u*9.+4.)*6.)*.25;',
    ' vec3 papel=vec3(.937,.906,.851)*(.965+.05*fib)-step(.9965,h(floor(u*res*.5)))*.06;',
    ' vec2 w=u-.5; float vin=.1*pow(length(w*vec2(1.3,1.))*1.5,3.);',
    // entrada: a peca anterior se dissolve no papel por baixo das primeiras pinceladas, sem folha vazia
    ' if(modo<.5){',
    '  float lv=fb(u*3.5+7.)*.7+fb(u*vec2(5.,30.)+vec2(0.,s*.4))*.3; float sm=smoothstep(lv-.2,lv+.2,smoothstep(0.,1.7,s)*1.6-.3);',
    '  vec3 ant=texture(C2,u).rgb*(.97+.04*fib)*(1.-vin);',
    '  o=vec4(mix(papel,ant,tem*(1.-sm)),1.); return; }',
    // a pintura original assenta por baixo das pinceladas, em manchas macias
    ' float g=fb(u*4.+3.)*.8+fb(u*vec2(9.,14.))*.2;',
    ' float dd=smoothstep(FIM-.5,FIM+1.4,s); float dm=smoothstep(g-.25,g+.25,dd*1.5-.25);',
    ' vec3 orig=texture(C,u).rgb*(.97+.04*fib);',
    ' float a=dm; vec3 cor=orig*(1.-vin)*a;',
    ' o=vec4(cor,a);',
    '}'].join('\n');

  function sh(gl, t, s) { var o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(o); return o; }
  function prog(gl, v, f) { var p = gl.createProgram(); gl.attachShader(p, sh(gl, gl.VERTEX_SHADER, v)); gl.attachShader(p, sh(gl, gl.FRAGMENT_SHADER, f)); gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw gl.getProgramInfoLog(p); return p; }

  window.sumi = function (cv, pecas, meta, op) {
    op = op || {};
    var gl = cv.getContext('webgl2', { antialias: true, alpha: false, premultipliedAlpha: true, preserveDrawingBuffer: !!op.guardar, powerPreference: 'low-power' });
    if (!gl) return null;
    var PR = prog(gl, VS, FS), Q = prog(gl, VQ, FQ);
    var U = function (n) { return gl.getUniformLocation(PR, n); }, UQ = function (n) { return gl.getUniformLocation(Q, n); };
    var qv = gl.createVertexArray(); gl.bindVertexArray(qv);
    var qb = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, qb);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    var T = pecas.map(function (pc) {
      var vao = gl.createVertexArray(); gl.bindVertexArray(vao);
      var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, pc.bin, gl.STATIC_DRAW);
      gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 4, gl.UNSIGNED_SHORT, true, 20, 0); gl.vertexAttribDivisor(0, 1);
      gl.enableVertexAttribArray(1); gl.vertexAttribPointer(1, 4, gl.UNSIGNED_SHORT, true, 20, 8); gl.vertexAttribDivisor(1, 1);
      gl.enableVertexAttribArray(2); gl.vertexAttribIPointer(2, 2, gl.UNSIGNED_SHORT, 20, 16); gl.vertexAttribDivisor(2, 1);
      var t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, pc.img);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      return { vao: vao, n: pc.bin.byteLength / 20, tex: t };
    });
    gl.bindVertexArray(null);
    gl.useProgram(PR);
    gl.uniform1f(U('uW'), meta.W); gl.uniform1f(U('uH'), meta.H); gl.uniform1f(U('uPad'), meta.pad);
    gl.uniform1f(U('uWmax'), meta.wmax); gl.uniform1f(U('uTmax'), meta.tmax);
    gl.useProgram(Q); gl.uniform1i(UQ('C'), 0); gl.uniform1i(UQ('C2'), 1); gl.uniform1f(UQ('P'), P); gl.uniform1f(UQ('FIM'), FIM);
    var n = T.length;
    return {
      P: P, n: n,
      desenha: function (t, dpr) {
        var r = cv.getBoundingClientRect(); dpr = Math.min(dpr || 1, 2);
        var W = op.tam ? op.tam[0] : Math.max(2, Math.round(r.width * dpr)), H = op.tam ? op.tam[1] : Math.max(2, Math.round(r.height * dpr));
        if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
        var i = Math.floor(t / P) % n, s = t - Math.floor(t / P) * P, c = T[i];
        gl.viewport(0, 0, W, H);
        gl.disable(gl.BLEND);
        gl.useProgram(Q); gl.bindVertexArray(qv);
        gl.uniform1f(UQ('s'), s); gl.uniform2f(UQ('res'), W, H); gl.uniform1f(UQ('modo'), 0);
        gl.uniform1f(UQ('tem'), (t >= P || op.laco) ? 1 : 0);
        gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, T[(i + n - 1) % n].tex);
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, c.tex);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
        {
          gl.useProgram(PR); gl.uniform1f(U('uT'), s); gl.uniform2f(U('uRes'), W, H);
          gl.bindVertexArray(c.vao); gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 22, c.n);
        }
        gl.useProgram(Q); gl.bindVertexArray(qv); gl.uniform1f(UQ('modo'), 1);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      }
    };
  };
})();
