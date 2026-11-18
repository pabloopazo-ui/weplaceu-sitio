# Sitio WEPLACEU 2026 · código fuente

Repositorio privado de Precisión con el código del sitio nuevo de WEPLACEU (`nuevo.wpu.cl` hoy, `weplaceu.cl` al lanzar).
Se actualiza desde la carpeta de trabajo de Precisión con `exportar_repo.py`: **los cambios se hacen allá o con un pull
request acá, nunca editando el tema directo en el servidor.**

## Cómo se arma

Requiere Python 3 con Pillow (`pip install pillow`).

```bash
python3 build_sitio_wpu.py        # → sitio/ (sitio estático de revisión) y su zip
python3 build_wordpress_wpu.py    # → wordpress/weplaceu-2026/ y wordpress/weplaceu-2026.zip (el tema)
```

`sitio/` y `wordpress/` no se versionan: salen de los dos generadores. `prep_imagenes.py` rehace `img/` desde las
fotos originales, que no están en el repositorio (viven en la carpeta de la cuenta); `img/` ya viene lista.

## Dónde se edita cada cosa

| Qué | Dónde se edita | Quién |
|---|---|---|
| Texto, fotos y orden del contenido de cualquier página | WordPress › Páginas › bloque «HTML personalizado» | Quien tenga usuario Editor o Administrador |
| Artículo nuevo del blog | WordPress › Páginas › Añadir, con **Blog** como página superior | Ídem |
| Página nueva (no artículo) | WordPress › Páginas › Añadir | Ídem |
| Cabecera, menú, pie, estilos, animaciones, formulario | Este repositorio (`build_sitio_wpu.py`, `nucleo/`) → tema nuevo | Precisión |
| Título, descripción, datos estructurados y Open Graph de las 14 páginas base | Este repositorio (`build_sitio_wpu.py`, tabla `PAGINAS`) → tema nuevo | Precisión |

**Desde el tema 1.4.0 el contenido vive en WordPress y el tema no lo vuelve a escribir.** Se quitó «Volver a importar
todo», que reemplazaba las 14 páginas y borraba lo editado. Consecuencia que hay que tener presente: un cambio de
TEXTO hecho en `build_sitio_wpu.py` después del lanzamiento no llega solo a WordPress; se copia a mano al bloque de
la página, o se hace directo en WordPress.

## Cómo se publica un artículo

1. WordPress › Páginas › abrir un artículo existente (por ejemplo «Cross-docking») › en el bloque HTML, copiar todo.
2. Páginas › Añadir › pegar en un bloque «HTML personalizado» › cambiar foto, título, migas, bajada y texto.
3. En «Atributos de página», **Página superior: Blog**. Escribir el **extracto** (es la descripción en Google, 120 a
   155 caracteres) y poner una **imagen destacada** (es la foto de la tarjeta en /blog/).
4. Publicar. El artículo aparece primero en la grilla de /blog/, entra al sitemap con su fecha y lleva sus datos
   estructurados de artículo. En weplaceu.cl queda indexable; en la copia de prueba, no.

Una página escrita en el editor sin copiar diseño también funciona: sale con el marco del sitio, su título como H1 y
el texto en formato de lectura. «Entradas» está oculto en wp-admin porque el sitio no las usa.

## Cómo se publica una versión del tema

1. Subir `VERSION_TEMA` en `build_wordpress_wpu.py` y anotar qué cambió en el comentario de versiones.
2. Generar, revisar en `nuevo.wpu.cl` (wp-admin › Apariencia › Temas › Añadir › Subir › «Reemplazar el instalado»).
3. Respaldar el servidor antes y después (cPanel › Softaculous › Backup) y bajar el respaldo el mismo día.
4. Recién con eso aprobado, la misma versión va a `weplaceu.cl`. El paso a paso del lanzamiento está en `GUIA_CAMBIO_weplaceu.md`.

## Qué no está acá

Respaldos de servidor (llevan la base de datos y `wp-config.php`), fotos originales, maqueta del cliente, capturas y
notas internas de la cuenta. Ninguna clave ni contraseña va en este repositorio: los accesos se piden a Pablo.
