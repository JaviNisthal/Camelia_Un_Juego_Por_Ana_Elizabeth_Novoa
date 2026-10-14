"""Genera el QR y la diapositiva final a partir de la URL pública DEFINITIVA.

Uso (solo cuando la página ya esté publicada y la hayas abierto en el teléfono):
  python3 tools/make_qr.py https://usuario.github.io/camelia-ra/

Crea entrega/qr_camelia.png y entrega/diapositiva_final.png (1920x1080):
el póster exacto, el QR y la instrucción para el PDF.
"""
import os
import sys
import urllib.parse

import qrcode
from PIL import Image, ImageDraw, ImageFont

from cutout import ROOT

FONTS = os.path.join(ROOT, "tools", "fonts")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    url = sys.argv[1].strip()
    u = urllib.parse.urlparse(url)
    if u.scheme != "https" or not u.netloc or any(x in url for x in ("example", "usuario", "TU-", "localhost")):
        raise SystemExit("La URL debe ser la dirección pública real y empezar por https://")

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=24, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(27, 20, 15), back_color="white").convert("RGB")
    out = os.path.join(ROOT, "entrega", "qr_camelia.png")
    img.save(out)
    print(f"QR: {out} -> {url}")

    poster_path = os.path.join(ROOT, "entrega", "camelia_poster.png")
    if not os.path.exists(poster_path):
        print("Aún no existe entrega/camelia_poster.png; no se genera la diapositiva.")
        return
    slide = Image.new("RGB", (1920, 1080), (27, 20, 15))
    poster = Image.open(poster_path)
    ph = 920
    poster = poster.resize((round(poster.width * ph / poster.height), ph), Image.LANCZOS)
    slide.paste(poster, (100, 80))
    d = ImageDraw.Draw(slide)
    c7 = lambda s: ImageFont.truetype(os.path.join(FONTS, "cinzel-latin-700-normal.woff"), s)
    c9 = ImageFont.truetype(os.path.join(FONTS, "cinzel-latin-900-normal.woff"), 100)
    serif = lambda s: ImageFont.truetype(os.path.join(FONTS, "cormorant-garamond-latin-600-normal.woff"), s)
    x = 100 + poster.width + 110
    d.text((x, 120), "EXPERIENCIA DE REALIDAD AUMENTADA", font=c7(26), fill=(184, 145, 62))
    d.text((x, 170), "CAMELIA", font=c9, fill=(242, 230, 207))
    q = img.resize((360, 360), Image.NEAREST)
    slide.paste(q, (x, 360))
    lines = ["Escanea el QR,", "inicia la cámara", "y enfoca el póster."]
    for k, line in enumerate(lines):
        d.text((x + 410, 395 + k * 66), line, font=serif(56), fill=(242, 230, 207))
    d.text((x, 780), "Necesitas un teléfono y el póster impreso", font=serif(32), fill=(232, 213, 176))
    d.text((x, 822), "o abierto en otra pantalla.", font=serif(32), fill=(232, 213, 176))
    d.text((x, 900), url, font=serif(28), fill=(232, 213, 176))
    d.text((x, 960), "ANA ELIZABETH NOVOA AGUILAR", font=c7(22), fill=(184, 145, 62))
    out2 = os.path.join(ROOT, "entrega", "diapositiva_final.png")
    slide.save(out2)
    print(f"Diapositiva: {out2}")


if __name__ == "__main__":
    main()
