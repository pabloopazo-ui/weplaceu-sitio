/* WEPLACEU · comportamiento del sitio v3 (sitio/assets/sitio.js). Lo copia build_sitio_wpu.py: se edita aquí. */
(function(){
  var raiz = document.documentElement;
  raiz.classList.add('js');
  /* ?estatico: sin animaciones y con todas las fotos cargadas, para capturas y pruebas */
  var ESTATICO = /estatico/.test(location.search);
  if(ESTATICO){ raiz.classList.add('estatico');
    document.querySelectorAll('img[loading="lazy"]').forEach(function(i){ i.loading = 'eager'; }); }
  var REDUCIDO = ESTATICO || window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* animaciones SVG (rutas de la torre de control): quietas si la persona pidió menos movimiento */
  if(REDUCIDO) document.querySelectorAll('svg').forEach(function(v){ if(v.pauseAnimations) v.pauseAnimations(); });

  /* ---------- barra de progreso de lectura y cabecera que se compacta ---------- */
  var barra = document.querySelector('.progreso'), nav = document.querySelector('.nav'), pend = false;
  function alHacerScroll(){ pend = false;
    var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
    if(barra) barra.style.setProperty('--p', max > 0 ? (h.scrollTop / max).toFixed(4) : 0);
    if(nav) nav.classList.toggle('scrolled', h.scrollTop > 40); }
  window.addEventListener('scroll', function(){ if(!pend){ pend = true; requestAnimationFrame(alHacerScroll); } }, {passive: true});
  alHacerScroll();

  /* ---------- menú del teléfono ---------- */
  var ham = document.getElementById('hamburger'), dr = document.getElementById('drawer'), ov = document.getElementById('overlay');
  function abrirMenu(){ dr.classList.add('open'); ov.classList.add('open'); ham.setAttribute('aria-expanded','true'); }
  function cerrarMenu(){ dr.classList.remove('open'); ov.classList.remove('open'); ham.setAttribute('aria-expanded','false'); }
  if(ham && dr){
    ham.addEventListener('click', abrirMenu); ov.addEventListener('click', cerrarMenu);
    document.getElementById('drawerClose').addEventListener('click', cerrarMenu);
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape') cerrarMenu(); });
  }

  /* ---------- carrusel de la portada: cada 3 s, barra que se llena, pausa con mouse o foco ---------- */
  var hero = document.querySelector('.hero');
  if(hero){
    var sl = hero.querySelectorAll('.hero-slide'), dots = hero.querySelectorAll('.hero-dot'), i = 0, t = null, pausado = false;
    var btnP = hero.querySelector('.hero-pausa');
    function ver(n){ i = (n + sl.length) % sl.length;
      sl.forEach(function(s, k){ s.classList.toggle('on', k === i); s.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
      dots.forEach(function(d, k){ d.setAttribute('aria-current', 'false'); void d.offsetWidth; if(k === i) d.setAttribute('aria-current', 'true'); }); }
    function correr(){ clearInterval(t); hero.classList.toggle('pausado', pausado || REDUCIDO);
      if(!pausado && !REDUCIDO) t = setInterval(function(){ ver(i + 1); }, 3000); }
    function detener(){ clearInterval(t); hero.classList.add('pausado'); }
    dots.forEach(function(d, k){ d.addEventListener('click', function(){ ver(k); correr(); }); });
    hero.addEventListener('mouseenter', detener);
    hero.addEventListener('mouseleave', correr);
    hero.addEventListener('focusin', detener);
    if(btnP){ if(REDUCIDO) btnP.hidden = true;
      btnP.addEventListener('click', function(){ pausado = !pausado; btnP.textContent = pausado ? 'Reanudar' : 'Pausar'; btnP.setAttribute('aria-pressed', pausado); correr(); }); }
    ver(0); correr();
  }

  /* ---------- preguntas frecuentes ---------- */
  document.querySelectorAll('.faq-q').forEach(function(q){
    q.addEventListener('click', function(){ q.setAttribute('aria-expanded', q.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'); });
  });

  /* ---------- aparición al hacer scroll: escalonada dentro de cada grilla ---------- */
  document.querySelectorAll('.g3,.g4,.fotos,.gal,.lineas,.ans-grid,.cifras,.pasos,.chips').forEach(function(g){
    Array.prototype.forEach.call(g.children, function(c, k){ c.style.setProperty('--i', k % 8); });
  });
  function contar(el){
    el.querySelectorAll('[data-cuenta]').forEach(function(n){
      var fin = parseInt(n.dataset.cuenta, 10), suf = n.dataset.suf || '', ini = null;
      if(REDUCIDO){ n.textContent = fin + suf; return; }
      function paso(ts){ if(!ini) ini = ts; var p = Math.min((ts - ini) / 1400, 1);
        n.textContent = Math.round(fin * (1 - Math.pow(1 - p, 3))).toLocaleString('es-CL') + suf; if(p < 1) requestAnimationFrame(paso); }
      requestAnimationFrame(paso);
    });
  }
  var obs = document.querySelectorAll('.reveal,.pasos,.cifras');
  var io = ('IntersectionObserver' in window && !ESTATICO) ? new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); contar(e.target); io.unobserve(e.target); } });
  }, {threshold: .12, rootMargin: '0px 0px -40px 0px'}) : null;
  obs.forEach(function(el){ if(io) io.observe(el); else { el.classList.add('in'); contar(el); } });

  /* ---------- torre de control en vivo: eventos que van entrando (ilustración, no datos reales) ---------- */
  document.querySelectorAll('[data-feed]').forEach(function(feed){
    var ev = JSON.parse(feed.getAttribute('data-feed')), k = 0, max = 4;
    function poner(){ var e = ev[k % ev.length]; k++;
      var d = document.createElement('div'); d.className = 'tv-ev';
      d.innerHTML = '<span class="ic" aria-hidden="true">' + e[0] + '</span><span><b>' + e[1] + '</b><small>' + e[2] + '</small></span>';
      feed.insertBefore(d, feed.firstChild);
      while(feed.children.length > max) feed.removeChild(feed.lastChild); }
    for(var n = 0; n < max; n++) poner();
    if(!REDUCIDO) setInterval(poner, 2600);
  });

  /* ---------- medición: los dos eventos que ya escucha GTM-KD4XDXL3 (GA4 «contacto» y Meta Lead / Contact) ----------
     Mismos nombres que en el sitio actual. Si GTM no cargó (revisión local), el empuje queda en dataLayer y no sale a ninguna parte. */
  window.dataLayer = window.dataLayer || [];
  document.addEventListener('click', function(e){
    var t = e.target && e.target.closest ? e.target.closest('a[href*="wa.me"], a[href*="api.whatsapp.com"]') : null;
    if(t) window.dataLayer.push({event: 'contacto_whatsapp'});
  }, true);

  /* ---------- formulario (en la revisión no envía nada; al publicar lo reemplaza el envío a HubSpot) ----------
     Al publicar, «contacto_formulario» se empuja cuando HubSpot confirma el envío, no al apretar el botón. */
  var f = document.getElementById('formContacto');
  if(f) f.addEventListener('submit', function(e){ e.preventDefault();
    if(!f.reportValidity()) return;
    window.dataLayer.push({event: 'contacto_formulario'});
    document.getElementById('formOk').style.display = 'block'; f.reset(); });

  /* ---------- revisión: notas, notas en la página y portada partida (versión B). Se quitan al publicar ---------- */
  var pan = document.getElementById('revPanel');
  if(pan){
    document.querySelectorAll('[data-rev-abrir]').forEach(function(b){ b.addEventListener('click', function(){ pan.classList.add('open'); pan.querySelector('.cerrar').focus(); }); });
    pan.querySelector('.cerrar').addEventListener('click', function(){ pan.classList.remove('open'); });
    pan.addEventListener('click', function(e){ if(e.target === pan) pan.classList.remove('open'); });
  }
  var vn = document.getElementById('verNotas');
  if(vn) vn.addEventListener('click', function(){ var on = document.body.classList.toggle('ver-notas');
    vn.setAttribute('aria-pressed', on); vn.textContent = vn.textContent.replace(/^(Mostrar|Ocultar)/, on ? 'Ocultar' : 'Mostrar'); });
  var vb = document.getElementById('verB');
  if(vb){
    if(/version-b/.test(location.hash)) document.body.classList.add('version-b');
    function etiqueta(){ var on = document.body.classList.contains('version-b');
      vb.setAttribute('aria-pressed', on); vb.textContent = on ? 'Ver portada con carrusel (versión A)' : 'Ver portada partida en dos (versión B)'; }
    vb.addEventListener('click', function(){ document.body.classList.toggle('version-b'); etiqueta(); window.scrollTo(0, 0); });
    etiqueta();
  }

  var y = document.getElementById('anio'); if(y) y.textContent = new Date().getFullYear();
})();
