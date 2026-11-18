# SEO del sitio nuevo de WEPLACEU · v3.1 · 15-nov-2026

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
| `/` | WEPLACEU · Traslado de camiones y distribución B2B en Chile (59) | Traslado de camiones, buses y maquinaria por sus propios medios y distribución a retail B2B en Chile, con seguimiento en línea en Control Tower. (144) | transporte por sus propios medios, distribución a retail, logística B2B Chile |
| `/transporte-por-sus-propios-medios/` | Traslado de camiones y buses por sus propios medios · WEPLACEU (62) | Trasladamos camiones, tractos, buses y maquinaria por sus propios medios desde puerto o concesionario, con checklist, GPS y prueba de entrega digital. (150) | traslado de camiones por sus propios medios, traslado de buses, traslado de vehículos pesados |
| `/distribucion-retail-b2b/` | Distribución a retail y transporte de carga B2B · WEPLACEU (58) | Distribución de carga paletizada desde tu bodega a supermercados, mejoramiento del hogar y canal ferretero, con flota propia y prueba de entrega digital. (153) | distribución a retail, transporte de carga B2B, distribución de pallets |
| `/cross-docking/` | Servicio de cross-docking: despacho en menos de 24 h · WEPLACEU (63) | Cross-docking en la Región Metropolitana: recibimos tu carga, la ordenamos por destino y la despachamos en menos de 24 horas, con respaldo de cada entrega. (155) | cross-docking, servicio de cross-docking Santiago, despacho en 24 horas |
| `/torre-de-control/` | Control Tower: seguimiento de flota en línea · WEPLACEU (55) | WEPLACEU Control Tower: monitoreo GPS, checklist con fotos, prueba de entrega descargable e indicadores de cada traslado y despacho, en una sola plataforma. (156) | torre de control logística, seguimiento de flota en línea, prueba de entrega digital |
| `/industrias/` | Transporte para marcas, concesionarios y retail · WEPLACEU (58) | Traslados y distribución para marcas e importadores de camiones y buses, concesionarios, empresas con flota, carroceros y marcas que venden en retail. (150) | transporte para concesionarios, traslado de unidades para importadores, logística para carroceros |
| `/nosotros/` | Nosotros: transporte, logística y tecnología · WEPLACEU (55) | WEPLACEU es una empresa chilena de transporte y logística B2B, construida sobre la confianza y la excelencia operacional, con cobertura nacional. (145) | empresa de transporte B2B Chile, logística integral |
| `/blog/` | Blog de transporte y logística B2B · WEPLACEU (45) | Guías sobre traslado de vehículos por sus propios medios, distribución a retail, cross-docking y seguimiento de carga en línea. (127) | blog logística B2B, guías de transporte |
| `/preguntas-frecuentes/` | Preguntas frecuentes sobre traslados y distribución · WEPLACEU (62) | Respuestas sobre traslados por sus propios medios, distribución a retail, cross-docking y el seguimiento en línea de cada servicio en Control Tower. (148) | preguntas frecuentes traslado de camiones, cross-docking |
| `/contacto/` | Cotizar traslado de unidades o distribución · WEPLACEU (54) | Cotiza un traslado de unidades por sus propios medios, una distribución a retail, cross-docking o una demostración de Control Tower con WEPLACEU. (145) | cotizar traslado de camiones, cotizar distribución |
| `/privacidad/` | Privacidad y datos personales · WEPLACEU (40) | Cómo usa WEPLACEU los datos que entregas en el formulario de contacto, dónde se guardan, por cuánto tiempo y cómo ejercer tus derechos. (135) | — |
| `/blog/traslado-por-sus-propios-medios/` | Qué es el traslado por sus propios medios · WEPLACEU (52) | En qué se diferencia del traslado en cama baja, qué revisa un checklist de retiro y qué respaldo deberías exigir al recibir. Guía de WEPLACEU. (142) | — |
| `/blog/cross-docking/` | Cross-docking: qué es y cómo despachar en menos de 24 h · WEPLACEU (66) | Qué es el cross-docking, en qué se diferencia del almacenaje y qué hay que definir para recibir y despachar carga en menos de 24 horas. (135) | — |
| `/blog/seguimiento-de-carga/` | Seguimiento de carga en línea: qué deberías poder ver · WEPLACEU (64) | Qué información debería mostrarte tu proveedor de transporte en línea y por qué la guía firmada ya no basta. Guía de WEPLACEU. (126) | — |

## Al publicar en weplaceu.cl

- [ ] Quitar `noindex, nofollow` (la revisión lo lleva para que nadie indexe la maqueta).
- [ ] Mantener las direcciones de esta tabla como enlaces permanentes de WordPress.
- [ ] Redirección 301: `/politica-de-cookies-ue/` → `/privacidad/`. La portada `/` se mantiene.
- [ ] Subir `sitemap.xml` a Google Search Console y pedir indexación de las páginas de servicio.
- [ ] Copiar `robots.txt` y `llms.txt` a la raíz del dominio.
- [ ] Las etiquetas ya van en cada página: consentimiento por defecto, GTM (GTM-KD4XDXL3) con guarda de dominio, noscript y las verificaciones de Google y Meta. **No pegar GA4, el píxel ni HubSpot sueltos**: viven dentro de GTM (detalle en `1 CLIENTES ACTIVOS/WEPLACEU/Etiquetas_WPU.md`).
- [ ] Si el sitio nuevo se monta en WordPress, quitar el fragmento de GTM de WPCode para que no cargue dos veces. Mantener el aviso Complianz: sin él el consentimiento queda denegado y nada mide.
- [ ] Conectar `contacto_formulario` a la confirmación real de HubSpot, no al botón.
- [ ] Probar en el dominio real: sin aceptar el aviso, cero solicitudes a Google Analytics y Meta; al aceptar, `page_view` en G-QYT834NZXB y PageView en el píxel 1170353078726123.
- [ ] Perfil de Negocio de Google: creado el 14-nov-2026 con área de servicio y dirección oculta. Si el sitio publica la dirección, la ficha debe mostrar la misma (ver `1 CLIENTES ACTIVOS/WEPLACEU/Perfil_Google_WPU.md`).
- [ ] Publicar los tres artículos del blog cuando WEPLACEU los apruebe, y uno nuevo al mes.
