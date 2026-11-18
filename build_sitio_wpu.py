"""Sitio de WEPLACEU · v3: sitio completo, dinámico y con SEO desarrollado, para revisión del cliente.

v3 (14-nov-2026, pedido de Pablo): más movimiento y capa tecnológica, los títulos que WEPLACEU ya puso
(maqueta de Carlos y encabezados del sitio actual) y SEO completo: palabras clave por página, datos
estructurados, migas, Open Graph, sitemap.xml, robots.txt y llms.txt.

Cada página es su propio archivo; estilos, código e imágenes son compartidos. Base de contenido: la maqueta
de Carlos (1 CLIENTES ACTIVOS/WEPLACEU/sitio_web/maqueta_cliente/WEPLACEU_Maqueta_Con_Textos_e_Imagenes.html) y la reunión «GRILLA DE CONTENIDOS WPU» del
13-nov-2026. Fotos: las de WEPLACEU (presentación y biblioteca pública de weplaceu.cl).

El sitio no se edita a mano: manda este generador. Imágenes: prep_imagenes.py → img/.
Uso: python3 build_sitio_wpu.py   → sitio/ y WPU_Sitio_v3.zip
"""
import hashlib, html, json, pathlib, re, shutil, sys, zipfile
from PIL import Image

AQUI = pathlib.Path(__file__).resolve().parent
VERSION, FECHA, FECHA_ISO = "v3.1", "15-nov-2026", "2026-11-15"
PUBLICADO_ISO = "2026-11-14"   # primera publicación de los artículos: no se mueve con cada versión
# v3.1 (15-nov-2026, QA de Pablo «mejora todo lo que se pueda»): fuentes servidas por el propio sitio (sin pedir nada
# a Google antes de pintar), un tamaño intermedio de 1440 px en cada foto grande y los derivados re-codificados desde el
# original, y en privacidad el canal real para ejercer derechos (el sitio no publica correo todavía).
OUT = AQUI / "sitio"
ZIP = AQUI / f"WPU_Sitio_{VERSION}.zip"
DOM = "https://weplaceu.cl"
# Verificación del dominio en Meta (Business Manager), pedida por Pablo el 14-nov-2026. Va también en vivo en weplaceu.cl (WPCode, encabezado).
MARCA = "WEPLACEU"                     # como lo escribe WEPLACEU en su maqueta y en su sitio actual
TORRE = "WEPLACEU Control Tower"        # título de la maqueta de Carlos
WA_NUM, WA_TXT = "56965351601", "+56 9 6535 1601"
# Ubicación: Pronto Cowork, Mallplaza Norte (prontocowork.cl/mall-plaza-norte, leído el 14-nov-2026).
# Coordenadas: nodo «Integramédica», Av. Américo Vespucio 1737, OpenStreetMap (n1278732757), la torre donde está el cowork.
DIR_CALLE, DIR_DETALLE, DIR_COMUNA = "Av. Américo Vespucio 1737", "Piso 8, Torre Integramédica · Mallplaza Norte", "Huechuraba"
DIR_CORTA = f"{DIR_CALLE}, piso 8, {DIR_COMUNA}"
GEO_LAT, GEO_LNG = -33.36627, -70.67834
MAPA_URL = f"https://www.google.com/maps/search/?api=1&query={GEO_LAT},{GEO_LNG}"
MAPA_RUTA = f"https://www.google.com/maps/dir/?api=1&destination={GEO_LAT},{GEO_LNG}"
MAPA_EMBED = f"https://www.google.com/maps?q={GEO_LAT},{GEO_LNG}&z=17&hl=es&output=embed"
IG_HANDLE = "weplaceu.cl"
IG_URL = f"https://www.instagram.com/{IG_HANDLE}/"   # el WhatsApp que hoy publica el sitio (cambiado el 12-nov-2026)
# ---- Etiquetas de medición (14-nov-2026). Todas viven dentro de GTM; el sitio solo carga el contenedor. ----
# GTM-KD4XDXL3 (cuenta GTM «Precisión Agencia», contenedor 286079629) lleva: GA4 G-QYT834NZXB + evento «contacto»,
# HubSpot (Hub 52288874) y el píxel de Meta 1170353078726123 (portafolio WEPLACEU), todo condicionado al consentimiento.
# Detalle completo: 1 CLIENTES ACTIVOS/WEPLACEU/Etiquetas_WPU.md.
GTM_ID = "GTM-KD4XDXL3"
GSC_VERIF = "EofH6V3YYczl4vKEFD9AC8Sy2UuP-iBLiHDAv20jA0U"    # Search Console, propiedad https://weplaceu.cl/ (copiado del sitio publicado)
FB_VERIF = "ue7kqd6rtg34xoeqadmiqa4cxuofab"                  # verificación del dominio en el portafolio WEPLACEU de Meta
HOSTS_MEDIDOS = ("weplaceu.cl", "www.weplaceu.cl")           # GTM solo carga en el dominio real: la revisión local o el ZIP no ensucian GA4 ni Meta
# Consentimiento por defecto denegado antes de GTM. Lee las cookies del aviso Complianz que ya usa weplaceu.cl (mismo script que el
# encabezado de WPCode). Sin aviso instalado, todo queda denegado y GA4, HubSpot y Meta no disparan: es el valor seguro.
CONSENT_JS = """window.dataLayer=window.dataLayer||[];
(function(){
  function gtag(){window.dataLayer.push(arguments);}
  function ck(n){var m=document.cookie.match(new RegExp('(?:^|; )'+n+'=([^;]*)'));return m?m[1]:'';}
  function estado(){
    var s=ck('cmplz_statistics')==='allow', m=ck('cmplz_marketing')==='allow';
    return {analytics_storage:s?'granted':'denied',ad_storage:m?'granted':'denied',ad_user_data:m?'granted':'denied',ad_personalization:m?'granted':'denied'};
  }
  var ini=estado();
  ini.functionality_storage='granted';ini.security_storage='granted';ini.wait_for_update=500;
  gtag('consent','default',ini);
  var ultimo=JSON.stringify(estado());
  function actualizar(){
    setTimeout(function(){
      var e=estado(),j=JSON.stringify(e);
      if(j===ultimo){return;}
      ultimo=j;
      gtag('consent','update',e);
      dataLayer.push({event:'consentimiento_actualizado',consentimiento_analitica:e.analytics_storage});
    },150);
  }
  ['cmplz_status_change','cmplz_fire_categories','cmplz_enable_category','cmplz_revoke'].forEach(function(n){document.addEventListener(n,actualizar);});
})();"""
GTM_JS = ("if(" + " || ".join(f"location.hostname==='{h}'" for h in HOSTS_MEDIDOS) + "){"
          "(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
          "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
          f"j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{GTM_ID}');}}")
ETIQUETAS_HEAD = (f'<meta name="google-site-verification" content="{GSC_VERIF}">\n'
                  f'<meta name="facebook-domain-verification" content="{FB_VERIF}">\n'
                  f'<!-- Consentimiento y Google Tag Manager ({GTM_ID}). Ver Etiquetas_WPU.md -->\n'
                  f'<script>\n{CONSENT_JS}\n</script>\n<script>{GTM_JS}</script>')
ETIQUETAS_BODY = (f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}" height="0" width="0" '
                  f'style="display:none;visibility:hidden" title="Google Tag Manager"></iframe></noscript>')
# Fuentes propias (OFL): Poppins e IBM Plex Mono, subconjunto latino, bajadas de Google Fonts el 15-nov-2026 a nucleo/fuentes/.
FUENTES = [("Poppins", w, f"poppins-{w}-latin.woff2") for w in (400, 600, 700, 800)] + [("IBM Plex Mono", w, f"ibm-plex-mono-{w}-latin.woff2") for w in (500, 600)]
RANGO_LATIN = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
FUENTES_CSS = "".join(f"@font-face{{font-family:'{f}';font-style:normal;font-weight:{w};font-display:swap;src:url(fuentes/{a}) format('woff2');unicode-range:{RANGO_LATIN}}}\n" for f, w, a in FUENTES)
PRECARGA_FUENTES = ("poppins-400-latin.woff2", "poppins-800-latin.woff2")   # texto corrido y títulos: lo primero que se pinta
CSS = FUENTES_CSS + (AQUI / "nucleo" / "sitio.css").read_text(encoding="utf-8")
JS = (AQUI / "nucleo" / "sitio.js").read_text(encoding="utf-8")
SELLO = hashlib.md5((CSS + JS).encode()).hexdigest()[:8]   # un cambio llega al navegador sin pasar por la caché
esc = html.escape

# ------------------------------------------------------------------ imágenes: nombre interno → nombre de archivo para buscadores
TAM = {p.stem: Image.open(p).size for p in (AQUI / "img").iterdir() if p.suffix in (".webp", ".png")}
SEO_IMG = {
    "patio_flota": "patio-camiones-tractos-weplaceu", "tractos_puerto": "retiro-tractos-puerto-traslado-por-sus-propios-medios",
    "tractos_patio": "traslado-de-camiones-por-sus-propios-medios", "bus": "traslado-de-buses-por-sus-propios-medios",
    "aljibe": "traslado-camion-aljibe-carrocero", "bodega": "distribucion-retail-bodega-central-pallets",
    "bodega2": "bodega-racks-pallets-cross-docking", "bodega3": "pallets-listos-para-despacho-retail",
    "carga_anden": "carga-de-camion-en-anden-distribucion-b2b", "anden_bodega": "anden-bodega-despacho-carga",
    "anden": "camiones-distribucion-anden", "camiones_blancos": "flota-de-distribucion-b2b", "descarga": "carga-de-pallets-camion-distribucion",
    "camiones": "camiones-distribucion-bodega", "flota": "flota-camiones-nuevos", "panel": "control-tower-indicadores-servicio",
    "torre_mapa": "control-tower-monitoreo-gps-flota", "torre_estados": "control-tower-estado-rutas-ordenes",
    "torre_checklist": "control-tower-checklist-digital", "torre_entrega": "control-tower-prueba-de-entrega-fotos",
    "torre_patio": "gestion-de-patio-camiones", "unidades_tolvas": "coordinacion-carroceros-camiones-tolva",
    "unidades_puerto": "tracto-retiro-en-puerto", "logo_blanco": "logo-weplaceu-blanco", "logo_azul": "logo-weplaceu",
}
USADAS = set()

def archivo(nombre, ancho=None):
    ext = "png" if nombre.startswith("logo") else "webp"
    return f'{SEO_IMG.get(nombre, nombre)}{f"-{ancho}" if ancho else ""}.{ext}'

# Tamaños derivados (v3.1): 960 y, si el original pasa de 1640, también 1440. Se re-codifican desde el original al
# escribir sitio/ (calidad 82); el original queda en calidad 88, como pidió Pablo el 14-nov. Una pantalla de 1366 px
# baja la de 1440 en vez de la de 1920.
DERIVADOS, CALIDAD_DERIVADA = (960, 1440), 82
def anchos(nombre):
    if f"{nombre}-960" not in TAM:
        return []
    return [a for a in DERIVADOS if a == 960 or TAM[nombre][0] > a + 200]
def srcset(nombre):
    return ", ".join([f"@/img/{archivo(nombre, a)} {a}w" for a in anchos(nombre)] + [f"@/img/{archivo(nombre)} {TAM[nombre][0]}w"])

def img(nombre, alt, cls="", eager=False, sizes="(max-width: 760px) 100vw, 50vw"):
    assert nombre in TAM, f"falta la imagen {nombre}"
    USADAS.add(nombre)
    w, h = TAM[nombre]
    c = f' class="{cls}"' if cls else ""
    carga = ' fetchpriority="high"' if eager else ' loading="lazy"'
    src = ""
    if anchos(nombre):
        src = f' srcset="{srcset(nombre)}" sizes="{sizes}"'
    return f'<img src="@/img/{archivo(nombre)}"{src} alt="{esc(alt)}" width="{w}" height="{h}"{c}{carga} decoding="async">'

def wa(txt=f"Hola, quiero cotizar un servicio con {MARCA}."):
    from urllib.parse import quote
    return f"https://wa.me/{WA_NUM}?text={quote(txt)}"

def rev(txt):
    return f'<p class="rev"><b>Para revisar:</b> {txt}</p>'

# Íconos propios de WEPLACEU (14-nov): dibujados para su operación, no un set genérico.
# Grilla de 32, trazo 1,7. Tres capas: líneas (color del texto), «a» = relleno de acento,
# «t» = trazo de acento y «d» = ruta punteada que avanza cuando la tarjeta entra en pantalla.
ICONOS = {
    # vehículos que se trasladan por sus propios medios (vista lateral)
    "camion": '<path d="M2 8h16v12H2z"/><path d="M18 11.5h5.5l4.5 5V20H18z"/><path class="a" d="M20 13.5h3l2.6 3H20z"/><path d="M2 20h26"/><circle cx="7" cy="23" r="2.4"/><circle cx="13" cy="23" r="2.4"/><circle cx="24" cy="23" r="2.4"/>',
    "bus": '<rect x="2.5" y="6.5" width="26.5" height="14.5" rx="2.5"/><path class="a" d="M5 9.5h5v4H5zM12 9.5h5v4h-5zM19 9.5h4.5v4H19z"/><path d="M26 9.5V21M2.5 16.5h23.5"/><circle cx="8.5" cy="23" r="2.4"/><circle cx="22.5" cy="23" r="2.4"/>',
    "maquinaria": '<rect x="2.5" y="21" width="17" height="5.5" rx="2.75"/><circle cx="6" cy="23.75" r=".9"/><circle cx="16" cy="23.75" r=".9"/><path d="M5 21v-7.5h7.5l2.5 4.5v3"/><path class="a" d="M7 15.5h4v3.5H7z"/><path d="M13.5 14.5L20 8l6 3.5"/><path class="a" d="M26 11.5l2.5 5.5-4.5 1.2z"/>',
    "liviano": '<path d="M6.6 20.5H3v-4.2l3.2-1.1 3.6-4.7h9.8l4.3 4.7 4.6 1.1v4.2h-2.1M11.4 20.5h9.2"/><path class="a" d="M10.8 12.3h4v3.2H8.4zM16.6 12.3h2.3l2.8 3.2h-5.1z"/><circle cx="9" cy="20.5" r="2.4"/><circle cx="23" cy="20.5" r="2.4"/>',
    # personas y operación
    "conductor": '<circle cx="16" cy="16" r="12"/><circle class="a" cx="16" cy="16" r="3.2"/><path d="M4.4 14h8.4M19.2 14h8.4M16 19.2V28"/>',
    "equipo": '<circle cx="10" cy="9" r="4"/><path d="M3 27v-3a7 7 0 0 1 14 0v3"/><path d="M19 15h7v7.5h-7z"/><path class="a" d="M26 18h2.6l1.9 2.5v2H26z"/><circle cx="21.5" cy="25" r="1.6"/><circle cx="27.5" cy="25" r="1.6"/>',
    "terreno": '<path d="M5.5 21.5a10.5 10.5 0 0 1 21 0"/><path class="a" d="M3 21.5h26v3.5H3z"/><path d="M13.5 11.3v6M18.5 11.3v6M13.5 11.3a10.5 10.5 0 0 1 5 0"/>',
    "red": '<circle cx="7" cy="8" r="3.2"/><circle cx="25" cy="8" r="3.2"/><circle class="a" cx="16" cy="24" r="4.2"/><path d="M10.2 8h11.6M8.6 10.9l5.2 9.4M23.4 10.9l-5.2 9.4"/>',
    # seguimiento y respaldo
    "gps": '<path class="d" d="M2.5 28c5-3.5 9 .5 14-2.5s6.5-5.5 13-4.5"/><path d="M16 21s7-6 7-11.5a7 7 0 0 0-14 0C9 15 16 21 16 21z"/><circle class="a" cx="16" cy="9.5" r="2.7"/>',
    "plataforma": '<rect x="2.5" y="4.5" width="27" height="17.5" rx="2"/><path d="M12 28h8M16 22v6"/><path class="d" d="M6.5 18c4-1 4.5-6.5 9-6s5 3 10-3"/><circle class="a" cx="25.5" cy="9" r="2"/>',
    "check": '<rect x="6" y="5" width="20" height="24" rx="2"/><rect class="a" x="12" y="3" width="8" height="4" rx="1"/><path class="t" d="M9.8 13.2l2 2 3.4-3.4M9.8 21.2l2 2 3.4-3.4"/><path d="M18.5 13.8h4.5M18.5 21.8h4.5"/>',
    "doc": '<rect x="8" y="2.5" width="16" height="27" rx="3"/><path d="M13.5 25.5h5"/><path class="t" d="M10.8 17.5c1.6-3.8 2.8-3.8 2.8-1.2s1.4 2.2 2.4-.6 2-2.4 2.3-.2 1.3 1.2 2.9-.8"/><path d="M11 20.5h10"/>',
    "historial": '<path d="M2.5 9h20M2.5 16h20M6 9v7M12.5 9v7M19 9v7"/><path d="M4.5 5.5v3.5M4.5 16v3.5M17 5.5v3.5M17 16v3.5" stroke-width="2.6"/><circle class="a" cx="23.5" cy="22.5" r="6.5"/><path d="M23.5 19.2v3.4l2.4 1.5"/>',
    "costo": '<path d="M8 3h16v26l-3-2-2.7 2-2.6-2-2.7 2-2.7-2L8 29z"/><path d="M12 9.5h8M12 13.5h8"/><rect class="a" x="11" y="18.5" width="10" height="3.5" rx=".6"/>',
    "estrella": '<path d="M4 5.5h24v15.5H13.5L7.5 26v-5H4z"/><path class="a" d="M16 8.6l1.45 3 3.25.35-2.4 2.25.7 3.25L16 15.85l-3 1.6.7-3.25-2.4-2.25 3.25-.35z"/>',
    "grafico": '<path d="M4.5 23a11.5 11.5 0 0 1 23 0"/><path d="M8.2 15l1.6 1.4M16 11v2.2M23.8 15l-1.6 1.4M3 27h26"/><path class="t" d="M16 23l6.2-7"/><circle class="a" cx="16" cy="23" r="2.4"/>',
    "escudo": '<path d="M16 3l11 4v8c0 7-5 11.5-11 14C10 26.5 5 22 5 15V7z"/><path class="t" d="M11 16l3.5 3.5L21.5 12.5"/>',
    # carga y lugares
    "caja": '<path d="M5 9.5h10v8.5H5zM17 9.5h10v8.5H17z"/><path class="a" d="M11 3.5h10v6H11z"/><path d="M3 18h26v3H3zM5 21v5M16 21v5M27 21v5M3 26h26"/>',
    "reloj": '<circle cx="16" cy="16" r="12"/><path class="a" d="M16 4a12 12 0 0 1 12 12H16z"/><path d="M16 9v7l5 3"/>',
    "patio": '<path d="M3 13.5l13-8.5 13 8.5V28H3z"/><path class="a" d="M7 18.5h6V28H7z"/><path d="M19 18.5h6V28h-6zM19 21.5h6M19 24.5h6M10 9.5h12"/>',
    "ruta": '<circle cx="6" cy="25" r="3"/><path class="d" d="M9 24c6-1 4-8 10-9s5 2 6.5-3.5"/><path class="a" d="M26 11.5s4-3.5 4-6.5a4 4 0 0 0-8 0c0 3 4 6.5 4 6.5z"/>',
    "origen": '<path d="M7 28V8h4v20M3 28h26M7 8h20M11 8l5-5M22 8v7"/><path class="a" d="M17 15h10v6.5H17z"/><path d="M20.3 15v6.5M23.7 15v6.5"/>',
    "destino": '<path d="M10 28.5V4"/><path class="a" d="M10 4.5h15l-3.5 4.5 3.5 4.5H10z"/><path d="M5 28.5h10"/>',
    "maestranza": '<path d="M20.5 3.5a6.5 6.5 0 0 0-6 8.8L4.4 22.4a2.6 2.6 0 0 0 3.7 3.7l10.1-10.1A6.5 6.5 0 0 0 27 9.5l-3.6 3.6-3.6-1-1-3.6z"/><circle class="a" cx="6.3" cy="24.2" r="1.3"/>',
}

def svg_ico(n):
    return f'<svg class="ico" viewBox="0 0 32 32" aria-hidden="true" focusable="false">{ICONOS[n]}</svg>'

def icono(n):
    return f'<span class="icono" aria-hidden="true">{svg_ico(n)}</span>'

# ------------------------------------------------------------------ bloques
def faq(items, titulo="Lo que más nos preguntan.", claro=True):
    fs = "".join(f'<div class="faq-item"><button class="faq-q" type="button" aria-expanded="false"><span>{esc(q)}</span><span class="ic" aria-hidden="true">+</span></button><div class="faq-a"><p>{esc(a)}</p></div></div>' for q, a in items)
    return f'<section class="section-pad{" claro" if claro else ""}"><div class="wrap"><div class="sec-title center reveal"><span class="eyebrow">Preguntas frecuentes</span><h2>{titulo}</h2></div><div class="faq-list">{fs}</div></div></section>'

def cta(titulo="Cuéntanos qué necesita tu empresa", texto="Ya sea para el traslado de unidades, transporte de carga, distribución B2B o una demostración de Control Tower, podemos evaluar una propuesta ajustada a tu operación.", boton="Cotizar"):
    return f'''<section class="section-pad"><div class="wrap"><div class="cta-band reveal zoom">
<div><span class="eyebrow light">Conversemos</span><h2>{titulo}</h2><p>{texto}</p></div>
<div class="btns"><a class="btn btn-teal" href="@/contacto.html">{boton} →</a><a class="btn btn-ghost" href="{wa()}" target="_blank" rel="noopener">Escribir por WhatsApp</a></div>
</div></div></section>'''

def pg_hero(crumbs, eyebrow, h1, lead, foto, alt, extra=""):
    migas = " › ".join(f'<a href="@/{u}">{esc(n)}</a>' if u else esc(n) for n, u in crumbs)
    return f'''<section class="pg-hero">{img(foto, alt, eager=True, sizes="100vw")}<div class="wrap">
<nav class="crumbs" aria-label="Ruta de navegación">{migas}</nav>
<span class="eyebrow light">{eyebrow}</span><h1>{h1}</h1><p class="lead">{lead}</p>{extra}
</div><div class="ruta-deco" aria-hidden="true"></div></section>'''

def fotos(items):
    return '<div class="fotos">' + "".join(f'<figure class="reveal zoom">{img(n, a, sizes="(max-width: 760px) 100vw, 33vw")}<figcaption>{esc(c)}</figcaption></figure>' for n, a, c in items) + "</div>"

def tarjetas(items, grid="g3"):
    out = []
    for it in items:
        ic, k, t, d = it if len(it) == 4 else (None, *it)
        out.append(f'<div class="card reveal">{icono(ic) if ic else ""}{f"<span class=k>{k}</span>" if k else ""}<h3>{t}</h3><p>{d}</p></div>')
    return f'<div class="{grid}">' + "".join(out) + "</div>"

def pasos(items):
    return f'<div class="pasos" style="--n:{len(items)}">' + "".join(f'<div class="paso reveal"><h3>{t}</h3><p>{d}</p></div>' for t, d in items) + "</div>"

CINTA = ["Traslado por sus propios medios", "Distribución a retail", "Cross-docking", "Checklist digital", "Monitoreo GPS", "Prueba de entrega digital",
         "Historial por chasis", "Logística integral", "Gestión logística inteligente", "Control Tower"]

def cinta():
    items = "".join(f"<span>{esc(x)}</span>" for x in CINTA)
    return f'<div class="cinta" aria-hidden="true"><div class="cinta-track">{items}{items}</div></div>'

CIFRAS = '''<div class="cifra"><strong data-cuenta="90" data-suf="+">90+</strong><span>Colaboradores en la operación</span></div>
<div class="cifra"><strong data-cuenta="700" data-suf="+">700+</strong><span>Traslados mensuales</span></div>
<div class="cifra"><strong>Chile</strong><span>Cobertura de operaciones de alcance nacional</span></div>'''

FEED = [["check", "Checklist de retiro completado", "Unidad 04 · puerto · ahora"], ["ruta", "Unidad en ruta", "Hacia el carrocero · hace 1 min"],
        ["caja", "Pallets cargados", "Bodega central · hace 2 min"], ["doc", "Guía firmada y fotos recibidas", "Entrega en retail · hace 4 min"],
        ["destino", "Llegada a destino", "Sucursal en regiones · hace 6 min"], ["estrella", "Entrega evaluada por quien recibe", "Encuesta de satisfacción · hace 8 min"]]

def torre_viva():
    """Ilustración animada del seguimiento en línea: rutas, unidades en movimiento y eventos. No muestra datos reales."""
    nodos = [("Puerto", 70, 300), ("Carrocero", 235, 195), ("Concesionario", 400, 112), ("Sucursal en regiones", 540, 58),
             ("Bodega central", 92, 92), ("Retail", 420, 300), ("Retail", 556, 232)]
    rutas = ["M70,300 C150,282 172,214 235,195", "M235,195 C300,176 334,124 400,112", "M400,112 C462,100 500,72 540,58",
             "M92,92 C200,122 300,262 420,300", "M420,300 C482,290 520,252 556,232"]
    unidad = "M70,300 C150,282 172,214 235,195 C300,176 334,124 400,112 C462,100 500,72 540,58"
    carga = "M92,92 C200,122 300,262 420,300 C482,290 520,252 556,232"
    rejilla = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="380" stroke="rgba(255,255,255,.04)"/>' for x in range(0, 601, 40)) + \
              "".join(f'<line x1="0" y1="{y}" x2="600" y2="{y}" stroke="rgba(255,255,255,.04)"/>' for y in range(0, 381, 40))
    rs = "".join(f'<path class="ruta" d="{d}"/>' for d in rutas)
    ns = "".join(f'<circle class="nodo-pulso" cx="{x}" cy="{y}" r="7" style="animation-delay:{k*.35:.2f}s"/><circle class="nodo" cx="{x}" cy="{y}" r="7"/>'
                 f'<text class="nodo-txt" x="{x + (12 if x < 500 else -12)}" y="{y - 12}" text-anchor="{"start" if x < 500 else "end"}">{n}</text>' for k, (n, x, y) in enumerate(nodos))
    puntos = (f'<circle class="movil-dot" r="6"><animateMotion dur="10s" repeatCount="indefinite" path="{unidad}"/></circle>'
              f'<circle class="movil-dot" r="6"><animateMotion dur="8s" repeatCount="indefinite" path="{carga}"/></circle>'
              f'<circle class="movil-dot" r="6"><animateMotion dur="8s" begin="4s" repeatCount="indefinite" path="{carga}"/></circle>')
    feed = esc(json.dumps([[svg_ico(i), t, d] for i, t, d in FEED], ensure_ascii=False))
    return f'''<div class="torre-viva reveal zoom">
<div><div class="tv-barra"><span class="vivo">EN LÍNEA</span><span>{TORRE} · vista de seguimiento</span></div>
<div class="tv-mapa"><svg viewBox="0 0 600 380" role="img" aria-label="Ilustración: rutas de traslado y de distribución con unidades en movimiento">{rejilla}{rs}{ns}{puntos}</svg></div></div>
<div class="tv-lado"><div class="tv-barra"><span>Eventos del servicio</span></div><div class="tv-feed" data-feed="{feed}" aria-live="off"></div>
<div class="tv-estados"><div><b>GPS</b><span>Ubicación en línea</span></div><div><b>Fotos</b><span>Checklist</span></div><div><b>Firma</b><span>Prueba de entrega</span></div></div></div>
</div><p class="tv-nota">Ilustración del seguimiento en línea. Los eventos son de ejemplo, no datos reales.</p>'''

# ------------------------------------------------------------------ preguntas frecuentes (una sola fuente)
FAQ_GENERAL = [
    ("¿Qué es el traslado por sus propios medios?", "Es mover un camión, bus o vehículo manejándolo hasta su destino, sin subirlo a una cama baja ni a otro camión. Lo hacen nuestros conductores, con checklist al retirar, seguimiento GPS y entrega con respaldo fotográfico."),
    ("¿Qué es la distribución a retail B2B?", "Es llevar los productos de una marca desde su bodega central hasta los locales y centros de distribución del retail: supermercados, mejoramiento del hogar y canal ferretero. Trabajamos con carga paletizada y la cita que agenda la marca."),
    ("¿Qué es el cross-docking?", "Es recibir la carga en una bodega y despacharla en menos de 24 horas, sin almacenarla. Sirve cuando el producto debe llegar rápido y no conviene tenerlo días en un rack."),
    ("¿Cómo sé dónde va mi camión o mi carga?", f"Con {TORRE} ves en línea la ubicación, el estado de cada servicio, quién recibió, las fotos y el documento de entrega. No necesitas llamar al conductor ni pedir fotos por WhatsApp."),
]
FAQ_PROPIOS = [
    ("¿Qué vehículos trasladan?", "Camiones, tractos, buses, vehículos livianos y maquinaria que puede circular por sí misma."),
    ("¿Llegan a regiones?", "Sí. Trasladamos unidades dentro de Santiago y hacia sucursales y clientes en regiones."),
    ("¿Cómo sé que la unidad llegó sin daños?", f"Registramos un checklist con fotos al retirar y otro al entregar. Los ves en {TORRE} y puedes descargar el documento."),
    ("¿Quién paga el combustible del traslado?", "Depende de la operación. Lo dejamos definido en la cotización, junto con los viáticos."),
]
FAQ_DISTRIB = [
    ("¿Hacen despachos a domicilio?", "No. Distribuimos de empresa a empresa: desde la bodega de tu marca a locales y centros de distribución del retail."),
    ("¿Quién agenda la cita con el retail?", "La agenda tu empresa con cada cliente. Nosotros cargamos, cumplimos el horario y te dejamos el respaldo de la entrega."),
    ("¿Cómo sé si la carga se entregó?", f"En {TORRE} ves el estado, quién recibió, las fotos y la guía firmada, en línea."),
]
FAQ_CROSS = [
    ("¿En cuánto tiempo sale la carga?", "En menos de 24 horas desde que se recibe: el mismo día o al siguiente."),
    ("¿Es lo mismo que almacenaje?", "No. En el almacenaje la carga se guarda; en el cross-docking se recibe, se ordena por destino y sale."),
    ("¿Qué necesitan saber para cotizarlo?", "Volumen, frecuencia, destinos, horarios de cita y las instalaciones disponibles."),
]
FAQ_TORRE = [
    ("¿Tengo que instalar algo?", "No. Tu equipo entra desde el navegador con el usuario y la contraseña que le creamos."),
    ("¿Quién de mi empresa puede verla?", "Quien necesite seguir la operación: jefe de logística, de transporte o de patio. Cada uno con su usuario."),
    ("¿Puedo descargar el respaldo de una entrega?", "Sí. Cada prueba de entrega se descarga como documento, con fotos y datos de quien recibió."),
    ("¿Sirve para las dos unidades de negocio?", "Sí. La usamos en los traslados por sus propios medios y en la distribución a retail."),
]

# ------------------------------------------------------------------ blog
POSTS = [
    {"slug": "traslado-por-sus-propios-medios", "foto": "tractos_puerto", "tag": "Guía",
     "titulo": "Qué es el traslado de vehículos por sus propios medios y cuándo conviene",
     "seo": "Qué es el traslado por sus propios medios",
     "resumen": "En qué se diferencia del traslado en cama baja, qué revisa un checklist de retiro y qué respaldo deberías exigir al recibir.",
     "cuerpo": [
        ("p", "Trasladar un vehículo por sus propios medios quiere decir que un conductor lo maneja desde el origen hasta el destino. La unidad no viaja arriba de una cama baja ni dentro de otro camión: rueda por la carretera como lo hará cuando empiece a trabajar."),
        ("h2", "Cuándo se usa"),
        ("p", "Sirve para camiones, tractos y buses que ya pueden circular. Se usa para entregar unidades nuevas a concesionarios y clientes, para llevarlas a carroceros, maestranzas o revisiones técnicas, y para moverlas entre sucursales."),
        ("p", "Cuando la unidad no puede circular por sí misma, el traslado tiene que ir sobre otro equipo. Por eso la primera pregunta de una cotización es qué unidad se mueve y en qué estado está."),
        ("h2", "Qué incluye un buen servicio"),
        ("ul", ["Un conductor habilitado para el tipo de unidad y la ruta.", "Un checklist de retiro con fotos y observaciones, antes de partir.", "Seguimiento GPS durante el viaje.", "Una prueba de entrega con fotos, hora y quién recibió.", "Costos del viaje, como combustible y viáticos, definidos en la cotización."]),
        ("h2", "Qué exigir al recibir la unidad"),
        ("p", "El respaldo tiene que contar la historia completa del traslado. Pide el checklist de salida y el de llegada, con fotos fechadas, y compáralos. Si hay una diferencia, queda a la vista y tiene responsable."),
        ("p", f"En {MARCA} ese respaldo queda en {TORRE}: lo ves en línea y lo descargas como documento."),
     ], "rel": ["transporte-por-sus-propios-medios.html", "torre-de-control.html"]},
    {"slug": "cross-docking", "foto": "carga_anden", "tag": "Distribución",
     "titulo": "Cross-docking: recibir y despachar en menos de 24 horas",
     "seo": "Cross-docking: qué es y cómo despachar en menos de 24 h",
     "desc": "Qué es el cross-docking, en qué se diferencia del almacenaje y qué hay que definir para recibir y despachar carga en menos de 24 horas.",
     "resumen": "Qué es, en qué se diferencia del almacenaje y qué hay que definir para diseñarlo.",
     "cuerpo": [
        ("p", "El cross-docking es una forma de mover carga en que la bodega funciona como punto de paso. La mercadería llega, se recibe, se ordena por destino y sale en menos de 24 horas."),
        ("h2", "En qué se diferencia del almacenaje"),
        ("p", "En el almacenaje la carga se guarda en racks hasta que se pide. En el cross-docking no se acumula: entra y sale el mismo día o al siguiente. Lo que se busca es velocidad, no espacio."),
        ("h2", "Cuándo conviene"),
        ("p", "Conviene cuando el producto tiene que llegar rápido al retail o cuando varias cargas se juntan para salir en una misma ruta. También cuando la marca no quiere ocupar espacio propio en una carga que solo va de paso."),
        ("h2", "Qué hay que definir para diseñarlo"),
        ("ul", ["Volumen: cuántos pallets o bultos por día.", "Frecuencia: todos los días, algunos días o por temporada.", "Destinos y horarios de cita de cada cliente.", "Instalaciones disponibles para recibir y despachar."]),
        ("p", f"Con esos datos se diseña la operación. Y como en cualquier entrega, {TORRE} deja el respaldo de cada despacho."),
     ], "rel": ["cross-docking.html", "distribucion-retail-b2b.html"]},
    {"slug": "seguimiento-de-carga", "foto": "torre_mapa", "tag": "Tecnología",
     "titulo": "Cómo saber dónde va tu carga sin llamar al conductor",
     "seo": "Seguimiento de carga en línea: qué deberías poder ver",
     "resumen": "Qué información debería mostrarte tu proveedor de transporte en línea y por qué la guía firmada ya no basta.",
     "cuerpo": [
        ("p", "En muchas operaciones, saber dónde va un camión todavía significa llamar al conductor o al jefe de la empresa de transporte. Y para facturar hay que esperar la foto de la guía firmada por WhatsApp."),
        ("h2", "Lo que deberías poder ver"),
        ("ul", ["La ubicación de cada camión en un mapa, en línea.", "El estado de cada servicio: por salir, en ruta o entregado.", "Quién recibió, a qué hora, con firma y fotos.", "Un documento de entrega que puedas descargar.", "Indicadores del servicio, como tiempos de entrega."]),
        ("h2", "Por qué la guía firmada ya no basta"),
        ("p", "La guía en papel vuelve cuando vuelve el conductor y no muestra cómo llegó la carga. Una prueba de entrega digital queda disponible apenas se entrega, con fotos y datos de quien recibió. Tu equipo puede facturar sin esperar a nadie."),
        ("h2", f"Cómo lo hacemos en {MARCA}"),
        ("p", f"Usamos {TORRE} en las dos unidades de negocio. Tu equipo entra con su propio usuario, ve la operación en línea y descarga los respaldos que necesita."),
     ], "rel": ["torre-de-control.html", "distribucion-retail-b2b.html"]},
]

def blog_cards(posts, titulo="Guías para quien mueve flotas y carga.", eyebrow="Desde el blog", claro=True):
    grid = "g2" if len(posts) == 2 else "g3"
    cs = "".join(f'''<article class="post reveal"><a class="ph" href="@/blog/{p["slug"]}.html" tabindex="-1" aria-hidden="true">{img(p["foto"], "", sizes="(max-width: 760px) 100vw, 33vw")}</a><div class="body"><span class="tag">{p["tag"]}</span><h3><a href="@/blog/{p["slug"]}.html">{p["titulo"]}</a></h3><p>{p["resumen"]}</p><a class="go" href="@/blog/{p["slug"]}.html">Leer el artículo</a></div></article>''' for p in posts)
    return f'''<section class="section-pad{" claro" if claro else ""}"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">{eyebrow}</span><h2>{titulo}</h2></div>
<div class="{grid}">{cs}</div></div></section>'''

VISIBILIDAD = ["Programación y asignación digital de servicios.", "Monitoreo GPS y estados de avance.", "Checklist de retiro y recepción con fotografías.",
               "Pruebas de entrega digitales y archivo por chasis.", "Indicadores, reportes e historial auditable.", "Gestión de incidencias y mejora continua."]

# ------------------------------------------------------------------ páginas
def p_inicio():
    slides = [
        ("patio_flota", "Patio con camiones y tractos alineados", "Transporte · Logística · Tecnología",
         '<h1>Movemos tu operación. <em>Conectamos tu negocio.</em></h1>',
         f"En {MARCA} integramos transporte profesional, soluciones logísticas y tecnología para entregar un servicio confiable, eficiente y trazable a lo largo de Chile.",
         '<a class="btn btn-teal" href="#unidades">Conoce nuestros servicios</a><a class="btn btn-ghost" href="@/torre-de-control.html">Nuestra tecnología</a>'),
        ("bodega", "Bodega central con carga paletizada lista para distribución a retail", "Unidad 02 · Distribución a retail y B2B",
         '<p class="hero-t">Llevamos los productos de tu marca <em>desde tu bodega hasta la góndola.</em></p>',
         "Despachos paletizados a supermercados, mejoramiento del hogar y canal ferretero, con flota propia y prueba de entrega digital.",
         '<a class="btn btn-teal" href="@/distribucion-retail-b2b.html">Explorar esta unidad →</a>'),
        ("tractos_puerto", "Tractos nuevos en un puerto, listos para su traslado por sus propios medios", "Unidad 01 · Transporte de unidades",
         '<p class="hero-t">Camiones, buses y maquinaria: <em>traslado seguro de principio a fin.</em></p>',
         "Retiro en puerto o concesionario, inspección, traslado y entrega con respaldo fotográfico, a lo largo de Chile.",
         '<a class="btn btn-teal" href="@/transporte-por-sus-propios-medios.html">Explorar esta unidad →</a>'),
    ]
    sl = "".join(f'''<div class="hero-slide{" on" if k == 0 else ""}" role="group" aria-roledescription="diapositiva" aria-label="{k+1} de 3">{img(f, a, eager=(k == 0), sizes="100vw")}
<div class="wrap"><div class="hero-copy"><span class="eyebrow light">{e}</span>{t}<p class="lead">{l}</p><div class="btns">{b}</div></div></div></div>''' for k, (f, a, e, t, l, b) in enumerate(slides))
    dots = "".join(f'<button class="hero-dot" type="button" aria-label="Ver diapositiva {k+1}"></button>' for k in range(3))
    hero = f'''<section class="hero" aria-roledescription="carrusel" aria-label="Lo que hace {MARCA}">{sl}
<div class="hero-ctrl"><div class="wrap">{dots}<button class="hero-pausa" type="button" aria-pressed="false">Pausar</button></div></div><a class="bajar" href="#nosotros" aria-label="Bajar a la siguiente sección"></a></section>'''
    partida = f'''<section class="hero-partida" aria-label="Elige una unidad de negocio">
<div class="partida-top"><span class="eyebrow light">Transporte · Logística · Tecnología</span><h1 class="hero-t">Movemos tu operación. <em>Conectamos tu negocio.</em></h1></div>
<a class="mitad" href="@/transporte-por-sus-propios-medios.html">{img("tractos_patio", "Tractos alineados listos para su traslado", sizes="50vw")}<div class="in"><span class="eyebrow light">Unidad 01</span><h2>Transporte de unidades por sus propios medios</h2><p>Camiones, buses y maquinaria manejados por nuestros conductores hasta su destino.</p><span class="btn btn-teal">Explorar esta unidad →</span></div></a>
<a class="mitad" href="@/distribucion-retail-b2b.html">{img("bodega3", "Bodega con carga paletizada", sizes="50vw")}<div class="in"><span class="eyebrow light">Unidad 02</span><h2>Distribución a retail y B2B</h2><p>La carga de tu marca, de tu bodega a la góndola, con prueba de entrega digital.</p><span class="btn btn-teal">Explorar esta unidad →</span></div></a>
</section>'''
    movil = f'''<section class="hero-movil">{img("patio_flota", "Patio con camiones y tractos", eager=True, sizes="100vw")}<div class="in">
<span class="eyebrow light">Transporte · Logística · Tecnología</span>
<h1 class="hero-t">Movemos tu operación. <em>Conectamos tu negocio.</em></h1>
<div class="lineas-m">
<a class="linea-btn" href="@/transporte-por-sus-propios-medios.html"><span>Transporte de unidades por sus propios medios<small>Camiones, buses y maquinaria</small></span><span class="flecha" aria-hidden="true">→</span></a>
<a class="linea-btn" href="@/distribucion-retail-b2b.html"><span>Distribución a retail y B2B<small>De tu bodega a la góndola</small></span><span class="flecha" aria-hidden="true">→</span></a>
</div>
<div class="btns"><a class="btn btn-teal" href="@/contacto.html" style="flex:1">Cotizar tu servicio →</a></div>
</div></section>'''
    nosotros = f'''<section class="section-pad" id="nosotros"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Sobre nosotros</span><h2>Una empresa construida sobre la confianza y <em>la excelencia operacional</em></h2>
<p class="lead" style="margin-top:1rem">{MARCA} nació con el propósito de desarrollar servicios de transporte de alta calidad, basados en las necesidades de cada cliente, el respeto por nuestros colaboradores y el cuidado del medioambiente. Nuestra propuesta combina experiencia operacional, seguridad, compromiso e integridad con herramientas digitales que facilitan el control de cada servicio.</p>
<p class="compromiso"><b>Nuestro compromiso:</b> seguridad, confianza, experiencia, compromiso e integridad.</p>
<a class="go" href="@/nosotros.html" style="margin-top:.6rem">Conoce {MARCA}</a></div>
<div class="foto reveal der">{img("tractos_patio", "Tractos alineados en el patio, listos para su traslado")}</div>
</div><div class="wrap"><div class="cifras plano">{CIFRAS}</div>{rev("las cifras 90+ y 700+ vienen del sitio actual y de la oferta técnica de agosto. Confirmar que siguen vigentes antes de publicar.")}</div></section>'''
    u1 = ["Retiros desde puertos y centros logísticos.", "Traslados a maestranzas, carroceros y revisiones técnicas.", "Distribución a sucursales y clientes en regiones.", "Checklist, respaldo fotográfico y prueba de entrega (POD) digital."]
    u2 = ["Transporte de carga de distintos volúmenes.", "Distribución entre centros, sucursales y clientes empresariales.", "Coordinación de operaciones retail y B2B.", "Cross-docking: recepción y despacho en menos de 24 horas."]
    lis = lambda xs: "".join(f"<li>{x}</li>" for x in xs)
    unidades = f'''<section class="section-pad claro" id="unidades"><div class="wrap">
<div class="sec-title reveal"><span class="eyebrow">Líneas de negocio</span><h2>Dos unidades especializadas. <em>Un mismo estándar de servicio.</em></h2></div>
<div class="lineas">
<a class="linea reveal" href="@/transporte-por-sus-propios-medios.html"><div class="ph">{img("tractos_puerto", "Retiro de tractos en puerto para traslado por sus propios medios")}<span class="num">UNIDAD 01</span></div><div class="body">
<span class="tag">Transporte de unidades</span><h3>Transporte de unidades por sus propios medios</h3>
<p>Especialistas en traslado profesional de camiones, buses y maquinaria que puede circular por sus propios medios. Trabajamos con conductores calificados y protocolos de inspección, retiro, seguimiento y entrega.</p>
<ul class="check">{lis(u1)}</ul><span class="go">Explorar esta unidad</span></div></a>
<a class="linea reveal" href="@/distribucion-retail-b2b.html"><div class="ph">{img("bodega", "Bodega central con pallets para distribución a retail")}<span class="num">UNIDAD 02</span></div><div class="body">
<span class="tag">Retail, transporte de carga y logística B2B</span><h3>Distribución a retail y B2B</h3>
<p>Soluciones para el movimiento de mercaderías y el abastecimiento de empresas, con coordinación de despachos y visibilidad de la operación.</p>
<ul class="check">{lis(u2)}</ul><span class="go">Explorar esta unidad</span></div></a>
</div>{rev("títulos de la maqueta de Carlos. La unidad 02 se llama «Distribución a retail y B2B», como pidió Carlos en la reunión (1:13:22); su título original queda como bajada. La tercera línea, de consultoría, no está decidida: el acompañamiento va dentro de cada unidad.")}</div></section>'''
    porque = [("red", "01", "Vendemos la operación completa", "Nos hacemos cargo del servicio de punta a punta: conductor, traslado, seguimiento y respaldo de cada paso."),
              ("plataforma", "02", "Una sola plataforma", "GPS, checklist, fotos, guías firmadas e indicadores en el mismo lugar. Tu equipo deja de perseguir información."),
              ("equipo", "03", "Conductores y flota propios", "Seleccionamos y habilitamos a cada conductor según la operación. En distribución, la carga va en nuestra flota."),
              ("terreno", "04", "Acompañamiento en terreno", "Coordinamos a tus proveedores, medimos plazos y te proponemos mejoras. Trabajamos junto a tu equipo.")]
    porque_s = f'''<section class="section-pad"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Logística integral</span>
<h2>Detrás de cada traslado hay <em>una operación completa.</em></h2></div>{tarjetas(porque, "g4")}</div></section>'''
    torre = f'''<section class="section-pad dark" id="control-tower"><div class="wrap">
<div class="g2" style="align-items:start;margin-bottom:2.4rem"><div class="reveal izq"><span class="eyebrow">Tecnología transversal</span><h2>{TORRE}</h2>
<p class="lead" style="margin-top:1rem">Una plataforma tecnológica que integra planificación, asignación, trazabilidad, control documental y evidencia operacional. No se trata solamente de conocer dónde está una unidad: se trata de disponer de información para gestionar la operación completa, desde la solicitud hasta la entrega.</p></div>
<div class="reveal der"><h3 style="margin-bottom:.4rem">Visibilidad en cada etapa</h3><ul class="check">{lis(VISIBILIDAD)}</ul><a class="btn btn-teal" href="@/torre-de-control.html" style="margin-top:.6rem">Conoce Control Tower →</a></div></div>
{torre_viva()}</div></section>'''
    galeria = f'''<section class="section-pad"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Lo que movemos</span><h2>De tractos nuevos <em>a pallets de consumo masivo.</em></h2></div>
{fotos([("bus", "Bus eléctrico listo para su traslado por sus propios medios", "Buses"), ("tractos_patio", "Tractos alineados en un patio", "Camiones y tractos"), ("aljibe", "Camión aljibe terminado en el patio de un carrocero", "Camiones con equipamiento"),
        ("camiones_blancos", "Flota de distribución en el andén", "Flota de distribución"), ("carga_anden", "Carga de un camión en el andén de una bodega", "Carga en andén"), ("bodega2", "Bodega con racks y pallets", "Bodega y pallets")])}
</div></section>'''
    sectores = "".join(f'<a class="linea-btn" href="@/industrias.html#{i}"><span>{esc(t)}</span><span class="flecha" aria-hidden="true">→</span></a>' for i, t, *_ in SECTORES)
    industrias = f'''<section class="section-pad dark"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">A quién servimos</span><h2>Empresas que necesitan <em>que sus unidades y su carga lleguen.</em></h2>
<p class="lead" style="margin-top:1rem">Marcas, importadores, concesionarios, carroceros y empresas con flota, y las marcas que distribuyen sus productos al retail.</p>
<div class="btns"><a class="btn btn-teal" href="@/industrias.html">Ver industrias →</a></div></div>
<div class="reveal der" style="display:grid;gap:.7rem">{sectores}</div></div></section>'''
    mejora = f'''<section class="section-pad claro"><div class="wrap g2">
<div class="foto reveal izq">{img("torre_patio", "Gestión de patio: posición de cada camión dentro de la instalación")}</div>
<div class="reveal der"><span class="eyebrow">Mejora continua</span><h2>De los datos a <em>decisiones operativas</em></h2>
<p class="lead" style="margin-top:1rem">Nuestra metodología de mejora continua busca identificar tiempos improductivos, reprocesos y oportunidades de eficiencia. La torre de control permite analizar los servicios, revisar incidencias y fortalecer la trazabilidad documental para tomar decisiones mejor informadas.</p>
<p class="lead" style="margin-top:.8rem">Un ejemplo es la gestión inteligente de patio, que registra la ubicación de los camiones dentro de instalaciones operativas y facilita su localización durante la preparación y despacho.</p></div>
</div></section>'''
    resp = "".join(f'<div class="ans reveal"><h3>{esc(q)}</h3><p class="answer">{esc(a)}</p></div>' for q, a in FAQ_GENERAL)
    resp_s = f'''<section class="section-pad" id="respuestas"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Respuestas directas</span>
<h2>Lo que conviene saber antes de cotizar.</h2></div><div class="ans-grid">{resp}</div>
<p style="margin-top:1.4rem"><a class="go" href="@/preguntas-frecuentes.html">Ver todas las preguntas frecuentes</a></p></div></section>'''
    return hero + partida + movil + cinta() + nosotros + unidades + porque_s + torre + galeria + industrias + mejora + resp_s + blog_cards(POSTS) + cta()

def p_propios():
    prov = "".join(f'<span class="chip claro">{x}</span>' for x in ["Equipamientos especiales", "Tolvas", "Grúas", "Aljibes", "Furgones", "Carrocerías", "Hidráulicos", "Sistemas eléctricos", "Pintura y rotulación"])
    return (pg_hero([("Inicio", "index.html"), ("Transporte de unidades por sus propios medios", None)], "Unidad 01 · Transporte de unidades",
                    "Transporte de unidades <em>por sus propios medios</em>",
                    "Especialistas en traslado profesional de camiones, buses y maquinaria que puede circular por sus propios medios. Trabajamos con conductores calificados y protocolos de inspección, retiro, seguimiento y entrega.",
                    "tractos_puerto", "Tractos nuevos en un puerto, listos para su traslado por sus propios medios",
                    f'<div class="btns"><a class="btn btn-teal" href="@/contacto.html">Cotizar un traslado →</a><a class="btn btn-ghost" href="{wa("Hola, quiero cotizar un traslado por sus propios medios.")}" target="_blank" rel="noopener">WhatsApp</a></div>')
    + cinta()
    + f'''<section class="section-pad"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Unidad 01 · Especialización</span><h2>Camiones, buses y maquinaria: <em>traslado seguro de principio a fin</em></h2>
<p class="lead" style="margin-top:1rem">En {MARCA} seleccionamos y habilitamos a nuestros conductores según los requerimientos de cada operación. Coordinamos movimientos desde puertos, concesionarios y centros de distribución hacia talleres, maestranzas, revisiones técnicas, sucursales o clientes finales.</p>
<p class="lead" style="margin-top:.8rem">El servicio se respalda con asignación digital, inspección de la unidad, registro de observaciones, seguimiento del traslado y comprobante de entrega. Cada movimiento puede quedar asociado al historial del vehículo o chasis.</p>
<p class="lead" style="margin-top:.8rem">Adicionalmente, nuestra oferta corporativa contempla transporte automotriz de vehículos livianos y pesados, así como soluciones con equipos especializados según disponibilidad y alcance contractual.</p></div>
<div class="foto reveal der">{img("bus", "Bus eléctrico listo para su traslado por sus propios medios")}</div>
</div></section>
<section class="section-pad claro"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Qué significa</span><h2>El vehículo viaja <em>manejado</em>, no cargado.</h2>
<div class="def" style="margin-top:1.2rem"><p><strong>Por sus propios medios</strong> quiere decir que un conductor de {MARCA} maneja la unidad hasta su destino. No va sobre una cama baja ni dentro de otro camión.</p></div>
<p style="margin-top:.8rem"><a class="go" href="@/blog/traslado-por-sus-propios-medios.html">Leer la guía completa</a></p></div>
<div class="reveal der">{tarjetas([("camion", "", "Camiones y tractos", "Unidades nuevas o en operación."), ("bus", "", "Buses", "Para empresas de transporte de pasajeros."), ("maquinaria", "", "Maquinaria", "La que puede circular por sí misma."), ("liviano", "", "Vehículos livianos", "Transporte automotriz de livianos y pesados.")], "g2")}</div>
</div></section>
<section class="section-pad"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Qué incluye</span><h2>Nos hacemos cargo del traslado <em>de punta a punta.</em></h2></div>
{tarjetas([("conductor", "Conductores", "Calificados para cada operación", "Seleccionamos y habilitamos a cada conductor según el tipo de unidad y la ruta."),
           ("costo", "Costos del viaje", "Un solo precio por el servicio", "Según la operación, el valor incluye combustible y viáticos del traslado."),
           ("check", "Inspección", "Checklist al retirar y al entregar", "Registramos el estado de la unidad con fotos y observaciones."),
           ("gps", "Seguimiento", "GPS y estados en línea", "Ves dónde va cada unidad y cuánto le falta para llegar."),
           ("doc", "Entrega", "Prueba de entrega digital", "Quién recibió, a qué hora, con fotos y documento descargable."),
           ("historial", "Historial", "Todo queda asociado al chasis", "Cada movimiento suma al historial de la unidad.")])}
{rev("confirmar en qué operaciones el combustible y los viáticos van incluidos y en cuáles no.")}</div></section>
<section class="section-pad claro"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Cómo trabajamos</span><h2>Cinco pasos, <em>todos con registro.</em></h2></div>
{pasos([("Solicitud", "Nos indicas unidades, origen, destino y fecha."), ("Asignación", "Asignamos al conductor habilitado para esa operación."),
        ("Retiro con checklist", "Inspección de la unidad con fotos y observaciones."), ("Traslado en línea", "Seguimiento GPS y estados de avance."),
        ("Entrega con respaldo", "Prueba de entrega digital y documento descargable.")])}</div></section>
<section class="section-pad"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Qué trasladamos</span><h2>Unidades nuevas, terminadas <em>o que cambian de base.</em></h2></div>
{fotos([("tractos_patio", "Tractos alineados en un patio", "Camiones y tractos"), ("bus", "Bus eléctrico listo para su traslado", "Buses"), ("aljibe", "Camión aljibe terminado", "Unidades con equipamiento")])}</div></section>
<section class="section-pad dark"><div class="wrap g2">
<div class="foto reveal izq">{img("unidades_tolvas", "Camiones tolva terminados en el patio de un carrocero")}</div>
<div class="reveal der"><span class="eyebrow">Maestranza</span><h2>Coordinación integral <em>de proveedores</em></h2>
<p class="lead" style="margin-top:1rem">Un Encargado de Maestranzas coordina y supervisa la planificación de los trabajos que realizan los distintos proveedores externos sobre los vehículos, garantizando plazos y correcta ejecución de cada etapa.</p>
<div class="chips">{"".join(f'<span class="chip">{x}</span>' for x in ["Equipamientos especiales", "Tolvas", "Grúas", "Aljibes", "Furgones", "Carrocerías", "Hidráulicos", "Sistemas eléctricos", "Pintura y rotulación"])}</div></div>
</div></section>
<section class="section-pad"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Desde dónde y hacia dónde</span><h2>Del puerto a la sucursal, <em>a lo largo de Chile.</em></h2></div>
{tarjetas([("origen", "Origen", "Puertos, concesionarios y centros logísticos", "Retiramos las unidades donde llegan o se almacenan."),
           ("maestranza", "Paso intermedio", "Maestranzas, carroceros y revisiones técnicas", "Llevamos la unidad a cada proveedor y la retiramos terminada."),
           ("destino", "Destino", "Sucursales y clientes en regiones", "Entregamos donde la unidad comienza a trabajar.")])}
<div class="foto reveal zoom" style="margin-top:1.4rem">{img("unidades_puerto", "Tracto en un puerto, listo para su retiro")}</div></div></section>'''
    + faq(FAQ_PROPIOS) + cta("Cotiza el traslado de tu flota.", "Dinos cuántas unidades, desde dónde y hacia dónde.", "Cotizar un traslado"))

def p_distribucion():
    return (pg_hero([("Inicio", "index.html"), ("Distribución a retail y B2B", None)], "Unidad 02 · Carga y distribución", "Distribución a retail <em>y B2B</em>",
                    "Soluciones para el movimiento de mercaderías y el abastecimiento de empresas, con coordinación de despachos y visibilidad de la operación.",
                    "bodega", "Bodega central con carga paletizada lista para distribución a retail",
                    '<div class="btns"><a class="btn btn-teal" href="@/contacto.html">Solicitar propuesta logística →</a><a class="btn btn-ghost" href="@/cross-docking.html">Ver cross-docking</a></div>')
    + cinta()
    + f'''<section class="section-pad"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Unidad 02 · Carga y distribución</span><h2>Logística para empresas <em>que necesitan cumplir cada entrega</em></h2>
<p class="lead" style="margin-top:1rem">El transporte de carga forma parte de la oferta de {MARCA}. Nuestro enfoque es responder a necesidades de distintos volúmenes mediante coordinación, control de horarios y seguimiento operacional.</p>
<p class="lead" style="margin-top:.8rem">La línea Retail & B2B lleva esta propuesta al abastecimiento de tiendas, la distribución entre empresas, la consolidación de rutas y el cross-docking. Cada solución se diseña de acuerdo con el volumen, la frecuencia, los destinos y las instalaciones disponibles.</p>
<p class="lead" style="margin-top:.8rem">La tecnología de {MARCA} permite centralizar solicitudes, asignaciones, estados de servicio y respaldos de entrega, contribuyendo a una gestión más transparente para el cliente.</p>
<a class="go" href="@/contacto.html" style="margin-top:.6rem">Solicitar propuesta logística</a></div>
<div class="foto reveal der">{img("descarga", "Carga de pallets en un camión de distribución B2B")}</div>
</div></section>
<section class="section-pad claro"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Qué hacemos</span><h2>Conectamos tu marca <em>con cada góndola.</em></h2>
<p class="lead" style="margin-top:1rem">Todo producto que llega al retail sale de la bodega central de su marca. Alguien tiene que llevarlo a cada supermercado, tienda de mejoramiento del hogar o ferretería. Ese es nuestro trabajo.</p></div>
<div class="reveal der">{tarjetas([("caja", "", "Carga paletizada", "De distintos volúmenes."), ("destino", "", "Centros y locales", "Despachos a centros de distribución, locales y clientes empresariales."), ("reloj", "", "Con la frecuencia que acuerdes", "Despachos diarios o según tu operación."), ("camion", "", "Flota propia", "Conductores y camiones de " + MARCA + ".")], "g2")}</div>
</div></section>
<section class="section-pad"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Cómo funciona</span><h2>Tú agendas la cita. <em>Nosotros llegamos a la hora.</em></h2></div>
{pasos([("Tu bodega prepara la carga", "Los pallets quedan listos en tu bodega central."), ("Tú agendas la cita", "Coordinas con cada cliente del retail el día y la hora."),
        ("Cargamos y salimos a tiempo", "Nuestra flota retira la carga y sigue la ruta del día."), ("Entrega con respaldo", "Guía firmada, fotos y estado visible en línea.")])}</div></section>
<section class="section-pad claro"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">En terreno</span><h2>Andén, bodega y ruta.</h2></div>
{fotos([("carga_anden", "Carga de un camión en el andén", "Carga en andén"), ("camiones_blancos", "Flota de distribución B2B", "Flota de distribución"), ("bodega2", "Bodega con racks y pallets", "Bodega central"),
        ("anden_bodega", "Andén de una bodega con un camión cargando", "Despacho"), ("anden", "Camiones esperando en el andén", "Salida a ruta"), ("bodega3", "Pallets listos para despacho", "Pallets listos")])}
{rev("las fotos de bodega son de la operación de un ex cliente (comentario de Carlos en la grilla). Para publicarlas hace falta su permiso, o que no se reconozca la marca. Tampoco se nombra a ninguna cadena de retail como destino sin confirmarlo con WEPLACEU.")}</div></section>
<section class="section-pad dark"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Lo que ves en cada entrega</span><h2>Dejas de pedir la foto de la guía <em>por WhatsApp.</em></h2>
<ul class="check"><li>Dónde va cada camión, en el mapa</li><li>Si la carga ya se entregó y a qué hora</li><li>Quién recibió y firmó la guía</li><li>Fotos de la entrega y documento descargable</li></ul>
<div class="btns"><a class="btn btn-teal" href="@/torre-de-control.html">Ver Control Tower →</a></div></div>
<div class="marco reveal der">{img("torre_entrega", "Prueba de entrega con las fotos de cada despacho en Control Tower")}</div>
</div></section>
<section class="section-pad"><div class="wrap g2" style="align-items:start">
<div class="reveal izq"><span class="eyebrow">Experiencia</span><h2>Ya operamos la distribución <em>de una marca de consumo masivo.</em></h2>
<p class="lead" style="margin-top:1rem">Durante cerca de tres años repartimos a diario sus productos, desde su casa matriz al retail, con flota propia y citas por cliente.</p></div>
<div class="reveal der"><span class="eyebrow">Crece con tu operación</span><h2>Más locales, <em>más frecuencia.</em></h2>
<p class="lead" style="margin-top:1rem">Cuando tu marca entra a nuevos locales o regiones, la operación se ajusta en volumen, frecuencia y destinos. La diseñamos contigo según lo que tu bodega puede despachar.</p></div>
</div></section>
<section class="section-pad claro"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Alcance</span><h2>Lo que hacemos y <em>lo que no.</em></h2></div>
<div class="g2" style="align-items:stretch">
<div class="card reveal"><h3>Sí hacemos</h3><ul class="check"><li>Distribución de empresa a empresa: de tu bodega al retail</li><li>Cross-docking: recepción y despacho en menos de 24 horas</li><li>Seguimiento y respaldo de cada entrega</li></ul></div>
<div class="card reveal"><h3>No hacemos</h3><ul class="check"><li>Última milla: despachos a domicilio de personas</li></ul></div>
</div></div></section>'''
    + faq(FAQ_DISTRIB) + cta("Solicita tu propuesta logística.", "Cuéntanos volumen, frecuencia y destinos.", "Solicitar propuesta"))

def p_cross():
    return (pg_hero([("Inicio", "index.html"), ("Distribución a retail y B2B", "distribucion-retail-b2b.html"), ("Cross-docking", None)], "Unidad 02 · Distribución", "Cross-docking: <em>despacho en menos de 24 horas</em>",
                    "Recibimos tu carga, la ordenamos por destino y la despachamos en menos de 24 horas. La bodega funciona como punto de paso, no como almacén.",
                    "bodega2", "Bodega con racks y pallets preparados para cross-docking",
                    '<div class="btns"><a class="btn btn-teal" href="@/contacto.html">Cotizar cross-docking →</a></div>')
    + f'''<section class="section-pad"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Qué es</span><h2>La carga entra <em>y sale el mismo día o al siguiente.</em></h2>
<div class="def" style="margin-top:1.2rem"><p><strong>Cross-docking</strong> es recibir la carga en bodega, ordenarla por destino y despacharla en menos de 24 horas, sin guardarla en racks.</p></div>
<p style="margin-top:1rem"><a class="go" href="@/blog/cross-docking.html">Leer la guía completa</a></p></div>
<div class="foto reveal der">{img("carga_anden", "Carga de un camión en el andén de una bodega")}</div>
</div></section>
<section class="section-pad claro"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Cómo funciona</span><h2>Tres pasos <em>en menos de 24 horas.</em></h2></div>
{pasos([("Llega la carga", "Se recibe en bodega y se registra."), ("Se ordena por destino", "Cada pallet queda asignado a su ruta y a su cita."), ("Sale a ruta", "Nuestra flota la entrega, con respaldo en Control Tower.")])}</div></section>
<section class="section-pad"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Diferencia</span><h2>Cross-docking <em>no es almacenaje.</em></h2></div>
<div class="g2" style="align-items:stretch">
<div class="card reveal izq">{icono("caja")}<h3>Almacenaje</h3><ul class="check"><li>La carga se guarda en racks</li><li>Puede quedarse días o semanas</li><li>Lo que se busca es espacio</li></ul></div>
<div class="card reveal der">{icono("reloj")}<h3>Cross-docking</h3><ul class="check"><li>La carga va de paso</li><li>Sale en menos de 24 horas</li><li>Lo que se busca es velocidad</li></ul></div>
</div></div></section>
<section class="section-pad claro"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Para diseñarlo</span><h2>Lo que necesitamos saber.</h2>
<p class="lead">Lo diseñamos según volumen, frecuencia, destinos e instalaciones disponibles.</p></div>
{tarjetas([("caja", "Volumen", "Pallets o bultos por día", "Cuánta carga entra y cuánta sale."), ("reloj", "Frecuencia", "Días de operación", "Todos los días, algunos días o por temporada."),
           ("ruta", "Destinos", "Clientes y horarios de cita", "A qué locales va y a qué hora te reciben."), ("patio", "Instalaciones", "Dónde se recibe y despacha", "Andenes y espacio disponibles.")], "g4")}
{rev("la maqueta de Carlos decía «cross-docking sujeto a capacidad e implementación acordadas». Confirmar si se ofrece hoy o si es parte de lo que la unidad busca sumar.")}</div></section>'''
    + faq(FAQ_CROSS) + cta("Cotiza tu operación de cross-docking.", "Cuéntanos volumen, frecuencia y destinos."))

def p_torre():
    mods = [("gps", "", "Monitoreo GPS", "Ubicación de cada unidad, paradas y avance de la ruta."), ("ruta", "", "Planificación", "Programación y asignación digital de servicios y rutas."),
            ("check", "", "Checklist con fotos", "Inspección de retiro y recepción, adaptada a cada operación."), ("doc", "", "Prueba de entrega", "Quién recibió, a qué hora, con firma, fotos y documento en PDF."),
            ("estrella", "", "Satisfacción", "Cada entrega puede terminar con una evaluación breve de quien recibe."), ("costo", "", "Costos", "Registro de costos por servicio."),
            ("historial", "", "Historial por chasis", "Cada movimiento queda asociado a la unidad."), ("grafico", "", "Indicadores", "Tiempos de servicio, entregas a tiempo y estado de las órdenes.")]
    gal = [("torre_mapa", "Monitoreo en línea de la flota"), ("torre_estados", "Estado de rutas y órdenes"), ("torre_checklist", "Checklist digital de la unidad"),
           ("torre_entrega", "Fotos de la prueba de entrega"), ("panel", "Indicadores del servicio"), ("torre_patio", "Gestión de patio")]
    gs = "".join(f'<figure class="reveal zoom">{img(n, c, sizes="(max-width: 760px) 100vw, 33vw")}<figcaption>{c}</figcaption></figure>' for n, c in gal)
    lis = "".join(f"<li>{x}</li>" for x in VISIBILIDAD)
    return (pg_hero([("Inicio", "index.html"), ("Control Tower", None)], "Tecnología transversal", TORRE,
                    "Una plataforma tecnológica que integra planificación, asignación, trazabilidad, control documental y evidencia operacional. No se trata solamente de conocer dónde está una unidad: se trata de disponer de información para gestionar la operación completa, desde la solicitud hasta la entrega.",
                    "patio_flota", "Patio con camiones y tractos en seguimiento", '<div class="btns"><a class="btn btn-teal" href="@/contacto.html">Pedir una demostración →</a></div>')
    + f'''<section class="section-pad dark"><div class="wrap">
<div class="g2" style="align-items:start;margin-bottom:2.4rem"><div class="reveal izq"><span class="eyebrow">Gestión logística inteligente</span><h2>Visibilidad <em>en cada etapa</em></h2>
<p class="lead" style="margin-top:1rem">Acompaña las dos unidades de negocio. La consultas desde tu computador, sin llamar a nadie.</p></div>
<div class="reveal der"><ul class="check">{lis}</ul></div></div>
{torre_viva()}</div></section>
<section class="section-pad"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Dos vistas</span><h2>Una para el conductor. <em>Otra para tu equipo.</em></h2></div>
<div class="g2" style="align-items:stretch">
<div class="card reveal izq">{icono("doc")}<span class="k">En el camino</span><h3>Vista del conductor</h3><p>En su celular registra el checklist, las fotos y la firma de quien recibe.</p></div>
<div class="card reveal der">{icono("plataforma")}<span class="k">En la oficina</span><h3>Vista de tu equipo</h3><p>Tu jefe de logística o de transporte ve la flota en el mapa, los estados, las pruebas de entrega y los reportes, con su propio usuario.</p></div>
</div></div></section>
<section class="section-pad claro"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Módulos</span><h2>Todo el servicio <em>en una sola plataforma.</em></h2>
<p class="lead">Muchas operaciones usan una herramienta para el checklist, otra para el GPS y una planilla para las entregas. Aquí está todo junto y conectado.</p></div>
{tarjetas(mods, "g4")}</div></section>
<section class="section-pad"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">La plataforma, por dentro</span><h2>Pantallas reales <em>de nuestra operación</em></h2>
<p class="lead">Imágenes de la plataforma en uso. Ocultamos datos de clientes, conductores y unidades.</p></div>
<div class="gal">{gs}</div>{rev("título y textos de la maqueta de Carlos («WEPLACEU Control Tower», «Visibilidad en cada etapa», «La plataforma, por dentro»). El sitio nunca nombra ni enlaza la plataforma del proveedor. El botón de acceso para clientes queda pendiente: el enlace mostraría el dominio del proveedor. Confirmar si la gestión de patio es parte de la misma plataforma.")}</div></section>
<section class="section-pad claro"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Mejora continua</span><h2>De los datos a <em>decisiones operativas</em></h2>
<p class="lead" style="margin-top:1rem">Nuestra metodología de mejora continua busca identificar tiempos improductivos, reprocesos y oportunidades de eficiencia. La torre de control permite analizar los servicios, revisar incidencias y fortalecer la trazabilidad documental para tomar decisiones mejor informadas.</p>
<p class="lead" style="margin-top:.8rem">Creamos un usuario para cada persona de tu equipo que necesite seguir la operación. Tu equipo consulta y descarga; los cambios los hace la operación de {MARCA}.</p>
<p style="margin-top:.8rem"><a class="go" href="@/blog/seguimiento-de-carga.html">Qué deberías poder ver de tu carga</a></p></div>
<div class="marco reveal der">{img("torre_checklist", "Checklist digital de recepción de una unidad en Control Tower")}</div>
</div></section>'''
    + faq(FAQ_TORRE) + cta("Pide una demostración de Control Tower.", "Te mostramos cómo verías tu propia operación.", "Pedir demostración"))

SECTORES = [
    ("marcas", "Marcas e importadores de camiones y buses", "tractos_puerto", "Tractos nuevos en un puerto",
     "Retiramos las unidades nuevas en puerto y las entregamos en concesionarios, carroceros o directamente al cliente final.",
     ["Retiro en puerto o centro logístico", "Entregas a la red de concesionarios", "Checklist y respaldo de cada unidad"], "transporte-por-sus-propios-medios.html"),
    ("concesionarios", "Concesionarios y redes de servicio", "tractos_patio", "Tractos alineados en el patio de un concesionario",
     "Movemos unidades entre sucursales, a revisión técnica o a los proveedores que las preparan para la venta.",
     ["Traslados entre sucursales y regiones", "Llevada y retiro de maestranzas y carroceros", "Historial de cada chasis"], "transporte-por-sus-propios-medios.html"),
    ("flotas", "Empresas con flota propia", "bus", "Bus listo para su traslado",
     "Transporte de pasajeros, arriendo de flotas y empresas con maquinaria: movemos tus unidades a mantención, a una faena nueva o a otra base.",
     ["Buses, camiones y vehículos livianos", "Maquinaria que circula por sí misma", "Seguimiento en línea de cada traslado"], "transporte-por-sus-propios-medios.html"),
    ("carroceros", "Carroceros y fabricantes de equipamiento", "aljibe", "Camión aljibe terminado en el patio de un carrocero",
     "Retiramos el chasis, lo llevamos a cada etapa del trabajo y entregamos la unidad terminada a tu cliente.",
     ["Coordinación entre proveedores", "Seguimiento de plazos por etapa", "Entrega con prueba digital"], "transporte-por-sus-propios-medios.html"),
    ("retail", "Marcas que venden en retail", "bodega", "Bodega central con carga paletizada",
     "Alimentos, productos químicos, herramientas e insumos industriales: llevamos tu carga desde tu bodega central a cada local del retail.",
     ["Carga paletizada con cita por cliente", "Cross-docking en menos de 24 horas", "Prueba de entrega para facturar sin esperar"], "distribucion-retail-b2b.html"),
]

def p_industrias():
    indice = "".join(f'<a href="#{i}">{esc(t)}</a>' for i, t, *_ in SECTORES)
    sec = "".join(f'''<article class="sector" id="{i}"><div class="foto reveal {"izq" if k % 2 == 0 else "der"}">{img(f, a)}</div><div class="reveal {"der" if k % 2 == 0 else "izq"}"><span class="eyebrow">Industria {k+1:02d}</span><h2>{esc(t)}</h2><p class="lead" style="margin-top:.8rem">{esc(d)}</p>
<ul class="check">{"".join(f"<li>{esc(x)}</li>" for x in pts)}</ul><a class="go" href="@/{u}">Ver el servicio</a></div></article>''' for k, (i, t, f, a, d, pts, u) in enumerate(SECTORES))
    return (pg_hero([("Inicio", "index.html"), ("Industrias", None)], "A quién servimos", "Industrias <em>que atendemos</em>",
                    "Empresas que necesitan que sus unidades o su carga lleguen a destino, a la hora y con respaldo.", "patio_flota", "Patio con camiones y tractos alineados",
                    f'<div class="indice">{indice}</div>')
    + f'<section class="section-pad"><div class="wrap">{sec}{rev("los cinco sectores salen de la reunión del 13-nov y de la base de prospectos cargada en el HubSpot de WEPLACEU. Confirmar que cubren a sus clientes actuales y potenciales.")}</div></section>'
    + cta())

def p_nosotros():
    pil = "".join(f'<span class="chip claro">{x}</span>' for x in ["Seguridad", "Confianza", "Experiencia", "Compromiso", "Integridad"])
    return (pg_hero([("Inicio", "index.html"), ("Nosotros", None)], "Sobre nosotros", "Una empresa construida sobre la confianza y <em>la excelencia operacional</em>",
                    "Transporte, logística y tecnología para empresas, a lo largo de Chile.", "tractos_patio", "Tractos alineados en un patio")
    + cinta()
    + f'''<section class="section-pad"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Logística integral</span><h2>Nacimos para hacer <em>transporte de alta calidad.</em></h2>
<p class="lead" style="margin-top:1rem">{MARCA} nació con el propósito de desarrollar servicios de transporte de alta calidad, basados en las necesidades de cada cliente, el respeto por nuestros colaboradores y el cuidado del medioambiente.</p>
<p class="lead" style="margin-top:.8rem">Nuestra propuesta combina experiencia operacional, seguridad, compromiso e integridad con herramientas digitales que facilitan el control de cada servicio.</p></div>
<div class="foto reveal der">{img("carga_anden", "Carga de un camión en el andén de una bodega")}</div>
</div></section>
<section class="section-pad claro"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Nuestro compromiso</span><h2>Lo que no cambia, <em>sea cual sea el servicio.</em></h2></div>
<div class="chips">{pil}</div>
<div class="cifras plano">{CIFRAS}</div>
{rev("la historia de la empresa, sus socios y el equipo se completan con la inducción que dicta WEPLACEU el lun 16-nov, 14:00–15:00. Las fotos del equipo salen de la sesión en terreno de noviembre (4 horas, 3 cambios de ropa, aviso con una semana).")}
</div></section>
<section class="section-pad"><div class="wrap g2">
<div class="reveal izq"><span class="eyebrow">Cómo trabajamos</span><h2>Primero entendemos tu operación. <em>Después cotizamos.</em></h2>
<p class="lead" style="margin-top:1rem">Antes de proponer un servicio preguntamos qué te está costando tiempo o plata. A veces la respuesta es un traslado. Otras veces es coordinar a tus proveedores o medir plazos que nadie estaba midiendo.</p>
<p class="lead" style="margin-top:.8rem">Por eso hablamos de acompañamiento: movemos unidades y carga, y además ayudamos a que tu operación funcione mejor.</p></div>
<div class="reveal der">{tarjetas([("escudo", "", "Seguridad", "Conductores habilitados y protocolos de inspección."), ("check", "", "Respaldo", "Cada paso queda registrado con fotos y documentos."), ("gps", "", "Visibilidad", "Ves tu operación en línea en Control Tower."), ("terreno", "", "Acompañamiento", "Trabajamos junto a tu equipo, en terreno.")], "g2")}</div>
</div></section>
<section class="section-pad dark"><div class="wrap"><div class="sec-title reveal"><span class="eyebrow">Nuestra operación</span><h2>En el puerto, en el patio <em>y en el andén.</em></h2></div>
{fotos([("tractos_puerto", "Tractos nuevos en un puerto", "Retiro en puerto"), ("patio_flota", "Patio con camiones y tractos", "Patio"), ("aljibe", "Camión aljibe terminado", "Unidades terminadas"),
        ("bus", "Bus listo para su traslado", "Buses"), ("camiones_blancos", "Flota de distribución", "Distribución"), ("bodega3", "Pallets listos para despacho", "Bodega")])}</div></section>
'''
    + mapa()
    + cta())

def mapa():
    return f'''<section class="section-pad claro" id="ubicacion"><div class="wrap ubicacion">
<div class="reveal izq"><span class="eyebrow">Dónde estamos</span><h2>Mallplaza Norte, <em>Huechuraba.</em></h2>
<p class="lead" style="margin-top:1rem">Nuestra oficina está en el cowork del piso 8 de la Torre Integramédica, en Mallplaza Norte. Desde ahí coordinamos operaciones de alcance nacional.</p>
<address class="dir-ficha"><b>{DIR_CALLE}</b><span>{DIR_DETALLE}</span><span>{DIR_COMUNA}, Región Metropolitana</span></address>
<div class="btns" style="margin-top:1.2rem"><a class="btn btn-navy" href="{MAPA_RUTA}" target="_blank" rel="noopener">Cómo llegar</a><a class="btn btn-borde" href="{IG_URL}" target="_blank" rel="noopener">{IG_SVG}@{IG_HANDLE}</a></div>
{rev("dirección tomada del sitio de Pronto Cowork (Mallplaza Norte: Av. Américo Vespucio 1737, piso 8, Torre Integramédica). Confirmar con WEPLACEU que se publica, y si reciben visitas ahí o es solo oficina administrativa. El punto del mapa es el de la torre en OpenStreetMap.")}</div>
<div class="mapa reveal der"><iframe src="{MAPA_EMBED}" title="Mapa: {MARCA} en Mallplaza Norte, Huechuraba" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
<span class="mapa-coord" aria-hidden="true">{-GEO_LAT:.4f}° S · {-GEO_LNG:.4f}° O</span></div>
</div></section>'''

def p_blog():
    return (pg_hero([("Inicio", "index.html"), ("Blog", None)], "Blog y noticias", "Guías de transporte <em>y logística B2B</em>",
                    "Lo que aprendemos en terreno, explicado para quien compra o administra transporte en su empresa.", "camiones_blancos", "Flota de distribución en el andén")
    + blog_cards(POSTS, "Últimas publicaciones.", "Artículos", claro=False)
    + f'<div class="wrap" style="margin-top:-2rem;margin-bottom:3rem">{rev("los tres artículos son borradores para revisar con WEPLACEU. Los siguientes se escriben con la información de la inducción del lunes.")}</div>'
    + cta())

NOMBRES = {"transporte-por-sus-propios-medios.html": "Transporte de unidades por sus propios medios", "torre-de-control.html": TORRE,
           "cross-docking.html": "Cross-docking", "distribucion-retail-b2b.html": "Distribución a retail y B2B"}

def p_post(p):
    cuerpo = ""
    for tipo, x in p["cuerpo"]:
        cuerpo += f"<{tipo}>{esc(x)}</{tipo}>" if tipo != "ul" else "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in x) + "</ul>"
    rel = " · ".join(f'<a class="go" href="@/{u}">{NOMBRES[u]}</a>' for u in p["rel"])
    otros = [o for o in POSTS if o is not p]
    corto = p["titulo"] if len(p["titulo"]) <= 40 else p["titulo"][:38].rsplit(" ", 1)[0] + "…"
    return (pg_hero([("Inicio", "index.html"), ("Blog", "blog.html"), (corto, None)], p["tag"], p["titulo"], p["resumen"], p["foto"], p["titulo"])
    + f'''<section class="section-pad"><div class="wrap"><article class="articulo reveal">
<p class="meta">Por {MARCA} · Borrador del {FECHA}</p>{cuerpo}
<div class="relacionados"><p><b>Servicios relacionados:</b></p><p>{rel}</p></div>
{rev("borrador. Revisar con WEPLACEU antes de publicar.")}</article></div></section>'''
    + blog_cards(otros, "Sigue leyendo.", "Más del blog") + cta())

def p_faq():
    grupos = [(f"Sobre {MARCA}", FAQ_GENERAL), ("Transporte de unidades por sus propios medios", FAQ_PROPIOS), ("Distribución a retail y B2B", FAQ_DISTRIB),
              ("Cross-docking", FAQ_CROSS), ("Control Tower", FAQ_TORRE)]
    cuerpo = "".join(faq(items, titulo, claro=(k % 2 == 1)) for k, (titulo, items) in enumerate(grupos))
    return (pg_hero([("Inicio", "index.html"), ("Preguntas frecuentes", None)], "Ayuda", "Preguntas <em>frecuentes</em>",
                    "Las respuestas a lo que más nos preguntan antes de cotizar.", "tractos_patio", "Tractos alineados en un patio")
    + cuerpo + cta())

def p_contacto():
    return (pg_hero([("Inicio", "index.html"), ("Contacto", None)], "Conversemos", "Cuéntanos qué necesita <em>tu empresa</em>",
                    "Ya sea para el traslado de unidades, transporte de carga, distribución B2B o una demostración de Control Tower, podemos evaluar una propuesta ajustada a tu operación.", "anden_bodega", "Andén de una bodega")
    + f'''<section class="section-pad"><div class="wrap contacto">
<div class="reveal izq"><h2>Te respondemos con una propuesta <em>para tu operación.</em></h2>
<p class="lead" style="margin-top:1rem">Mientras más datos nos des de volumen, frecuencia y destinos, más precisa será la cotización.</p>
<div class="datos-contacto" style="margin-top:1.4rem"><a href="{wa()}" target="_blank" rel="noopener">{WA_SVG}WhatsApp {WA_TXT}</a><a href="{IG_URL}" target="_blank" rel="noopener">{IG_SVG}Instagram @{IG_HANDLE}</a><a href="{MAPA_URL}" target="_blank" rel="noopener">{ICO_PIN}{DIR_CORTA}</a></div>
{rev("falta definir qué correo se publica (info@weplaceu.cl o info@wpu.cl). En el sitio publicado, este formulario llega al HubSpot de WEPLACEU, como el actual.")}</div>
<form class="form reveal der" id="formContacto" novalidate>
<div class="fila"><div><label for="f-nombre">Nombre</label><input id="f-nombre" name="firstname" autocomplete="given-name" required></div>
<div><label for="f-apellido">Apellido</label><input id="f-apellido" name="lastname" autocomplete="family-name" required></div></div>
<div class="fila"><div><label for="f-empresa">Empresa</label><input id="f-empresa" name="company" autocomplete="organization" required></div>
<div><label for="f-tel">Teléfono</label><input id="f-tel" name="phone" type="tel" autocomplete="tel"></div></div>
<label for="f-correo">Correo de trabajo</label><input id="f-correo" name="email" type="email" autocomplete="email" required>
<label for="f-servicio">¿Qué necesitas?</label><select id="f-servicio" name="linea_de_negocio">
<option>Transporte de unidades</option><option>Transporte de carga y Retail B2B</option><option>Cross-docking</option><option>Demostración Control Tower</option><option>Otro</option></select>
<label for="f-msg">Cuéntanos qué necesitas</label><textarea id="f-msg" name="message" placeholder="Unidades o carga, origen, destino y frecuencia"></textarea>
<p class="legal">Usamos estos datos solo para responder tu solicitud. Más detalle en <a href="@/privacidad.html">privacidad y datos personales</a>.</p>
<button class="btn btn-navy" type="submit">Enviar solicitud</button>
<p class="form-ok" id="formOk" role="status">Revisión: en el sitio publicado esta solicitud llega al equipo comercial de {MARCA}.</p>
</form></div></section>'''
    + mapa())

def p_privacidad():
    return (pg_hero([("Inicio", "index.html"), ("Privacidad", None)], "Datos personales", "Privacidad y <em>datos personales</em>",
                    "Qué datos pedimos, para qué los usamos y cómo ejercer tus derechos.", "camiones_blancos", "Flota de distribución")
    + f'''<section class="section-pad"><div class="wrap prosa">
<h2>Qué datos pedimos</h2><p>En el formulario de contacto pedimos nombre, apellido, empresa, correo, teléfono y el detalle de tu solicitud.</p>
<h2>Para qué los usamos</h2><p>Solo para responder tu solicitud y, si corresponde, enviarte una propuesta comercial. No los vendemos.</p>
<h2>Dónde se guardan</h2><p>En el sistema de gestión comercial de {MARCA} (HubSpot), que los procesa por encargo nuestro.</p>
<h2>Por cuánto tiempo</h2><p>Mientras dure la conversación comercial y el plazo que fije la política de {MARCA}.</p>
<h2>Tus derechos</h2><p>Puedes pedir acceso, rectificación, eliminación u oposición por el <a href="@/contacto.html">formulario de contacto</a> o por <a href="{wa("Hola, quiero ejercer mis derechos sobre mis datos personales.")}" target="_blank" rel="noopener">WhatsApp ({WA_TXT})</a>.</p>
<h2>Cookies</h2><p>El sitio usa cookies de medición y de marketing solo si las aceptas en el aviso de cookies.</p>
{rev("texto base que debe validar WEPLACEU con su asesor legal: plazo de conservación, correo para ejercer derechos y transferencia internacional de datos (HubSpot opera fuera de Chile). Ley 21.719, vigente el 1-dic-2026. El aviso de cookies actual del sitio (Complianz) se mantiene.")}
</div></section>''')

# ------------------------------------------------------------------ SEO por página: archivo, menú, título, descripción, contenido, tipo, imagen, palabras clave
PAGINAS = [
    ("index.html", "inicio", "WEPLACEU | Traslado de camiones y distribución B2B en Chile",
     "Traslado de camiones, buses y maquinaria por sus propios medios y distribución a retail B2B en Chile, con seguimiento en línea en Control Tower.",
     p_inicio, "WebPage", "patio_flota", "transporte por sus propios medios, distribución a retail, logística B2B Chile"),
    ("transporte-por-sus-propios-medios.html", "propios", "Traslado de camiones y buses por sus propios medios | WEPLACEU",
     "Trasladamos camiones, tractos, buses y maquinaria por sus propios medios desde puerto o concesionario, con checklist, GPS y prueba de entrega digital.",
     p_propios, "Service", "tractos_puerto", "traslado de camiones por sus propios medios, traslado de buses, traslado de vehículos pesados"),
    ("distribucion-retail-b2b.html", "distribucion", "Distribución a retail y transporte de carga B2B | WEPLACEU",
     "Distribución de carga paletizada desde tu bodega a supermercados, mejoramiento del hogar y canal ferretero, con flota propia y prueba de entrega digital.",
     p_distribucion, "Service", "bodega", "distribución a retail, transporte de carga B2B, distribución de pallets"),
    ("cross-docking.html", "distribucion", "Servicio de cross-docking: despacho en menos de 24 h | WEPLACEU",
     "Cross-docking en la Región Metropolitana: recibimos tu carga, la ordenamos por destino y la despachamos en menos de 24 horas, con respaldo de cada entrega.",
     p_cross, "Service", "bodega2", "cross-docking, servicio de cross-docking Santiago, despacho en 24 horas"),
    ("torre-de-control.html", "torre", "Control Tower: seguimiento de flota en línea | WEPLACEU",
     "WEPLACEU Control Tower: monitoreo GPS, checklist con fotos, prueba de entrega descargable e indicadores de cada traslado y despacho, en una sola plataforma.",
     p_torre, "WebPage", "patio_flota", "torre de control logística, seguimiento de flota en línea, prueba de entrega digital"),
    ("industrias.html", "industrias", "Transporte para marcas, concesionarios y retail | WEPLACEU",
     "Traslados y distribución para marcas e importadores de camiones y buses, concesionarios, empresas con flota, carroceros y marcas que venden en retail.",
     p_industrias, "CollectionPage", "patio_flota", "transporte para concesionarios, traslado de unidades para importadores, logística para carroceros"),
    ("nosotros.html", "nosotros", "Nosotros: transporte, logística y tecnología | WEPLACEU",
     "WEPLACEU es una empresa chilena de transporte y logística B2B, construida sobre la confianza y la excelencia operacional, con cobertura nacional.",
     p_nosotros, "AboutPage", "tractos_patio", "empresa de transporte B2B Chile, logística integral"),
    ("blog.html", "blog", "Blog de transporte y logística B2B | WEPLACEU",
     "Guías sobre traslado de vehículos por sus propios medios, distribución a retail, cross-docking y seguimiento de carga en línea.",
     p_blog, "CollectionPage", "camiones_blancos", "blog logística B2B, guías de transporte"),
    ("preguntas-frecuentes.html", None, "Preguntas frecuentes sobre traslados y distribución | WEPLACEU",
     "Respuestas sobre traslados por sus propios medios, distribución a retail, cross-docking y el seguimiento en línea de cada servicio en Control Tower.",
     p_faq, "FAQPage", "tractos_patio", "preguntas frecuentes traslado de camiones, cross-docking"),
    ("contacto.html", "contacto", "Cotizar traslado de unidades o distribución | WEPLACEU",
     "Cotiza un traslado de unidades por sus propios medios, una distribución a retail, cross-docking o una demostración de Control Tower con WEPLACEU.",
     p_contacto, "ContactPage", "anden_bodega", "cotizar traslado de camiones, cotizar distribución"),
    ("privacidad.html", None, "Privacidad y datos personales | WEPLACEU",
     "Cómo usa WEPLACEU los datos que entregas en el formulario de contacto, dónde se guardan, por cuánto tiempo y cómo ejercer tus derechos.",
     p_privacidad, "WebPage", "camiones_blancos", ""),
] + [(f'blog/{p["slug"]}.html', "blog", f'{p["seo"]} | WEPLACEU', p.get("desc", p["resumen"] + " Guía de WEPLACEU."), (lambda p=p: p_post(p)), "BlogPosting", p["foto"], "") for p in POSTS]

FAQ_DE = {"index.html": FAQ_GENERAL, "transporte-por-sus-propios-medios.html": FAQ_PROPIOS, "distribucion-retail-b2b.html": FAQ_DISTRIB,
          "cross-docking.html": FAQ_CROSS, "torre-de-control.html": FAQ_TORRE,
          "preguntas-frecuentes.html": FAQ_GENERAL + FAQ_PROPIOS + FAQ_DISTRIB + FAQ_CROSS + FAQ_TORRE}

MIGAS = {}   # ruta → [(nombre, ruta)]

# ------------------------------------------------------------------ cabecera, pie y revisión
NAV = [("propios", "Por sus propios medios", "transporte-por-sus-propios-medios.html"), ("distribucion", "Retail y B2B", "distribucion-retail-b2b.html"),
       ("torre", "Control Tower", "torre-de-control.html"), ("industrias", "Industrias", "industrias.html"),
       ("nosotros", "Nosotros", "nosotros.html"), ("blog", "Blog", "blog.html")]

def cabecera(actual):
    def a(k, n, u): return f'<a href="@/{u}"{" aria-current=\"page\"" if k == actual else ""}>{n}</a>'
    links = "".join(a(*x) for x in NAV)
    return f'''<header class="nav"><div class="wrap nav-inner">
<a class="nav-logo" href="@/index.html" aria-label="{MARCA}, inicio">{img("logo_blanco", MARCA, eager=True)}</a>
<nav class="nav-links" aria-label="Navegación principal">{links}</nav>
<div class="nav-cta"><a class="btn btn-teal" href="@/contacto.html">Cotizar →</a>
<button class="hamburger" id="hamburger" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="drawer"><span></span><span></span><span></span></button></div>
</div></header>
<div class="overlay" id="overlay"></div>
<aside class="drawer" id="drawer" aria-label="Menú"><button class="drawer-close" id="drawerClose" type="button" aria-label="Cerrar menú">×</button>
{a("inicio", "Inicio", "index.html")}{links}<a href="@/cross-docking.html">Cross-docking</a>{a("contacto", "Contacto", "contacto.html")}<a class="btn btn-teal" href="@/contacto.html">Cotizar →</a></aside>'''

def pie():
    return f'''<footer><div class="wrap"><div class="foot-grid">
<div>{img("logo_blanco", MARCA)}<p>Transporte · Logística · Tecnología. Traslado de unidades por sus propios medios y distribución a retail B2B, con {TORRE}. Cobertura nacional.</p>
<p class="foot-dir"><a href="{MAPA_URL}" target="_blank" rel="noopener">{ICO_PIN}<span>{DIR_CALLE}, piso 8<br>Torre Integramédica · Mallplaza Norte<br>{DIR_COMUNA}, Región Metropolitana</span></a></p>
<p class="foot-redes"><a href="{IG_URL}" target="_blank" rel="noopener" aria-label="Instagram de {MARCA}: @{IG_HANDLE}">{IG_SVG}<span>@{IG_HANDLE}</span></a></p></div>
<div><h3>Servicios</h3><a href="@/transporte-por-sus-propios-medios.html">Transporte de unidades</a><a href="@/distribucion-retail-b2b.html">Distribución a retail y B2B</a><a href="@/cross-docking.html">Cross-docking</a><a href="@/torre-de-control.html">Control Tower</a></div>
<div><h3>{MARCA}</h3><a href="@/nosotros.html">Nosotros</a><a href="@/industrias.html">Industrias</a><a href="@/blog.html">Blog</a><a href="@/preguntas-frecuentes.html">Preguntas frecuentes</a></div>
<div><h3>Conversemos</h3><a href="{wa()}" target="_blank" rel="noopener">WhatsApp {WA_TXT}</a><a href="{IG_URL}" target="_blank" rel="noopener">Instagram @{IG_HANDLE}</a><a href="@/contacto.html">Formulario de cotización</a><a href="@/privacidad.html">Privacidad</a></div>
</div><div class="foot-bottom">© <span id="anio"></span> {MARCA} · Transporte, logística y tecnología · weplaceu.cl</div></div></footer>'''

NOTAS = {
    "Lo que cambió en la v3 (pedido de Pablo, 14-nov)": [
        "Títulos y textos de la maqueta de Carlos, tal como los escribió. Donde Carlos pidió cambiarlos en la reunión, se aplicó su cambio: la unidad 02 se llama «Distribución a retail y B2B».",
        "Encabezados del sitio actual que se conservan: «Logística integral» y «Gestión logística inteligente».",
        "La marca se escribe WEPLACEU y la torre «WEPLACEU Control Tower», como en la maqueta de Carlos.",
        "Movimiento: carrusel con barra de avance, entradas escalonadas, cinta de servicios, torre de control animada, línea de pasos que se llena y barra de progreso de lectura.",
        "SEO: título y descripción por página, palabras clave, migas, datos estructurados (organización, servicios, preguntas, artículos), Open Graph, sitemap.xml, robots.txt y llms.txt.",
    ],
    "Lo que aplica de la reunión del 13-nov": [
        "Sitio completo de varias páginas; los nombres de las unidades dicen «por sus propios medios» y «distribución».",
        "Portada en escritorio: carrusel de 3 mensajes cada 3 segundos. En teléfono: mensaje, las dos unidades como botones y cotizar.",
        "Versión B para probar: portada partida en dos (botón de la franja amarilla).",
        "Nunca se nombra ni se enlaza la plataforma del proveedor.",
        "Se explica que vendemos la operación completa, no una aplicación.",
    ],
    "Decisiones abiertas de WEPLACEU": [
        "Tercera línea de consultoría o acompañamiento dentro de las dos unidades.",
        "Botón de acceso para clientes a la plataforma.",
        "Permiso para las fotos de bodega del ex cliente y para nombrar cadenas de retail.",
        "Vigencia de las cifras 90+ colaboradores y 700+ traslados mensuales.",
        "Si el cross-docking se ofrece hoy o es parte de lo que la unidad busca sumar.",
    ],
    "Fotos": [
        "Todas son de WEPLACEU: su presentación y la biblioteca pública de weplaceu.cl. Ninguna es de banco de imágenes.",
        "Se difuminaron patentes, rostros, la rotulación de otra empresa en dos camiones y marcas en cajas de bodega.",
        "Las unidades de las fotos son Volvo, y Volvo es cliente. WEPLACEU ya las publica en su sitio actual: confirmar que se pueden seguir usando.",
    ],
    "Al publicar (lo hace Precisión)": [
        "Se quita la franja amarilla, las notas, la versión que pierda la prueba A/B y la etiqueta noindex.",
        "Se mantienen Tag Manager, GA4, el aviso de cookies, el envío del formulario a HubSpot y el WhatsApp.",
        "Se sube el sitemap a Search Console y se redirige /politica-de-cookies-ue/ a /privacidad/.",
        "Protección anti-robot en el formulario y vigilancia de visitas, como pidió Pablo en la reunión.",
    ],
}

def panel_rev():
    cuerpo = "".join(f"<h3>{t}</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in xs)}</ul>" for t, xs in NOTAS.items())
    return f'''<div class="rev-panel" id="revPanel" role="dialog" aria-modal="true" aria-label="Notas de revisión"><div class="rev-box">
<button class="cerrar" type="button" aria-label="Cerrar notas">×</button><h2>Notas de revisión · sitio {VERSION} · {FECHA}</h2>
<p>Sitio construido con la maqueta de Carlos y la reunión del 13-nov-2026. «Mostrar notas en la página» marca en amarillo lo que falta confirmar.</p>{cuerpo}</div></div>'''

def franja(portada, n_notas):
    b = '<button type="button" id="verB" aria-pressed="false">Ver portada partida en dos (versión B)</button>' if portada else ""
    n = f'<button type="button" id="verNotas" aria-pressed="false">Mostrar notas en la página ({n_notas})</button>' if n_notas else ""
    return f'''<div class="rev-bar" role="note"><div class="wrap"><span><b>Sitio en revisión {VERSION}</b> · {FECHA} · preparado por Precisión</span>
<button type="button" data-rev-abrir>Notas de revisión</button>{n}{b}</div></div>'''

WA_SVG = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3C9 3 3.3 8.6 3.3 15.6c0 2.5.7 4.9 2 7L3 29l6.6-2.2c2 1.1 4.2 1.7 6.4 1.7 7 0 12.7-5.6 12.7-12.6S23 3 16 3zm0 23.1c-2 0-4-.6-5.7-1.6l-.4-.2-3.9 1.3 1.3-3.8-.3-.4a10.4 10.4 0 0 1-1.7-5.8C5.3 9.8 10.1 5.1 16 5.1s10.7 4.7 10.7 10.5S21.9 26.1 16 26.1zm5.9-7.8c-.3-.2-1.9-.9-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7.1a8.7 8.7 0 0 1-4.3-3.7c-.3-.6.3-.5.9-1.7.1-.2 0-.4 0-.5l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6a1.2 1.2 0 0 0-.9.4 3.7 3.7 0 0 0-1.1 2.7 6.5 6.5 0 0 0 1.4 3.4 14.6 14.6 0 0 0 5.6 4.9c2.1.9 2.9 1 3.9.8.6-.1 1.9-.8 2.2-1.5s.3-1.3.2-1.5-.3-.2-.6-.4z"/></svg>'
IG_SVG = '<svg class="ico-red" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.3" cy="6.7" r="1.2" fill="currentColor"/></svg>'
ICO_PIN = '<svg class="ico-red" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 21.5s6.5-5.6 6.5-11a6.5 6.5 0 0 0-13 0c0 5.4 6.5 11 6.5 11z" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="10.3" r="2.3" fill="currentColor"/></svg>'
# Flecha de los botones: un trazo propio que se desliza al pasar el mouse (reemplaza el carácter «→»).
FLECHA = '<svg class="flecha-svg" viewBox="0 0 20 12" aria-hidden="true" focusable="false"><path d="M1 6h16M12 1.5L17.5 6 12 10.5" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="square"/></svg>'

# ------------------------------------------------------------------ datos estructurados
SERVICIOS = [("Transporte de unidades por sus propios medios", "transporte-por-sus-propios-medios.html"), ("Distribución a retail y B2B", "distribucion-retail-b2b.html"),
             ("Cross-docking", "cross-docking.html"), (TORRE, "torre-de-control.html")]

def canon(ruta):
    return DOM + ("/" if ruta == "index.html" else "/" + ruta[:-5] + "/")

def img_abs(nombre):
    return f"{DOM}/img/{archivo(nombre)}"

ORG = {"@context": "https://schema.org", "@type": "Organization", "@id": DOM + "/#organizacion", "name": MARCA, "alternateName": ["We Place U", "WPU"],
       "url": DOM, "logo": img_abs("logo_azul"), "slogan": "Movemos tu operación. Conectamos tu negocio.",
       "description": "Empresa chilena de transporte, logística y tecnología: traslado de unidades por sus propios medios y distribución a retail B2B, con seguimiento en línea.",
       "areaServed": {"@type": "Country", "name": "Chile"},
       "address": {"@type": "PostalAddress", "streetAddress": "Av. Américo Vespucio 1737, piso 8, Torre Integramédica (Mallplaza Norte)", "addressLocality": "Huechuraba", "addressRegion": "Región Metropolitana", "addressCountry": "CL"},
       "location": {"@type": "Place", "name": "Pronto Cowork Mallplaza Norte", "geo": {"@type": "GeoCoordinates", "latitude": GEO_LAT, "longitude": GEO_LNG}, "hasMap": MAPA_URL},
       "sameAs": [IG_URL],
       "contactPoint": {"@type": "ContactPoint", "telephone": "+56965351601", "contactType": "sales", "areaServed": "CL", "availableLanguage": "es"},
       "knowsAbout": ["Traslado de camiones por sus propios medios", "Traslado de buses", "Distribución a retail", "Transporte de carga B2B", "Cross-docking", "Torre de control logística"],
       "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Servicios de " + MARCA, "itemListElement": [
           {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "url": canon(u)}} for n, u in SERVICIOS]}}
WEBSITE = {"@context": "https://schema.org", "@type": "WebSite", "@id": DOM + "/#sitio", "url": DOM, "name": MARCA, "inLanguage": "es-CL", "publisher": {"@id": DOM + "/#organizacion"}}

def datos_estructurados(ruta, titulo, desc, tipo, foto):
    url = canon(ruta)
    lds = [ORG, WEBSITE]
    pg = {"@context": "https://schema.org", "@type": "WebPage" if tipo in ("Service", "BlogPosting") else tipo, "@id": url + "#pagina", "url": url,
          "name": titulo, "description": desc, "inLanguage": "es-CL", "isPartOf": {"@id": DOM + "/#sitio"}, "about": {"@id": DOM + "/#organizacion"},
          "primaryImageOfPage": {"@type": "ImageObject", "url": img_abs(foto)}, "breadcrumb": {"@id": url + "#migas"},
          "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["h1", ".answer"]}}
    if tipo == "FAQPage":
        pg["mainEntity"] = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_DE[ruta]]
    lds.append(pg)
    migas = MIGAS.get(ruta, [("Inicio", "index.html")])
    lds.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "@id": url + "#migas", "itemListElement": [
        {"@type": "ListItem", "position": k + 1, "name": n, "item": canon(u)} for k, (n, u) in enumerate(migas)]})
    if tipo == "Service":
        lds.append({"@context": "https://schema.org", "@type": "Service", "name": titulo.split(" | ")[0], "serviceType": titulo.split(" | ")[0], "description": desc,
                    "provider": {"@id": DOM + "/#organizacion"}, "areaServed": {"@type": "Country", "name": "Chile"}, "url": url,
                    "audience": {"@type": "BusinessAudience", "audienceType": "Empresas"}, "image": img_abs(foto)})
    if tipo == "BlogPosting":
        lds.append({"@context": "https://schema.org", "@type": "BlogPosting", "headline": titulo.split(" | ")[0], "description": desc, "image": img_abs(foto),
                    "datePublished": PUBLICADO_ISO, "dateModified": FECHA_ISO, "author": {"@id": DOM + "/#organizacion"}, "publisher": {"@id": DOM + "/#organizacion"},
                    "inLanguage": "es-CL", "mainEntityOfPage": url})
    if ruta in FAQ_DE and tipo != "FAQPage":
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_DE[ruta]]})
    return "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)

def documento(ruta, clave, titulo, desc, cuerpo, tipo, foto, claves):
    pre = "../" * ruta.count("/")
    portada = ruta == "index.html"
    pre_img = f'<link rel="preload" as="image" href="@/img/{archivo(foto)}" imagesrcset="{srcset(foto)}" imagesizes="100vw" fetchpriority="high">' if anchos(foto) else ""
    doc = f'''<!DOCTYPE html>
<html lang="es-CL">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{canon(ruta)}">
<link rel="alternate" hreflang="es-CL" href="{canon(ruta)}"><link rel="alternate" hreflang="x-default" href="{canon(ruta)}">
<meta name="theme-color" content="#111C31">
{ETIQUETAS_HEAD}
<meta property="og:type" content="{"article" if tipo == "BlogPosting" else "website"}"><meta property="og:site_name" content="{MARCA}"><meta property="og:locale" content="es_CL">
<meta property="og:title" content="{esc(titulo)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canon(ruta)}">
<meta property="og:image" content="{img_abs(foto)}"><meta property="og:image:width" content="{TAM[foto][0]}"><meta property="og:image:height" content="{TAM[foto][1]}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(titulo)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{img_abs(foto)}">
<link rel="icon" type="image/png" href="@/img/{archivo("logo_azul")}">
<!-- {MARCA} · sitio {VERSION} ({FECHA}). Lo genera build_sitio_wpu.py: no se edita a mano. Palabras clave de la página: {esc(claves)} -->
{"".join(f'<link rel="preload" href="@/assets/fuentes/{a}" as="font" type="font/woff2" crossorigin>' for a in PRECARGA_FUENTES)}
{pre_img}
<link rel="stylesheet" href="@/assets/sitio.css?v={SELLO}">
{datos_estructurados(ruta, titulo, desc, tipo, foto)}
</head>
<body>
{ETIQUETAS_BODY}
<a class="skip" href="#contenido">Saltar al contenido</a>
<div class="progreso" aria-hidden="true"></div>
{franja(portada, cuerpo.count('<p class="rev">'))}
{cabecera(clave)}
<main id="contenido">{cuerpo}</main>
{pie()}
<div class="mcta"><a class="btn btn-teal" href="@/contacto.html">Cotizar →</a></div>
<a class="wa-float" href="{wa()}" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp">{WA_SVG}</a>
{panel_rev()}
<script src="@/assets/sitio.js?v={SELLO}"></script>
</body>
</html>'''
    return doc.replace('"@/', f'"{pre}').replace(' @/', f' {pre}')

# ------------------------------------------------------------------ archivos para buscadores
def sitemap(docs):
    urls = "".join(f'''<url><loc>{canon(r)}</loc><lastmod>{FECHA_ISO}</lastmod><changefreq>{"weekly" if r.startswith("blog") or r == "index.html" else "monthly"}</changefreq><priority>{"1.0" if r == "index.html" else "0.9" if t == "Service" else "0.6"}</priority><image:image><image:loc>{img_abs(f)}</image:loc></image:image></url>
''' for r, _, _, _, _, t, f, _ in PAGINAS)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n{urls}</urlset>\n'

ROBOTS = f"""# {MARCA} · robots.txt (sitio {VERSION})
User-agent: *
Allow: /
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

Sitemap: {DOM}/sitemap.xml
"""

def llms():
    servicios = "\n".join(f"- [{n}]({canon(u)})" for n, u in SERVICIOS)
    paginas = "\n".join(f"- [{t.split(' | ')[0]}]({canon(r)}): {d}" for r, _, t, d, _, _, _, _ in PAGINAS)
    return f"""# {MARCA}

> Empresa chilena de transporte, logística y tecnología, con oficina en Mallplaza Norte (Av. Américo Vespucio 1737, piso 8, Huechuraba, Región Metropolitana) y cobertura nacional. Instagram: @{IG_HANDLE} ({IG_URL}). Dos unidades de negocio: traslado de unidades por sus propios medios (camiones, tractos, buses, maquinaria y vehículos livianos manejados por conductores de {MARCA}) y distribución a retail y B2B (carga paletizada desde la bodega central de una marca a supermercados, mejoramiento del hogar y canal ferretero, con cross-docking en menos de 24 horas). Ambas se siguen en línea en {TORRE}: GPS, checklist con fotos, prueba de entrega digital e historial por chasis.

{MARCA} no hace última milla a personas. Trabaja solo con empresas (B2B).

## Servicios
{servicios}

## Páginas
{paginas}

## Contacto
- WhatsApp: {WA_TXT}
- Cotización: {canon("contacto.html")}
"""


def informe_seo():
    """Plan SEO del sitio, generado desde PAGINAS para que no se separe del sitio. Documento interno."""
    filas = "\n".join(f"| `{canon(r)[len(DOM):]}` | {t.replace('|', '·')} ({len(t)}) | {d} ({len(d)}) | {c or '—'} |" for r, _, t, d, _, _, _, c in PAGINAS)
    return f"""# SEO del sitio nuevo de {MARCA} · {VERSION} · {FECHA}

Generado por `build_sitio_wpu.py`: no se edita a mano. Documento interno de Precisión.

## Qué se hizo

1. **Una página por intención de búsqueda.** Cada servicio tiene su propia dirección, su título y su descripción, con la palabra clave principal en el título, la descripción, el H1 y la primera sección.
2. **Títulos de 66 caracteres o menos y descripciones de 110 a 170**, únicos por página. El generador no escribe el sitio si alguno se sale del rango.
3. **Datos estructurados en cada página (JSON-LD):** Organization (con nombres alternativos «We Place U» y «WPU», catálogo de servicios, área de servicio Chile, teléfono comercial), WebSite, WebPage, BreadcrumbList, Service en cada servicio, FAQPage donde hay preguntas y BlogPosting en los artículos.
4. **Respuestas directas y preguntas frecuentes** escritas para que Google y los buscadores con IA las citen tal cual (marcadas con `speakable`).
5. **Open Graph y Twitter Card** con foto propia por página, para que el enlace se vea bien al compartirlo por WhatsApp o LinkedIn.
6. **Imágenes con nombre descriptivo** (`traslado-de-buses-por-sus-propios-medios.webp`), texto alternativo, ancho y alto declarados, dos tamaños por `srcset` y carga diferida fuera de la primera pantalla. La foto de portada se precarga.
7. **`sitemap.xml`** con las 14 páginas y su foto principal, **`robots.txt`** y **`llms.txt`** (resumen de la empresa para buscadores con IA).
8. **Enlaces internos:** migas de pan visibles, servicios relacionados al pie de cada artículo, artículos relacionados y enlaces cruzados entre las unidades, cross-docking y Control Tower.

## Palabras clave, títulos y descripciones por página

| Dirección | Título (caracteres) | Descripción (caracteres) | Palabras clave |
|---|---|---|---|
{filas}

## Al publicar en weplaceu.cl

- [ ] Quitar `noindex, nofollow` (la revisión lo lleva para que nadie indexe la maqueta).
- [ ] Mantener las direcciones de esta tabla como enlaces permanentes de WordPress.
- [ ] Redirección 301: `/politica-de-cookies-ue/` → `/privacidad/`. La portada `/` se mantiene.
- [ ] Subir `sitemap.xml` a Google Search Console y pedir indexación de las páginas de servicio.
- [ ] Copiar `robots.txt` y `llms.txt` a la raíz del dominio.
- [ ] Las etiquetas ya van en cada página: consentimiento por defecto, GTM ({GTM_ID}) con guarda de dominio, noscript y las verificaciones de Google y Meta. **No pegar GA4, el píxel ni HubSpot sueltos**: viven dentro de GTM (detalle en `1 CLIENTES ACTIVOS/WEPLACEU/Etiquetas_WPU.md`).
- [ ] Si el sitio nuevo se monta en WordPress, quitar el fragmento de GTM de WPCode para que no cargue dos veces. Mantener el aviso Complianz: sin él el consentimiento queda denegado y nada mide.
- [ ] Conectar `contacto_formulario` a la confirmación real de HubSpot, no al botón.
- [ ] Probar en el dominio real: sin aceptar el aviso, cero solicitudes a Google Analytics y Meta; al aceptar, `page_view` en G-QYT834NZXB y PageView en el píxel 1170353078726123.
- [ ] Perfil de Negocio de Google: creado el 14-nov-2026 con área de servicio y dirección oculta. Si el sitio publica la dirección, la ficha debe mostrar la misma (ver `1 CLIENTES ACTIVOS/WEPLACEU/Perfil_Google_WPU.md`).
- [ ] Publicar los tres artículos del blog cuando WEPLACEU los apruebe, y uno nuevo al mes.
"""

# ------------------------------------------------------------------ verificación antes de escribir
PROHIBIDAS = ["drivin", "driving", "simpliroute", "beetrack", "bitrac", "volvo", "porsche", "nips", "traverso", "hoffen", "sodimac", "easy", "jumbo",
              "líder", "unimarc", "traindelta", "simma", "fruna", "marco polo", "maqueta comercial", "oferta técnica", "todas las regiones",
              "cualquier región", "todo chile", "istock", "torre de control wpu", "we place u"]

def visible(doc):
    t = re.sub(r'(?s)<script.*?</script>|<style.*?</style>|<head>.*?</head>', '', doc)
    t = re.sub(r'(?s)<p class="rev">.*?</p>|<div class="rev-panel".*?</div></div>|<div class="rev-bar".*?</div></div>', '', t)
    return t

def verificar(docs):
    errores = []
    titulos, descs = {}, {}
    for ruta, doc in docs.items():
        vis = visible(doc)
        texto = re.sub(r"<[^>]+>", " ", vis)
        for w in PROHIBIDAS:
            if re.search(r"\b" + re.escape(w) + r"\b", texto, re.I):
                errores.append(f"{ruta}: aparece «{w}» en el texto visible")
        if re.search(r'alt="[^"]*\b(volvo|red movilidad)\b', vis, re.I):
            errores.append(f"{ruta}: texto alternativo con marca de cliente")
        for m in re.finditer(r"<img(?![^>]*\balt=)", doc):
            errores.append(f"{ruta}: imagen sin texto alternativo")
        base = (OUT / ruta).parent
        enlaces = re.findall(r'(?:href|src)="([^"]+)"', doc) + [u.split()[0] for ss in re.findall(r'(?:srcset|imagesrcset)="([^"]+)"', doc) for u in ss.split(", ")]
        for h in enlaces:
            if h.startswith(("http", "mailto:", "tel:", "#")):
                if h.startswith("#") and len(h) > 1 and f'id="{h[1:]}"' not in doc:
                    errores.append(f"{ruta}: ancla sin destino {h}")
                continue
            dest, _, ancla = h.partition("#")
            dest = dest.split("?")[0]
            p = (base / dest).resolve()
            rel = p.relative_to(OUT.resolve()).as_posix() if str(p).startswith(str(OUT.resolve())) else None
            if rel is None:
                errores.append(f"{ruta}: enlace fuera del sitio {h}")
            elif rel.startswith("img/"):
                if pathlib.Path(rel).name not in {archivo(n) for n in TAM if not n.endswith("-960")} | {archivo(n, a) for n in TAM if not n.endswith("-960") for a in anchos(n)}:
                    errores.append(f"{ruta}: imagen inexistente {h}")
            elif rel.startswith("assets/"):
                pass
            elif rel not in docs:
                errores.append(f"{ruta}: enlace roto {h}")
            elif ancla and f'id="{ancla}"' not in docs[rel]:
                errores.append(f"{ruta}: ancla inexistente {h}")
        # etiquetas: el consentimiento va antes que GTM, GTM solo en el dominio real, y las dos verificaciones de dominio
        cab = doc.split("</head>")[0]
        i_cons, i_gtm = cab.find("gtag('consent','default'"), cab.find("googletagmanager.com/gtm.js")
        if i_cons < 0 or i_gtm < 0 or i_cons > i_gtm:
            errores.append(f"{ruta}: falta el consentimiento por defecto antes de GTM")
        if f"id='+i+dl" not in cab or f"'{GTM_ID}'" not in cab or "location.hostname==='weplaceu.cl'" not in cab:
            errores.append(f"{ruta}: GTM sin {GTM_ID} o sin la guarda de dominio")
        if f'ns.html?id={GTM_ID}' not in doc.split("<body>")[1][:400]:
            errores.append(f"{ruta}: falta el noscript de GTM al inicio del body")
        for m_ in (f'google-site-verification" content="{GSC_VERIF}"', f'facebook-domain-verification" content="{FB_VERIF}"'):
            if cab.count(m_) != 1: errores.append(f"{ruta}: verificación de dominio ausente o repetida ({m_[:28]})")
        if re.search(r"fbq\(|connect\.facebook\.net|G-QYT834NZXB", doc):
            errores.append(f"{ruta}: etiqueta pegada en la página; todo va dentro de GTM")
        h1 = len(re.findall(r"<h1[\s>]", vis))
        if (ruta == "index.html" and h1 != 3) or (ruta != "index.html" and h1 != 1):
            errores.append(f"{ruta}: {h1} títulos h1")
        t = html.unescape(re.search(r"<title>(.*?)</title>", doc).group(1)); d = html.unescape(re.search(r'name="description" content="([^"]*)"', doc).group(1))
        if len(t) > 66: errores.append(f"{ruta}: título de {len(t)} caracteres (máx. 66)")
        if not 110 <= len(d) <= 170: errores.append(f"{ruta}: descripción de {len(d)} caracteres (110–170)")
        if t in titulos: errores.append(f"{ruta}: título repetido con {titulos[t]}")
        if d in descs: errores.append(f"{ruta}: descripción repetida con {descs[d]}")
        titulos[t], descs[d] = ruta, ruta
        for need in ['property="og:image"', 'rel="canonical"', '"BreadcrumbList"', 'name="twitter:card"']:
            if need not in doc: errores.append(f"{ruta}: falta {need}")
        for j in re.findall(r'<script type="application/ld\+json">(.*?)</script>', doc):
            try: json.loads(j)
            except Exception as e: errores.append(f"{ruta}: datos estructurados inválidos ({e})")
        if "@/" in doc:
            errores.append(f"{ruta}: quedó una ruta sin resolver")
    return errores

if __name__ == "__main__":
    for ruta, *_ in PAGINAS:
        pass
    # migas para los datos estructurados (las mismas que se ven en cada página)
    MIGAS.update({r: [("Inicio", "index.html")] + ([(t.split(" | ")[0], r)] if r != "index.html" else []) for r, _, t, *_ in PAGINAS})
    for p in POSTS:
        MIGAS[f'blog/{p["slug"]}.html'] = [("Inicio", "index.html"), ("Blog", "blog.html"), (p["titulo"], f'blog/{p["slug"]}.html')]
    MIGAS["cross-docking.html"] = [("Inicio", "index.html"), ("Distribución a retail y B2B", "distribucion-retail-b2b.html"), ("Cross-docking", "cross-docking.html")]
    docs = {ruta: documento(ruta, clave, titulo, desc, fn(), tipo, foto, claves) for ruta, clave, titulo, desc, fn, tipo, foto, claves in PAGINAS}
    docs = {r: d.replace(" →</", f" {FLECHA}</").replace('class="flecha" aria-hidden="true">→</span>', f'class="flecha" aria-hidden="true">{FLECHA}</span>') for r, d in docs.items()}
    errs = verificar(docs)
    if errs:
        print("NO SE ESCRIBIÓ. Errores:"); [print(" -", e) for e in sorted(set(errs))]; sys.exit(1)
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True); (OUT / "img").mkdir(); (OUT / "blog").mkdir()
    (OUT / "assets" / "sitio.css").write_text(CSS, encoding="utf-8")
    (OUT / "assets" / "sitio.js").write_text(JS, encoding="utf-8")
    (OUT / "assets" / "fuentes").mkdir()
    for _, _, a in FUENTES:
        shutil.copy(AQUI / "nucleo" / "fuentes" / a, OUT / "assets" / "fuentes" / a)
    for n in sorted(USADAS | {"logo_azul"}):
        ext = "png" if n.startswith("logo") else "webp"
        shutil.copy(AQUI / "img" / f"{n}.{ext}", OUT / "img" / archivo(n))
        if anchos(n):
            original = Image.open(AQUI / "img" / f"{n}.{ext}").convert("RGB")
            for a in anchos(n):
                original.resize((a, round(original.height * a / original.width)), Image.LANCZOS).save(
                    OUT / "img" / archivo(n, a), "WEBP", quality=CALIDAD_DERIVADA, method=6)
    for ruta, doc in docs.items():
        (OUT / ruta).write_text(doc, encoding="utf-8")
    (OUT / "sitemap.xml").write_text(sitemap(docs), encoding="utf-8")
    (OUT / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    (OUT / "llms.txt").write_text(llms(), encoding="utf-8")
    (AQUI / "SEO_sitio_WPU.md").write_text(informe_seo(), encoding="utf-8")
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f"WPU_sitio_{VERSION}/" + f.relative_to(OUT).as_posix())
    peso = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"OK sitio/ · {len(docs)} páginas · {len(USADAS)} imágenes · {peso/1024:.0f} KB · {ZIP.name} {ZIP.stat().st_size/1024:.0f} KB · "
          f"{sum(d.count('<p class=\"rev\">') for d in docs.values())} notas de revisión")
