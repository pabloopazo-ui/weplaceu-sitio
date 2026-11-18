# Pasar el sitio nuevo a weplaceu.cl: 15 minutos y sin tocar NIC

**El cambio es subir un archivo y activarlo, y se deshace con un botón.** Se hace dentro del WordPress que hoy sirve weplaceu.cl (`weplaceu.cl/wp-admin`). No se tocan NIC Chile, los DNS, el hosting ni el correo de Google de WEPLACEU. Se ensayó entero el 15-nov-2026 en nuevo.wpu.cl, con los mismos plugins que tiene el sitio actual.

## Cuándo hacerlo

Después de que Carlos e Ignacio aprueben el contenido. Hasta hoy siguen abiertos estos puntos (las notas de revisión del sitio v3.1):

| Punto | Qué falta |
|---|---|
| Correo público | Decidir entre info@weplaceu.cl e info@wpu.cl. Hoy la página de privacidad manda a ejercer derechos por el formulario y WhatsApp |
| Dirección | Confirmar que se publica Mallplaza Norte y si reciben visitas ahí |
| Cifras 90+ y 700+ | Confirmar que siguen vigentes |
| Cross-docking | Confirmar que se ofrece hoy |
| Fotos de bodega | Son de la operación de un ex cliente: hace falta su permiso, o reemplazarlas |
| Nosotros | Historia y equipo: salen de la inducción del lunes 16-nov |
| Blog | Los tres artículos son borradores |
| Privacidad | Validar el texto con su asesor legal (Ley 21.719) |
| PHP del sitio actual | **No bloquea.** weplaceu.cl corre con PHP 7.4.34. El 15-nov, con autorización de Pablo, nuevo.wpu.cl se pasó a 7.4 y se probó lo que corre en el cambio real: las 14 páginas, la 404, sitemap, robots y llms.txt en 200 sin errores; «Volver al sitio anterior» y una nueva activación sin errores; las 14 páginas idénticas antes y después. El registro de errores solo mostró dos avisos de la configuración de PHP del hosting (módulo `redis` cargado dos veces, versión de Imagick), que no vienen del tema. Después se devolvió a 8.3 y las 14 siguieron idénticas. Subir PHP sigue pendiente por seguridad (7.4 ya no recibe parches), no por el cambio |

## El cambio, paso a paso

1. **Respaldo del sitio actual.** En `weplaceu.cl/wp-admin` › All-in-One WP Migration › Exportar › Archivo. Bajarlo al computador. El último es del 14-nov-2026 y está en Descargas.
2. **Subir el tema.** Apariencia › Temas › Añadir tema › Subir tema › elegir `1 CLIENTES ACTIVOS/WEPLACEU/sitio_web/publicar/_respaldo_tema_weplaceu-2026_v1.3.0_publicado_2026-11-15.zip` › Instalar ahora. WordPress acepta hasta 2 GB y el archivo pesa 10 MB.
3. **Activar.** En la pantalla siguiente, «Activar». En ese momento:
   - se crean las 14 páginas;
   - la portada pasa a ser la nueva;
   - el tema anota cómo estaba el sitio para poder volver.
4. **Si alguna página del sitio actual ya existía con la misma dirección** (contacto, nosotros…), entrar a Apariencia › Contenido WEPLACEU › «Volver a importar todo». Hoy el sitio actual solo tiene la portada y la política de cookies, así que no debería hacer falta.
5. **Revisar** con la lista de abajo.

## Qué hace el tema con los plugins del sitio actual

No hay que desactivar ninguno. El tema apaga su salida pública mientras está activo, y si se vuelve atrás, todo queda como estaba.

| Plugin | Qué pasa |
|---|---|
| Complianz | Sigue mostrando el aviso de cookies, con los ajustes de diseño que tenía en WPCode. **No desactivar**: sin el aviso el consentimiento queda denegado y nada mide |
| WPCode | Su encabezado global no sale, porque repetía el consentimiento y Google Tag Manager, que ya trae el tema. Sus fragmentos PHP siguen corriendo |
| Rank Math | No sale su cabecera, su esquema ni sus sitemaps. `/sitemap_index.xml` redirige a `/sitemap.xml` |
| Click to Chat | Su botón no sale. El sitio trae el suyo |
| Elementor (y su versión Pro) | Sus estilos y scripts no cargan |

La portada anterior (`/weplaceu/`) redirige a `/`. La política de cookies de Complianz (`/politica-de-cookies-ue/`) se muestra con el diseño nuevo y sin indexarse.

## Lista de revisión, recién activado

| Revisar | Qué debe pasar |
|---|---|
| `weplaceu.cl` en el teléfono y en el computador | La portada nueva, con el aviso de cookies abajo |
| Ver el código fuente de la portada y buscar `GTM-KD4XDXL3` | Aparece 3 veces: un comentario, el script y el `noscript`. Si aparece más, el encabezado de WPCode sigue saliendo |
| Rechazar las cookies y recargar | Cero solicitudes a Google Analytics y a Meta |
| Aceptar las cookies | `page_view` en GA4 (G-QYT834NZXB) y PageView en el píxel 1170353078726123 |
| `weplaceu.cl/robots.txt` | Debe decir `Allow`, sin `Disallow: /`, y nombrar el sitemap |
| `weplaceu.cl/sitemap.xml` | Las 14 páginas con `weplaceu.cl` |
| Formulario de contacto | Un envío real avisado a WEPLACEU, para ver que llega a su HubSpot y que GA4 marca `contacto_formulario` |
| Search Console | Enviar `https://weplaceu.cl/sitemap.xml`; el anterior era `sitemap_index.xml` |

## Si algo sale mal: volver en un clic

Apariencia › **Contenido WEPLACEU** › **Volver al sitio anterior**. Eso:
- deja activo el tema anterior (Astra);
- devuelve la portada, los enlaces permanentes y la descripción a como estaban;
- pasa las 14 páginas a borrador, sin borrarlas.

Para volver a publicar el sitio nuevo basta con activar otra vez el tema. Se probó ida y vuelta dos veces el 15-nov-2026 en nuevo.wpu.cl y el contenido quedó idéntico.

## Lo que queda después, sin apuro

- Rank Math, Click to Chat y Elementor quedan instalados sin salida. Se pueden desactivar cuando se confirme que no hace falta volver atrás.
- Rank Math tenía la verificación de Search Console; el tema también la trae, así que no se pierde.
- La copia de prueba `nuevo.wpu.cl` puede quedar como respaldo o borrarse después del cambio.
