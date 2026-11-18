#!/usr/bin/env python3
"""Tema de WordPress del sitio nuevo de WEPLACEU, armado desde sitio/ (lo que escribe build_sitio_wpu.py).

Uso: python3 build_sitio_wpu.py && python3 build_wordpress_wpu.py   → wordpress/weplaceu-2026.zip

Qué hace:
- Saca de cada página la franja amarilla, el panel y las notas de revisión (Carlos eligió la portada A el 14-nov-2026).
- Separa cada página en tres partes: cabeza (<head>), lo que va antes de <main> y lo que va después.
  La cabeza y los bordes viven en el tema (datos/paginas.json); el contenido de <main> se importa como
  página de WordPress en un bloque «HTML personalizado», editable desde wp-admin.
- Reescribe los enlaces relativos: x.html → /x/, blog/x.html → /blog/x/, img/ y assets/ → carpeta del tema.
- Reemplaza el formulario de revisión por el envío real al formulario de HubSpot de WEPLACEU
  (Hub 52288874, GUID 2d5e998d…), sin pageUri, que es lo que hoy deja pasar el filtro de dominio.
No se edita a mano: manda este generador.
"""
import json, pathlib, posixpath, re, shutil, sys, zipfile

AQUI = pathlib.Path(__file__).resolve().parent
SITIO = AQUI / "sitio"
SALIDA = AQUI / "wordpress"
TEMA = "weplaceu-2026"
DIR_TEMA = SALIDA / TEMA
ZIP = SALIDA / f"{TEMA}.zip"
VERSION_TEMA = "1.4.0"
DOM = "https://weplaceu.cl"
# v1.1.0 (14-nov-2026): sin bloqueo a buscadores en weplaceu.cl. El «noindex» y el robots que cierra todo quedan
# solo para cualquier otro dominio (la copia de prueba nuevo.wpu.cl), igual que la guarda de GTM.
# El tema sirve /robots.txt, /sitemap.xml y /llms.txt con el dominio en que corre.
# v1.2.0 (15-nov-2026, QA de Pablo «mejora todo lo que se pueda»): sitio v3.1 (fuentes propias y fotos de 1440 px);
# la portada pierde la versión B que no se eligió y queda con un solo h1 por pantalla; WordPress deja de mostrar
# el nombre del administrador (?author=, /author/ y la API de usuarios), los feeds y XML-RPC; encabezados de
# seguridad; readme.html y license.txt cerrados; la 404 con su título y sin canónica; caché de un año para
# assets/ (llevan versión en la dirección); limpieza del contenido de ejemplo de WordPress.
# v1.3.0 (15-nov-2026, Pablo: «que esté todo ok para llegar y moverse»): el tema queda listo para activarse en el
# WordPress que hoy sirve weplaceu.cl (Astra + Elementor Pro + Rank Math + Complianz + Click to Chat + WPCode) sin
# tocar ningún plugin: apaga en la parte pública la cabecera de Rank Math, el botón de Click to Chat, el encabezado
# global de WPCode (que repetía el consentimiento y GTM) y los estilos de Elementor/Astra; conserva el aviso de
# Complianz con su diseño; redirige la portada antigua y los sitemaps de Rank Math; muestra con el diseño del sitio
# cualquier otra página publicada (la política de cookies de Complianz). Al activarse guarda cómo estaba el sitio, y
# «Apariencia › Contenido WEPLACEU › Volver al sitio anterior» lo deja igual que antes en un clic.
# v1.4.0 (18-nov-2026, a partir del diagnóstico de Raúl Villarroel): el contenido vive en WordPress y el diseño en el
# repositorio. Se quita «Volver a importar todo», que reescribía las 14 páginas y borraba lo editado. Una página creada
# en WordPress ya no sale con «noindex»: entra al sitemap (que pasa a armarse con lo publicado y toma la fecha de la
# última edición) y, si es hija de «Blog», se publica como artículo con el marco del blog y aparece sola en /blog/.
# Una página que trae su propio diseño (copiada de un artículo existente) se muestra tal cual. «Entradas» se oculta en
# wp-admin: el sitio no las usa. Extracto e imagen destacada de cada página alimentan la descripción y la tarjeta.
HUB, FORM_GUID = "52288874", "2d5e998d-38a1-425d-941a-fa25bc1add00"

if not (SITIO / "index.html").exists():
    sys.exit("Falta sitio/: corre primero build_sitio_wpu.py")

# ------------------------------------------------------------------ limpieza de la revisión
def sin_revision(doc):
    doc = re.sub(r'<div class="rev-bar".*?</div></div>\n?', "", doc, flags=re.S)
    doc = re.sub(r'<div class="rev-panel".*?</div></div>\n?', "", doc, flags=re.S)
    doc = re.sub(r'<p class="rev">.*?</p>', "", doc, flags=re.S)
    doc = doc.replace('<meta name="robots" content="noindex, nofollow">\n', "")   # lo decide el tema según el dominio
    doc = doc.replace(DOM + "/img/", "%%TEMA%%/img/")                             # en WordPress las fotos viven en el tema
    doc = doc.replace('<p class="form-ok" id="formOk" role="status">Revisión: en el sitio publicado esta solicitud llega al equipo comercial de WEPLACEU.</p>',
                      '<p class="form-ok" id="formOk" role="status">Gracias. Recibimos tu solicitud y el equipo comercial de WEPLACEU te va a contactar.</p>'
                      '<p class="form-ok form-error" id="formError" role="alert">No pudimos enviar la solicitud. Escríbenos por WhatsApp y te respondemos.</p>')
    return doc

# ------------------------------------------------------------------ enlaces
def destino(url, dir_pagina):
    """Convierte una ruta relativa del sitio estático en una del WordPress, con marcadores."""
    if re.match(r"^(https?:|mailto:|tel:|#|data:|//|%%)", url) or not url:
        return url
    ruta, _, ancla = url.partition("#")
    ruta, _, query = ruta.partition("?")
    abs_ = posixpath.normpath(posixpath.join(dir_pagina, ruta))
    if abs_.startswith("img/") or abs_.startswith("assets/"):
        nuevo = "%%TEMA%%/" + abs_ + (("?" + query) if query else "")
    elif abs_ == "index.html":
        nuevo = "%%HOME%%/"
    elif abs_.endswith(".html"):
        nuevo = "%%HOME%%/" + abs_[:-5] + "/"
    else:
        return url
    return nuevo + (("#" + ancla) if ancla else "")

def reescribir(fragmento, dir_pagina):
    def attr(m):
        nombre, valor = m.group(1), m.group(2)
        if nombre in ("srcset", "imagesrcset"):
            partes = [p.strip() for p in valor.split(",")]
            valor = ", ".join(" ".join([destino(p.split()[0], dir_pagina)] + p.split()[1:]) for p in partes if p)
        else:
            valor = destino(valor, dir_pagina)
        return f'{nombre}="{valor}"'
    return re.sub(r'\b(href|src|srcset|imagesrcset)="([^"]*)"', attr, fragmento)

# ------------------------------------------------------------------ páginas
paginas = []
for f in sorted(SITIO.rglob("*.html")):
    rel = f.relative_to(SITIO).as_posix()
    doc = sin_revision(f.read_text(encoding="utf-8"))
    d = posixpath.dirname(rel)
    cabeza = doc[doc.index("<head>") + 6: doc.index("</head>")]
    cuerpo = doc[doc.index("<body>") + 6: doc.index("</body>")]
    i_main = cuerpo.index('<main id="contenido">')
    f_main = cuerpo.index("</main>")
    antes = cuerpo[:i_main]
    contenido = cuerpo[i_main + len('<main id="contenido">'): f_main]
    despues = cuerpo[f_main + len("</main>"):]
    # el script del sitio lo pone el tema, con su versión
    despues = re.sub(r'<script src="[^"]*assets/sitio\.js[^"]*"></script>\s*', "", despues)
    titulo = re.search(r"<title>(.*?)</title>", cabeza).group(1).split(" | ")[0]
    ruta = "" if rel == "index.html" else rel[:-5]           # «» es la portada
    paginas.append({"ruta": ruta, "slug": "inicio" if ruta == "" else ruta.split("/")[-1],
                    "padre": posixpath.dirname(ruta) if "/" in ruta else "",
                    "titulo": titulo,
                    "cabeza": reescribir(cabeza, d).strip(), "antes": reescribir(antes, d).strip(),
                    "despues": reescribir(despues, d).strip(), "contenido": reescribir(contenido, d).strip()})
# La portada publicada es la A (Carlos, 14-nov-2026): la B (partida en dos) era solo para revisión.
for p in paginas:
    if p["ruta"] == "":
        p["contenido"], n = re.subn(r'<section class="hero-partida".*?</section>\n?', "", p["contenido"], flags=re.S)
        if n != 1:
            sys.exit("No encontré la versión B de la portada")
paginas.sort(key=lambda p: (p["ruta"].count("/"), p["ruta"] != "", p["ruta"]))   # padres primero

# verificación antes de escribir
errores = []
for p in paginas:
    todo = p["cabeza"] + p["antes"] + p["contenido"] + p["despues"]
    for resto in re.findall(r'(?:href|src|srcset)="(?!%%|https?:|mailto:|tel:|#|data:|//)([^"]+)"', todo):
        errores.append(f"/{p['ruta']}: enlace sin convertir {resto}")
    for marca in ("rev-bar", "rev-panel", 'class="rev"', "Revisión:", 'name="robots"', DOM + "/img/"):
        if marca in todo:
            errores.append(f"/{p['ruta']}: quedó «{marca}»")
    h1 = len(re.findall(r"<h1[\s>]", p["contenido"]))
    if h1 != (2 if p["ruta"] == "" else 1):   # portada: uno en el carrusel de escritorio y otro en la portada móvil, nunca los dos a la vez
        errores.append(f"/{p['ruta']}: {h1} títulos h1")
    if "fonts.googleapis" in todo or "fonts.gstatic" in todo:
        errores.append(f"/{p['ruta']}: pide fuentes a Google")
    if "<main" in p["contenido"] or "</main>" in p["contenido"]:
        errores.append(f"/{p['ruta']}: el contenido trae otro main")
    for img in re.findall(r"%%TEMA%%/(img/[^\s\"?,]+)", todo):
        if not (SITIO / img).exists():
            errores.append(f"/{p['ruta']}: falta {img}")
# archivos para buscadores, con el dominio como marcador
ARCHIVOS = {}
for nombre in ("sitemap.xml", "robots.txt", "llms.txt"):
    txt = (SITIO / nombre).read_text(encoding="utf-8").replace(DOM + "/img/", "%%TEMA%%/img/").replace(DOM, "%%HOME%%")
    if DOM in txt:
        errores.append(f"{nombre}: quedó el dominio fijo")
    ARCHIVOS[nombre] = txt
if ARCHIVOS["sitemap.xml"].count("<loc>%%HOME%%") != 14:
    errores.append("sitemap.xml: no trae las 14 páginas")
if "Sitemap: %%HOME%%/sitemap.xml" not in ARCHIVOS["robots.txt"]:
    errores.append("robots.txt: no apunta al sitemap")
if len(paginas) != 14:
    errores.append(f"se esperaban 14 páginas y hay {len(paginas)}")
if errores:
    print("NO SE ESCRIBIÓ:"); [print(" -", e) for e in sorted(set(errores))]; sys.exit(1)

# ------------------------------------------------------------------ JS: formulario real a HubSpot
js = (SITIO / "assets" / "sitio.js").read_text(encoding="utf-8")
viejo = re.search(r"  var f = document\.getElementById\('formContacto'\);.*?f\.reset\(\); \}\);\n", js, re.S)
if not viejo:
    sys.exit("No encontré el bloque del formulario en sitio.js")
nuevo = f"""  var f = document.getElementById('formContacto');
  if(f) f.addEventListener('submit', function(e){{ e.preventDefault();
    if(!f.reportValidity()) return;
    var v = function(n){{ var el = f.elements[n]; return el ? String(el.value || '').trim() : ''; }};
    var detalle = ['Empresa: ' + v('company'), 'Necesita: ' + v('linea_de_negocio'), '', v('message')].join('\\n').trim();
    var campos = [['email', v('email')], ['firstname', v('firstname')], ['lastname', v('lastname')], ['phone', v('phone')], ['message', detalle]]
      .filter(function(c){{ return c[1]; }}).map(function(c){{ return {{objectTypeId: '0-1', name: c[0], value: c[1]}}; }});
    var hutk = (document.cookie.match(/(?:^|; )hubspotutk=([^;]*)/) || [])[1];
    var cuerpo = {{fields: campos, context: hutk ? {{hutk: hutk}} : {{}}}};   /* sin pageUri: así lo acepta el filtro de dominio de HubSpot */
    var boton = f.querySelector('button[type=submit]'); if(boton) boton.disabled = true;
    var ok = document.getElementById('formOk'), err = document.getElementById('formError');
    if(ok) ok.style.display = 'none'; if(err) err.style.display = 'none';
    fetch('https://api.hsforms.com/submissions/v3/integration/submit/{HUB}/{FORM_GUID}', {{
      method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(cuerpo)}})
    .then(function(r){{ if(!r.ok) throw new Error('HubSpot ' + r.status);
      window.dataLayer.push({{event: 'contacto_formulario'}});
      if(ok) ok.style.display = 'block'; f.reset(); }})
    .catch(function(){{ if(err) err.style.display = 'block'; }})
    .then(function(){{ if(boton) boton.disabled = false; }});
  }});
"""
js = js[:viejo.start()] + nuevo + js[viejo.end():]
css = (SITIO / "assets" / "sitio.css").read_text(encoding="utf-8") + "\n.form-error{background:#fde8e8;color:#8a1c1c}\n" + (
    "/* Aviso de cookies de Complianz: los ajustes que el sitio actual tenía en el encabezado de WPCode (10-nov-2026) */\n"
    ".cmplz-cookiebanner .cmplz-btn.cmplz-accept{background-color:#111C31!important;border-color:#111C31!important;color:#fff!important}\n"
    ".cmplz-cookiebanner .cmplz-link,.cmplz-cookiebanner a{color:#111C31!important}\n"
    "@media (max-width:767px){.cmplz-cookiebanner{padding:14px 16px 10px!important;row-gap:8px!important}"
    ".cmplz-cookiebanner .cmplz-message{font-size:12px!important;line-height:1.35!important;max-height:68px;overflow-y:auto}"
    ".cmplz-cookiebanner .cmplz-buttons{flex-direction:row!important;gap:8px!important}"
    ".cmplz-cookiebanner .cmplz-btn{flex:1 1 0!important;min-width:0!important;height:38px!important;font-size:13px!important;padding:0 6px!important}"
    "body:has(.cmplz-cookiebanner.cmplz-show) .wa-float{display:none!important}}\n")

# ------------------------------------------------------------------ PHP del tema
STYLE = f"""/*
Theme Name: WEPLACEU 2026
Theme URI: https://weplaceu.cl
Author: Precisión
Description: Sitio nuevo de WEPLACEU (14 páginas). Generado por build_wordpress_wpu.py desde build_sitio_wpu.py: no se edita a mano. El contenido vive en WordPress: cada página se edita en wp-admin (bloque HTML personalizado) y el tema no lo vuelve a escribir. Un artículo nuevo es una página hija de Blog. La cabecera, el pie, el diseño y el SEO de las 14 páginas base viven en el repositorio (datos/paginas.json).
Version: {VERSION_TEMA}
Requires at least: 6.0
Requires PHP: 7.4
Text Domain: weplaceu-2026
*/
"""

FUNCTIONS = r"""<?php
/* Tema WEPLACEU 2026 · generado por build_wordpress_wpu.py · no se edita a mano. */
if (!defined('ABSPATH')) exit;

function wpu_datos() {
  static $datos = null;
  if ($datos === null) {
    $datos = array();
    $json = json_decode(file_get_contents(get_template_directory() . '/datos/paginas.json'), true);
    foreach ($json as $p) $datos[$p['ruta']] = $p;
  }
  return $datos;
}
function wpu_marcas($html) {
  return str_replace(array('%%HOME%%', '%%TEMA%%'), array(untrailingslashit(home_url()), get_template_directory_uri()), $html);
}
/* Producción = el dominio real. En cualquier otro (la copia de prueba) el sitio se cierra a buscadores. */
function wpu_es_produccion() {
  $h = strtolower(isset($_SERVER['HTTP_HOST']) ? preg_replace('/:\\d+$/', '', $_SERVER['HTTP_HOST']) : '');
  return in_array($h, array('weplaceu.cl', 'www.weplaceu.cl'), true);
}
/* Páginas publicadas en WordPress que no vienen del tema: artículos nuevos del blog y otras páginas (v1.4.0) */
function wpu_indexable($p) {
  return !preg_match('/cookie|cmplz|complianz/i', $p->post_name);   /* las páginas legales de Complianz no van a buscadores */
}
function wpu_paginas_extra($solo_blog = false) {
  $datos = wpu_datos();
  $args = array('post_type' => 'page', 'post_status' => 'publish', 'numberposts' => -1, 'orderby' => 'date', 'order' => 'DESC', 'has_password' => false);
  if ($solo_blog) {
    $blog = get_page_by_path('blog', OBJECT, 'page');
    if (!$blog) return array();
    $args['post_parent'] = $blog->ID;
  }
  $extra = array();
  foreach (get_posts($args) as $p) {
    $ruta = get_page_uri($p->ID);
    if ((int) get_option('page_on_front') === (int) $p->ID || $ruta === 'inicio' || isset($datos[$ruta]) || !wpu_indexable($p)) continue;
    $extra[] = $p;
  }
  return $extra;
}
/* El sitemap: las 14 páginas base con la fecha de su última edición, más todo lo publicado después en WordPress */
function wpu_sitemap($xml) {
  foreach (wpu_datos() as $ruta => $d) {
    $pg = ($ruta === '') ? get_post((int) get_option('page_on_front')) : get_page_by_path($ruta, OBJECT, 'page');
    if (!$pg) continue;
    $loc = home_url('/' . ($ruta === '' ? '' : $ruta . '/'));
    $xml = preg_replace('#(<loc>' . preg_quote($loc, '#') . '</loc><lastmod>)[0-9-]+#', '${1}' . get_post_modified_time('Y-m-d', false, $pg), $xml);
  }
  $extra = '';
  foreach (wpu_paginas_extra() as $p) {
    $extra .= '<url><loc>' . esc_url(get_permalink($p)) . '</loc><lastmod>' . get_post_modified_time('Y-m-d', false, $p) . '</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>' . "\n";
  }
  return str_replace('</urlset>', $extra . '</urlset>', $xml);
}
/* Extracto e imagen destacada en las páginas: describen un artículo nuevo en Google y en su tarjeta del blog */
add_action('init', function () { add_post_type_support('page', 'excerpt'); });
add_action('after_setup_theme', function () { add_theme_support('post-thumbnails'); });
/* El sitio no usa «Entradas»: un artículo es una página hija de Blog. Se oculta para que nadie publique donde no se ve. */
add_action('admin_menu', function () { remove_menu_page('edit.php'); });
/* /robots.txt, /sitemap.xml y /llms.txt salen del tema, con el dominio en que corre */
add_action('init', function () {
  $ruta = strtolower(parse_url(isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '', PHP_URL_PATH));
  $tipos = array('/robots.txt' => 'text/plain', '/sitemap.xml' => 'application/xml', '/llms.txt' => 'text/plain');
  if (!isset($tipos[$ruta]) && preg_match('#^/[a-z0-9_-]*sitemap[a-z0-9_-]*\.(xml|xsl)$#', $ruta)) {   /* sitemap_index.xml de Rank Math y sus hijos */
    wp_redirect(home_url('/sitemap.xml'), 301); exit;
  }
  if (!isset($tipos[$ruta])) return;
  $archivo = get_template_directory() . '/datos' . $ruta;
  if ($ruta === '/robots.txt' && !wpu_es_produccion()) {
    $txt = "# Copia de prueba de WEPLACEU: cerrada a buscadores. El sitio publico es https://weplaceu.cl\nUser-agent: *\nDisallow: /\n";
  } else {
    $txt = wpu_marcas(file_get_contents($archivo));
    if ($ruta === '/sitemap.xml') $txt = wpu_sitemap($txt);
  }
  status_header(200);
  header('Content-Type: ' . $tipos[$ruta] . '; charset=UTF-8');
  if (!wpu_es_produccion()) header('X-Robots-Tag: noindex, nofollow');
  echo $txt;
  exit;
}, 0);
add_filter('wp_sitemaps_enabled', '__return_false');
add_action('send_headers', function () {
  if (!wpu_es_produccion()) header('X-Robots-Tag: noindex, nofollow');
  header('X-Content-Type-Options: nosniff');
  header('Referrer-Policy: strict-origin-when-cross-origin');
  header('X-Frame-Options: SAMEORIGIN');
  header('Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()');
});

/* Seguridad: WordPress no muestra quién administra el sitio ni sirve lo que el sitio no usa */
add_action('template_redirect', function () {
  if (is_author() || isset($_GET['author'])) { wp_safe_redirect(home_url('/'), 301); exit; }   /* ?author=1 revelaba el usuario */
  if (is_feed()) { wp_safe_redirect(home_url('/'), 301); exit; }                               /* el sitio no tiene entradas */
}, 1);
add_filter('rest_endpoints', function ($e) {
  if (!is_user_logged_in()) { unset($e['/wp/v2/users'], $e['/wp/v2/users/(?P<id>[\\d]+)']); }
  return $e;
});
add_filter('xmlrpc_enabled', '__return_false');
add_filter('wp_headers', function ($h) { unset($h['X-Pingback']); return $h; });

/* Convivencia con los plugins del WordPress que hoy sirve weplaceu.cl. Nada se desactiva: solo se apaga su salida
   pública mientras este tema está activo, así que volver al tema anterior lo deja todo como estaba. */
add_filter('disable_ihaf', '__return_true');   /* WPCode: el encabezado global repetía el consentimiento y GTM, que ya trae el tema */
/* ¿La función viene de uno de esos plugins? Se mira el archivo donde está definida, así cubre también las anónimas. */
function wpu_es_ajeno($cb) {
  $f = $cb['function'];
  try {
    if (is_array($f)) $r = new ReflectionMethod(is_object($f[0]) ? get_class($f[0]) : $f[0], $f[1]);
    elseif (is_string($f) && strpos($f, '::') !== false) $r = new ReflectionMethod($f);
    elseif (is_string($f) || $f instanceof Closure) $r = new ReflectionFunction($f);
    else return false;
    $archivo = wp_normalize_path((string) $r->getFileName());
  } catch (Throwable $e) {
    return false;
  }
  return (bool) preg_match('#/(plugins/(elementor|elementor-pro|seo-by-rank-math|seo-by-rank-math-pro|click-to-chat-for-whatsapp)|themes/astra)/#', $archivo);
}
function wpu_sin_salida_ajena() {
  global $wp_filter;
  foreach (array('wp_head', 'wp_footer', 'get_footer', 'wp_body_open', 'rank_math/head') as $gancho) {
    if (empty($wp_filter[$gancho])) continue;
    foreach ($wp_filter[$gancho]->callbacks as $prioridad => $cbs) {
      foreach ($cbs as $cb) {
        if ($gancho === 'rank_math/head' || wpu_es_ajeno($cb)) remove_action($gancho, $cb['function'], $prioridad);
      }
    }
  }
}
add_action('wp', function () { if (!is_admin()) wpu_sin_salida_ajena(); }, 99);
add_action('wp_head', 'wpu_sin_salida_ajena', -9999);     /* por si un plugin engancha después de «wp» */
add_action('wp_footer', 'wpu_sin_salida_ajena', -9999);
function wpu_ruta_actual() {
  if (is_front_page()) return '';
  if (is_page()) return get_page_uri(get_queried_object_id());
  return null;
}
function wpu_pagina_actual() {
  $datos = wpu_datos();
  $r = wpu_ruta_actual();
  return ($r !== null && isset($datos[$r])) ? $datos[$r] : null;
}

/* Lo que WordPress agrega por su cuenta y que el sitio ya trae (o no necesita) */
add_action('after_setup_theme', function () {
  remove_action('wp_head', 'rel_canonical');
  remove_action('wp_head', 'wp_shortlink_wp_head');
  remove_action('wp_head', 'wp_generator');
  remove_action('wp_head', 'wp_robots', 1);
  remove_action('wp_head', 'print_emoji_detection_script', 7);
  remove_action('wp_print_styles', 'print_emoji_styles');
  remove_action('wp_head', 'rsd_link');
  remove_action('wp_head', 'wlwmanifest_link');
  remove_action('wp_head', 'rest_output_link_wp_head');
  remove_action('wp_head', 'wp_oembed_add_discovery_links');
  remove_action('wp_head', 'feed_links', 2);
  remove_action('wp_head', 'feed_links_extra', 3);
  remove_filter('the_content', 'wptexturize');
  remove_filter('the_content', 'convert_smilies', 20);
  remove_filter('the_content', 'wp_filter_content_tags', 12);
  remove_filter('the_content', 'wpautop');
});
function wpu_sin_estilos_de_bloques() {
  foreach (array('wp-block-library', 'wp-block-library-theme', 'global-styles', 'classic-theme-styles', 'wp-img-auto-sizes-contain', 'core-block-supports') as $h) {
    wp_dequeue_style($h);
  }
  if (is_admin()) return;
  /* estilos y scripts de Elementor, Astra, Click to Chat y Rank Math: el sitio no los usa. Complianz (cmplz) se queda. */
  foreach (array(wp_styles(), wp_scripts()) as $cola) {
    foreach ((array) $cola->queue as $h) {
      if (preg_match('/^(elementor|e-|swiper|font-awesome|fontawesome|astra|ht_ctc|ht-ctc|ctc|rank-math|wpcode)/i', $h)) {
        $cola === wp_styles() ? wp_dequeue_style($h) : wp_dequeue_script($h);
      }
    }
  }
}
add_action('wp_enqueue_scripts', 'wpu_sin_estilos_de_bloques', 100);
add_action('wp_print_styles', 'wpu_sin_estilos_de_bloques', 0);     /* justo antes de imprimirlos en la cabecera */
add_action('wp_print_footer_scripts', 'wpu_sin_estilos_de_bloques', 0);
add_filter('show_admin_bar', '__return_false');

/* Cambia solo el estado de una página. wp_update_post volvería a guardar el contenido y, con los filtros de seguridad
   de WordPress activos, reescribe los «&» de los enlaces de mapas como «&amp;». */
function wpu_estado($id, $estado) {
  global $wpdb;
  $wpdb->update($wpdb->posts, array('post_status' => $estado), array('ID' => (int) $id));
  clean_post_cache((int) $id);
}

/* Importa (o vuelve a importar) las 14 páginas desde datos/paginas.json */
function wpu_importar($pisar = false) {
  if (function_exists('kses_remove_filters')) kses_remove_filters();
  $hechas = array(); $ids = array();
  foreach (wpu_datos() as $ruta => $p) {
    $contenido = "<!-- wp:html -->\n" . wpu_marcas($p['contenido']) . "\n<!-- /wp:html -->";
    $existe = get_page_by_path($ruta === '' ? 'inicio' : $ruta, OBJECT, 'page');
    $padre = ($p['padre'] !== '' && isset($ids[$p['padre']])) ? $ids[$p['padre']] : 0;
    if ($existe && !$pisar) {
      if ($existe->post_status !== 'publish') wpu_estado($existe->ID, 'publish');   /* la vuelta atrás las deja en borrador */
      $ids[$ruta] = $existe->ID; continue;
    }
    $post = array('post_type' => 'page', 'post_status' => 'publish', 'post_title' => $p['titulo'],
                  'post_name' => $p['slug'], 'post_parent' => $padre, 'post_content' => $contenido,
                  'comment_status' => 'closed', 'ping_status' => 'closed');
    if ($existe) { $post['ID'] = $existe->ID; $id = wp_update_post(wp_slash($post), true); }
    else { $id = wp_insert_post(wp_slash($post), true); }
    if (!is_wp_error($id)) { $ids[$ruta] = $id; $hechas[] = '/' . $ruta; }
  }
  if (isset($ids[''])) { update_option('show_on_front', 'page'); update_option('page_on_front', $ids['']); }
  update_option('permalink_structure', '/%postname%/');
  update_option('blogname', 'WEPLACEU');
  update_option('blogdescription', 'Movemos tu operación. Conectamos tu negocio.');
  update_option('timezone_string', 'America/Santiago');
  update_option('default_comment_status', 'closed');
  update_option('blog_public', 1);   /* el cierre de la copia de prueba lo hace wpu_es_produccion(), no este ajuste */
  flush_rewrite_rules();
  return $hechas;
}
/* El cambio: al activar el tema se guarda cómo estaba el sitio (una sola vez) y se importan las páginas */
add_action('after_switch_theme', function ($nombre_viejo = '', $tema_viejo = null) {
  if (!get_option('wpu_cambio')) {
    $viejo = ($tema_viejo instanceof WP_Theme) ? $tema_viejo->get_stylesheet() : (string) get_option('theme_switched');
    if ($viejo && $viejo !== get_stylesheet()) {
      update_option('wpu_cambio', array('tema' => $viejo, 'show_on_front' => get_option('show_on_front'),
        'page_on_front' => (int) get_option('page_on_front'), 'permalink_structure' => get_option('permalink_structure'),
        'blogdescription' => get_option('blogdescription'), 'fecha' => current_time('mysql')), false);
    }
  }
  wpu_importar(false);
}, 10, 2);

/* La vuelta atrás: deja el sitio como estaba antes de activar este tema */
function wpu_volver() {
  $c = get_option('wpu_cambio');
  if (!$c || !wp_get_theme($c['tema'])->exists()) return false;
  foreach (array_reverse(wpu_datos(), true) as $ruta => $p) {   /* hijas primero */
    $pg = get_page_by_path($ruta === '' ? 'inicio' : $ruta, OBJECT, 'page');
    if ($pg && $pg->post_status === 'publish') wpu_estado($pg->ID, 'draft');
  }
  foreach (array('show_on_front', 'page_on_front', 'permalink_structure', 'blogdescription') as $o) update_option($o, $c[$o]);
  require_once ABSPATH . 'wp-admin/includes/file.php';
  require_once ABSPATH . 'wp-admin/includes/misc.php';
  insert_with_markers(get_home_path() . '.htaccess', 'WEPLACEU 2026', array());
  delete_option('wpu_cambio');
  delete_option('wpu_tema_version');
  switch_theme($c['tema']);
  flush_rewrite_rules();
  return $c['tema'];
}

/* La portada anterior redirige a la nueva */
add_action('template_redirect', function () {
  $c = get_option('wpu_cambio');
  if ($c && !empty($c['page_on_front']) && (int) $c['page_on_front'] !== (int) get_option('page_on_front') && is_page((int) $c['page_on_front'])) {
    wp_safe_redirect(home_url('/'), 301); exit;
  }
}, 2);

/* Una vez por versión del tema, al entrar a wp-admin: limpia el contenido de ejemplo y cierra archivos que delatan la versión */
function wpu_actualizar() {
  foreach (array(array('hello-world', 'post'), array('sample-page', 'page'), array('privacy-policy', 'page')) as $x) {
    $p = get_page_by_path($x[0], OBJECT, $x[1]);
    if ($p && $p->post_status !== 'trash') wp_trash_post($p->ID);   /* a la papelera, no se borra */
  }
  $priv = get_page_by_path('privacidad', OBJECT, 'page');
  if ($priv) update_option('wp_page_for_privacy_policy', $priv->ID);
  require_once ABSPATH . 'wp-admin/includes/file.php';
  require_once ABSPATH . 'wp-admin/includes/misc.php';
  insert_with_markers(get_home_path() . '.htaccess', 'WEPLACEU 2026', array(
    '<FilesMatch "^(readme\\.html|license\\.txt|wp-config-sample\\.php)$">', 'Require all denied', '</FilesMatch>'));
}
add_action('admin_init', function () {
  $v = wp_get_theme()->get('Version');
  if (get_option('wpu_tema_version') === $v || !current_user_can('manage_options')) return;
  wpu_actualizar();
  update_option('wpu_tema_version', $v);
});

/* Herramienta en wp-admin: Apariencia → Contenido WEPLACEU */
add_action('admin_menu', function () {
  add_theme_page('Contenido WEPLACEU', 'Contenido WEPLACEU', 'manage_options', 'wpu-contenido', function () {
    echo '<div class="wrap"><h1>Contenido WEPLACEU</h1>';
    if (isset($_GET['hecho'])) echo '<div class="notice notice-success"><p>Páginas importadas: ' . intval($_GET['hecho']) . '.</p></div>';
    echo '<p>El tema trae las 14 páginas base del sitio. <strong>El contenido vive en WordPress</strong>: cada página se edita en Páginas (bloque «HTML personalizado») y el tema no lo vuelve a escribir. «Crear las que faltan» solo crea las que no existan.</p>';
    echo '<p><strong>Artículo nuevo:</strong> Páginas › Añadir, con «Blog» como página superior. Lo más rápido es copiar el bloque HTML de un artículo existente y cambiar foto, título y texto. Aparece solo en /blog/ y en el sitemap. El extracto se usa como descripción en Google y la imagen destacada en la tarjeta.</p>';
    /* estado del cambio: lo que el tema apaga en la parte pública, sin desactivar nada */
    $activos = (array) get_option('active_plugins');
    $vistos = array('seo-by-rank-math/' => 'Rank Math: su cabecera, su esquema y sus sitemaps no salen; manda la del tema',
      'click-to-chat-for-whatsapp/' => 'Click to Chat: su botón no sale; el sitio trae el suyo', 'insert-headers-and-footers/' => 'WPCode: su encabezado global no sale (repetía el consentimiento y GTM); sus fragmentos PHP siguen corriendo',
      'elementor/' => 'Elementor: sus estilos, sus scripts y su etiqueta «generator» no salen en las páginas del sitio', 'complianz-gdpr/' => 'Complianz: el aviso de cookies sigue funcionando, con el diseño del sitio');
    echo '<h2>Convivencia con los plugins</h2><ul style="list-style:disc;padding-left:1.5em">';
    $alguno = false;
    foreach ($vistos as $pre => $txt) foreach ($activos as $a) if (strpos($a, $pre) === 0) { echo '<li>' . esc_html($txt) . '</li>'; $alguno = true; break; }
    if (!$alguno) echo '<li>Ninguno de los plugins del sitio actual está activo aquí.</li>';
    echo '</ul>';
    $c = get_option('wpu_cambio');
    if ($c) {
      echo '<h2>Volver al sitio anterior</h2><p>Este tema se activó el ' . esc_html($c['fecha']) . ' en reemplazo de «' . esc_html($c['tema']) . '». Volver deja ese tema activo, la portada, los enlaces permanentes y la descripción como estaban, y pasa las 14 páginas a borrador (no se borran). Para volver a publicar el sitio nuevo basta con activar este tema otra vez.</p>';
      echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
      wp_nonce_field('wpu_volver');
      echo '<input type="hidden" name="action" value="wpu_volver">';
      submit_button('Volver al sitio anterior', 'delete', 'submit', false, array('onclick' => "return confirm('Se vuelve al tema anterior y las 14 páginas pasan a borrador. ¿Seguir?')"));
      echo '</form>';
    }
    /* v1.4.0: ya no existe «Volver a importar todo»; reescribía las 14 páginas y borraba lo editado en wp-admin */
    echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
    wp_nonce_field('wpu_importar');
    echo '<input type="hidden" name="action" value="wpu_importar">';
    submit_button('Crear las que faltan', 'primary', 'submit', false);
    echo '</form>';
    echo '</div>';
  });
});
add_action('admin_post_wpu_volver', function () {
  if (!current_user_can('switch_themes')) wp_die('Sin permiso');
  check_admin_referer('wpu_volver');
  $t = wpu_volver();
  wp_safe_redirect($t ? admin_url('themes.php?volvio=1') : admin_url('themes.php?page=wpu-contenido'));
  exit;
});
add_action('admin_post_wpu_importar', function () {
  if (!current_user_can('manage_options')) wp_die('Sin permiso');
  check_admin_referer('wpu_importar');
  $hechas = wpu_importar(false);   /* nunca pisa lo editado */
  wp_safe_redirect(admin_url('themes.php?page=wpu-contenido&hecho=' . count($hechas)));
  exit;
});
"""

INDEX = r"""<?php
/* Plantilla única del sitio WEPLACEU 2026 · generada por build_wordpress_wpu.py */
if (!defined('ABSPATH')) exit;
$wpu = wpu_pagina_actual();
if (!$wpu && is_page() && have_posts()) {
  /* página publicada en WordPress que no viene del tema: un artículo nuevo (hija de Blog), la política de cookies de Complianz… */
  $datos = wpu_datos();
  $pg = get_queried_object();
  $es_articulo = $pg->post_parent && get_page_uri($pg->post_parent) === 'blog';
  $wpu = $datos[$es_articulo ? 'blog/cross-docking' : 'privacidad'];   /* el marco del blog marca «Blog» en el menú */
  $wpu['generica'] = true;
  $wpu['propia'] = (bool) preg_match('#^\s*(<!-- wp:html -->\s*)?<section#', $pg->post_content);   /* trae su propio diseño, copiado de un artículo */
  $wpu['noindex'] = !wpu_indexable($pg) || post_password_required($pg);
  $titulo = esc_html(wp_strip_all_tags(get_the_title($pg))) . ' | WEPLACEU';
  $url = esc_url(get_permalink($pg));
  $desc = has_excerpt($pg) ? esc_attr(wp_strip_all_tags(get_the_excerpt($pg))) : '';
  $wpu['cabeza'] = preg_replace('#<title>.*?</title>#s', '<title>' . $titulo . '</title>', $wpu['cabeza']);
  $wpu['cabeza'] = preg_replace('#<link rel="(canonical|alternate)"[^>]*>|<meta (name|property)="(description|og:[a-z:]+|twitter:[a-z:]+)"[^>]*>|<link rel="preload" as="image"[^>]*>|<script type="application/ld\+json">.*?</script>#s', '', $wpu['cabeza']);
  $wpu['cabeza'] .= "\n" . '<link rel="canonical" href="' . $url . '">' . "\n" . '<meta property="og:title" content="' . $titulo . '">'
    . "\n" . '<meta property="og:url" content="' . $url . '">' . "\n" . '<meta property="og:type" content="' . ($es_articulo ? 'article' : 'website') . '">';
  if ($desc) $wpu['cabeza'] .= "\n" . '<meta name="description" content="' . $desc . '">' . "\n" . '<meta property="og:description" content="' . $desc . '">';
  if (has_post_thumbnail($pg)) $wpu['cabeza'] .= "\n" . '<meta property="og:image" content="' . esc_url(get_the_post_thumbnail_url($pg, 'full')) . '">';
  if ($es_articulo) $wpu['cabeza'] .= "\n" . '<script type="application/ld+json">' . wp_json_encode(array('@context' => 'https://schema.org', '@type' => 'BlogPosting',
    'headline' => wp_strip_all_tags(get_the_title($pg)), 'datePublished' => get_post_time('c', false, $pg), 'dateModified' => get_post_modified_time('c', false, $pg),
    'mainEntityOfPage' => get_permalink($pg), 'author' => array('@type' => 'Organization', 'name' => 'WEPLACEU'), 'publisher' => array('@type' => 'Organization', 'name' => 'WEPLACEU'))) . '</script>';
} elseif (!$wpu) {
  $datos = wpu_datos();
  $wpu = $datos[''];
  if (!is_404()) status_header(404);
  $wpu['contenido_404'] = true;
  /* la 404 no hereda el título, la canónica ni los datos estructurados de la portada */
  $wpu['cabeza'] = preg_replace('#<title>.*?</title>#s', '<title>Página no encontrada | WEPLACEU</title>', $wpu['cabeza']);
  $wpu['cabeza'] = preg_replace('#<link rel="(canonical|alternate)"[^>]*>|<meta (property|name)="(og:url|og:title|twitter:title)"[^>]*>|<link rel="preload" as="image"[^>]*>|<script type="application/ld\+json">.*?</script>#s', '', $wpu['cabeza']);
}
$version = wp_get_theme()->get('Version');
?><!DOCTYPE html>
<html lang="es-CL">
<head>
<?php echo wpu_marcas($wpu['cabeza']); ?>
<?php if (!wpu_es_produccion() || !empty($wpu['contenido_404']) || !empty($wpu['noindex'])) echo '<meta name="robots" content="noindex, nofollow">' . "\n"; ?>
<?php wp_head(); ?>
</head>
<body>
<?php echo wpu_marcas($wpu['antes']); ?>
<main id="contenido"><?php
if (!empty($wpu['contenido_404'])) {
  echo '<section class="section-pad"><div class="wrap"><h1>No encontramos esta página</h1><p class="lead">Puede que la dirección haya cambiado. <a href="' . esc_url(home_url('/')) . '">Volver al inicio</a> o <a href="' . esc_url(home_url('/contacto/')) . '">escríbenos</a>.</p></div></section>';
} elseif (!empty($wpu['generica']) && empty($wpu['propia'])) {
  add_filter('the_content', 'wpautop');   /* una página escrita en WordPress sí necesita sus párrafos */
  while (have_posts()) { the_post(); echo '<section class="section-pad"><div class="wrap prosa"><h1>' . esc_html(get_the_title()) . '</h1>'; the_content(); echo '</div></section>'; }
} elseif (wpu_ruta_actual() === 'blog') {
  /* /blog/: los artículos publicados en WordPress entran primero en la grilla, sin tocar el contenido de la página */
  ob_start();
  while (have_posts()) { the_post(); the_content(); }
  $html = ob_get_clean();
  $tarjetas = '';
  foreach (wpu_paginas_extra(true) as $p) {
    $u = esc_url(get_permalink($p));
    $foto = has_post_thumbnail($p) ? '<a class="ph" href="' . $u . '" tabindex="-1" aria-hidden="true">' . get_the_post_thumbnail($p, 'large', array('alt' => '', 'loading' => 'lazy', 'decoding' => 'async')) . '</a>' : '';
    $tarjetas .= '<article class="post reveal">' . $foto . '<div class="body"><span class="tag">Artículo</span><h3><a href="' . $u . '">' . esc_html(wp_strip_all_tags(get_the_title($p))) . '</a></h3>'
      . (has_excerpt($p) ? '<p>' . esc_html(wp_strip_all_tags(get_the_excerpt($p))) . '</p>' : '') . '<a class="go" href="' . $u . '">Leer el artículo</a></div></article>';
  }
  if ($tarjetas && strpos($html, '<div class="g3">') !== false) $html = preg_replace('#<div class="g3">#', '<div class="g3">' . str_replace(array('\\', '$'), array('\\\\', '\\$'), $tarjetas), $html, 1);
  elseif ($tarjetas) $html .= '<section class="section-pad"><div class="wrap"><div class="g3">' . $tarjetas . '</div></div></section>';
  echo $html;
} else {
  while (have_posts()) { the_post(); the_content(); }
}
?></main>
<?php echo wpu_marcas($wpu['despues']); ?>
<script src="<?php echo esc_url(get_template_directory_uri() . '/assets/sitio.js?v=' . $version); ?>"></script>
<?php wp_footer(); ?>
</body>
</html>
"""

# ------------------------------------------------------------------ escribir
if DIR_TEMA.exists():
    shutil.rmtree(DIR_TEMA)
(DIR_TEMA / "datos").mkdir(parents=True)
(DIR_TEMA / "assets").mkdir()
shutil.copytree(SITIO / "assets" / "fuentes", DIR_TEMA / "assets" / "fuentes")
shutil.copytree(SITIO / "img", DIR_TEMA / "img")
(DIR_TEMA / "assets" / "sitio.js").write_text(js, encoding="utf-8")
(DIR_TEMA / "assets" / "sitio.css").write_text(css, encoding="utf-8")
(DIR_TEMA / "style.css").write_text(STYLE, encoding="utf-8")
(DIR_TEMA / "functions.php").write_text(FUNCTIONS, encoding="utf-8")
(DIR_TEMA / "index.php").write_text(INDEX, encoding="utf-8")
(DIR_TEMA / "datos" / "paginas.json").write_text(json.dumps(paginas, ensure_ascii=False, indent=0), encoding="utf-8")
(DIR_TEMA / "datos" / ".htaccess").write_text("Require all denied\n", encoding="utf-8")
# assets/ lleva versión en la dirección (?v=), así que el navegador lo guarda un año. img/ queda con la caché del hosting.
(DIR_TEMA / "assets" / ".htaccess").write_text('<IfModule mod_headers.c>\nHeader set Cache-Control "public, max-age=31536000, immutable"\n</IfModule>\n', encoding="utf-8")
for nombre, txt in ARCHIVOS.items():
    (DIR_TEMA / "datos" / nombre).write_text(txt, encoding="utf-8")
# captura del tema para wp-admin
shutil.copy(SITIO / "img" / "logo-weplaceu.png", DIR_TEMA / "screenshot.png")
if ZIP.exists():
    ZIP.unlink()
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(DIR_TEMA.rglob("*")):
        if f.is_file():
            z.write(f, f"{TEMA}/" + f.relative_to(DIR_TEMA).as_posix())
print(f"OK {ZIP.relative_to(AQUI)} · {len(paginas)} páginas · {ZIP.stat().st_size/1024:.0f} KB")
for p in paginas:
    print(f"  /{p['ruta']}{'/' if p['ruta'] else ''}  ← {p['titulo']}  (padre: {p['padre'] or '—'})")
