"""Genera los iconos y las pantallas de carga de la app del cliente a partir del logo.

Uso (desde la raiz del proyecto):
    python scripts/gen_icons.py android/app/src/main/res [ruta del logo]

Crea en la carpeta res indicada:
  - mipmap-*/ic_launcher.png y ic_launcher_round.png (iconos clasicos, Android 7.1 y anteriores)
  - mipmap-*/ic_launcher_foreground.png (primer plano del icono adaptativo, 108 dp, logo dentro de la zona segura)
  - drawable*/splash.png (pantalla de carga, mismas medidas que las de Capacitor)
El fondo del icono adaptativo NO lo crea este script: es res/values/ic_launcher_background.xml (#1A202C).
Requiere Pillow. Fondo: azul medianoche #1A202C (paleta oficial de DeliveryOS).
"""
import os
import sys

from PIL import Image, ImageDraw

LOGO_POR_DEFECTO = r"C:\Users\jairo\Documents\Proyectos Python\logos\logo_solo.png"
BG = (26, 32, 44, 255)  # #1A202C

if len(sys.argv) < 2:
    sys.exit(__doc__)
dest = sys.argv[1]
logo = sys.argv[2] if len(sys.argv) > 2 else LOGO_POR_DEFECTO
src = Image.open(logo).convert("RGBA")
src = src.crop(src.getchannel("A").getbbox())  # recortar al contenido: se centra lo que se ve


def logo_w(width):
    h = round(src.height * width / src.width)
    return src.resize((max(1, round(width)), max(1, h)), Image.LANCZOS)


def centrado(canvas, im):
    canvas.alpha_composite(im, ((canvas.width - im.width) // 2, (canvas.height - im.height) // 2))
    return canvas


def supermuestreo(size, dibujar, k=4):
    """Dibuja a k veces el tamano y reduce: bordes suaves."""
    return dibujar(size * k).resize((size, size), Image.LANCZOS)


# ---- iconos adaptativos (108 dp) y clasicos (48 dp)
DENS = {"mdpi": 1.0, "hdpi": 1.5, "xhdpi": 2.0, "xxhdpi": 3.0, "xxxhdpi": 4.0}
for d, f in DENS.items():
    out = os.path.join(dest, f"mipmap-{d}")
    os.makedirs(out, exist_ok=True)
    # primer plano adaptativo: capa transparente de 108 dp con el logo dentro de la zona segura (66 dp)
    C = round(108 * f)
    fg = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    centrado(fg, logo_w(C * 0.52)).save(os.path.join(out, "ic_launcher_foreground.png"))

    S = round(48 * f)

    def cuadrado(sz):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle((0, 0, sz - 1, sz - 1), radius=round(sz * 0.2), fill=BG)
        return centrado(im, logo_w(sz * 0.72))

    def redondo(sz):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse((0, 0, sz - 1, sz - 1), fill=BG)
        return centrado(im, logo_w(sz * 0.64))

    supermuestreo(S, cuadrado).save(os.path.join(out, "ic_launcher.png"))
    supermuestreo(S, redondo).save(os.path.join(out, "ic_launcher_round.png"))


# ---- pantallas de carga (mismas medidas que las de Capacitor)
SPLASH = {
    "drawable": (480, 320),
    "drawable-land-mdpi": (480, 320), "drawable-land-hdpi": (800, 480), "drawable-land-xhdpi": (1280, 720),
    "drawable-land-xxhdpi": (1600, 960), "drawable-land-xxxhdpi": (1920, 1280),
    "drawable-port-mdpi": (320, 480), "drawable-port-hdpi": (480, 800), "drawable-port-xhdpi": (720, 1280),
    "drawable-port-xxhdpi": (960, 1600), "drawable-port-xxxhdpi": (1280, 1920),
}
for carpeta, (w, h) in SPLASH.items():
    out = os.path.join(dest, carpeta)
    os.makedirs(out, exist_ok=True)
    im = Image.new("RGBA", (w, h), BG)
    ancho = min(w * 0.42, h * 0.42 / (src.height / src.width))  # nunca mas alto que el 42 % de la pantalla
    centrado(im, logo_w(ancho)).convert("RGB").save(os.path.join(out, "splash.png"), optimize=True)

print("listo:", dest)
