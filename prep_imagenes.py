"""Prepara las imágenes del sitio WPU: recortes sin datos personales ni de clientes, en WebP.

Fuentes: la maqueta de Carlos (láminas de la oferta técnica de agosto, incrustadas en base64)
y las fotos de presentacion/fotos/. Se corre una vez; build_sitio_wpu.py lee img/.
"""
import re, io, base64, hashlib, pathlib
from PIL import Image, ImageFilter, ImageOps

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = next(p for p in AQUI.parents if (p / "CLAUDE.md").is_file())  # raíz del proyecto, a cualquier profundidad (16-nov-2026)
MAQ = RAIZ / "1 CLIENTES ACTIVOS/WEPLACEU/sitio_web/maqueta_cliente" / "WEPLACEU_Maqueta_Con_Textos_e_Imagenes.html"
FOT = AQUI.parent / "presentacion" / "fotos"
OUT = AQUI / "img"; OUT.mkdir(exist_ok=True)

# láminas de la maqueta, por su texto alternativo
t = MAQ.read_text(encoding="utf-8")
lam = {}
for b64, alt in re.findall(r'<img[^>]*?src="data:image/png;base64,([A-Za-z0-9+/=]+)"[^>]*?alt="([^"]*)"', t):
    lam.setdefault(alt, Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB"))

# Calidad (14-nov-2026, pedido de Pablo: «mejora la calidad de las imágenes»).
# Todas a calidad 88 y con un enfoque suave. Las que van de fondo en portada o encabezado se llevan a
# 1920 de ancho si el original es menor (se agrandan con Lanczos y se enfocan); los recortes de la
# plataforma, que son chicos, se agrandan al doble para que no se vean pixelados en la galería.
CALIDAD = 88
FONDOS = {"patio_flota", "tractos_puerto", "tractos_patio", "bodega", "bodega2", "bodega3", "camiones", "camiones_blancos",
          "anden", "anden_bodega", "carga_anden", "panel", "flota", "bus", "aljibe"}
RECORTES = {"torre_mapa", "torre_estados", "torre_checklist", "torre_entrega", "torre_patio", "unidades_tolvas", "unidades_puerto"}

def guardar(img, nombre, ancho=None, q=None):
    if nombre in FONDOS and nombre not in ("bus",):
        ancho = max(ancho or 0, 1920)
    if ancho and img.width > ancho:
        img = img.resize((ancho, round(img.height * ancho / img.width)), Image.LANCZOS)
    elif nombre in FONDOS and ancho and img.width < ancho:
        img = img.resize((ancho, round(img.height * ancho / img.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 70, 2))
    elif nombre in RECORTES:
        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
    img = img.filter(ImageFilter.UnsharpMask(0.8, 35, 3))
    img.save(OUT / f"{nombre}.webp", "WEBP", quality=CALIDAD, method=6)
    if img.width > 1100:   # versión liviana para tarjetas y galerías (el sitio la ofrece por srcset)
        chica = img.resize((960, round(img.height * 960 / img.width)), Image.LANCZOS)
        chica.save(OUT / f"{nombre}-960.webp", "WEBP", quality=CALIDAD, method=6)
    print(nombre, img.size, (OUT / f"{nombre}.webp").stat().st_size)


def tapar(img, cajas, r=8):
    for c in cajas:
        zona = img.crop(c).filter(ImageFilter.GaussianBlur(r))
        img.paste(zona, c[:2])
    return img

# fotos reales de operación
# Zonas a difuminar, en coordenadas de la foto original (QA del 13-nov-2026):
# patentes, rotulación de otra empresa en los camiones, rostros y marcas en cajas.
DIFUMINAR = {
    "camiones": [(1100, 715, 1220, 765), (800, 490, 950, 615), (395, 545, 545, 600), (330, 680, 385, 710), (830, 750, 945, 795)],
    "descarga": [(630, 910, 775, 990), (105, 660, 275, 825), (1040, 575, 1190, 715)],   # original 1600x1200
    "anden": [(1100, 795, 1205, 852)],
    "bodega2": [(15, 840, 210, 1045)],
    "bodega": [],
}
for n, w in [("camiones", 1600), ("bodega", 1400), ("bodega2", 1200), ("anden", 1200), ("descarga", 1200)]:
    im = Image.open(FOT / f"{n}.jpg").convert("RGB")
    guardar(tapar(im, DIFUMINAR[n], 9), n, w, 66)
fl = Image.open(FOT / "flota.jpg").convert("RGB")
fl = tapar(fl, [(430, 700, 510, 745)], 6)                        # patente delantera
guardar(fl.crop((0, 150, fl.width, fl.height)), "flota", 1200)   # sin la marca de agua del logo, arriba a la derecha
for n in ("panel", "panel2"):
    guardar(Image.open(FOT / f"{n}.jpg").convert("RGB"), n, 1280, 80)


# fotos del sitio actual de WPU (biblioteca pública de medios de weplaceu.cl, bajadas el 13-nov-2026
# a fuentes_wpu/). Sin las de iStock, las de la plantilla ni los mosaicos con texto encima.
WEB = AQUI / "fuentes_wpu"
NUEVAS = [  # (archivo, nombre, ancho, zonas a difuminar en coordenadas del original)
    ("2025_09_weplaceu2.jpeg", "bus", 900, [(30, 855, 150, 945)]),                       # patente
    ("2025_09_weplaceu3.jpeg", "tractos_patio", 1280, []),
    ("2025_09_weplaceu4.jpeg", "tractos_puerto", 1280, []),
    ("2025_09_weplaceu6.jpeg", "aljibe", 1052, []),
    ("2025_09_weplaceu7.jpeg", "patio_flota", 1052, []),
    ("2023_10_WhatsApp-Image-2023-10-16-at-12.21.04.jpeg", "anden_bodega", 1024, []),
    ("2023_10_WhatsApp-Image-2023-10-16-at-12.21.04-1.jpeg", "carga_anden", 1024, []),
    ("2023_10_WhatsApp-Image-2023-10-16-at-12.21.04-4.jpeg", "bodega3", 1024, []),
    ("2023_10_weplaceu14.jpg", "camiones_blancos", 800, [(200, 472, 280, 518), (340, 375, 410, 408), (45, 385, 100, 425)]),
]
for arch, nombre, w, zonas in NUEVAS:
    im = Image.open(WEB / arch).convert("RGB")
    guardar(tapar(im, zonas, 9), nombre, w, 70)

# recortes de las láminas: solo la interfaz, sin título ni número de página
mapa = lam["Monitoreo GPS"].crop((757, 345, 1220, 657))
guardar(mapa, "torre_mapa", None, 82)
s02 = lam["Material operacional de WEPLACEU"]
guardar(s02.crop((670, 194, 1280, 480)), "unidades_tolvas", None, 80)
guardar(tapar(s02.crop((670, 489, 1280, 665)), [(230, 120, 315, 145)], 3), "unidades_puerto", None, 80)   # patente trasera
guardar(lam["Checklist digital"].crop((481, 306, 893, 731)), "torre_checklist", None, 82)
guardar(lam["Dashboard real de indicadores WEPLACEU"].crop((135, 502, 790, 658)), "torre_estados", None, 82)
pe = lam["Trazabilidad digital"].crop((666, 319, 1237, 545))   # fotos de entrega, sin la firma de quien recibe
guardar(tapar(pe, [(0, 130, 571, 222)], 1.6), "torre_entrega", None, 82)   # fotos difuminadas: patentes ilegibles
guardar(lam["Gestión de patio"].crop((65, 390, 681, 679)).filter(ImageFilter.GaussianBlur(1.3)), "torre_patio", None, 82)   # números de chasis ilegibles   # sin el título con el nombre del patio

# logo: azul para fondo claro y blanco para fondo oscuro, del archivo del kit de marca
logo = Image.open(AQUI.parent / "assets" / "logo-weplaceu-azul-para-fondo-claro.png").convert("RGBA")
logo.save(OUT / "logo_azul.png")
blanco = Image.new("RGBA", logo.size, (255, 255, 255, 0))
blanco.putalpha(logo.getchannel("A"))
blanco.save(OUT / "logo_blanco.png")
print("logos", logo.size)
