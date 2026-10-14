"""Compone el póster vertical (A4 a 300 ppp) con la arena de fondo y Camelia en pose de acción.

Uso:
  python3 tools/make_poster.py --arena source/Camelia_ambientacion_principal.png \
                               --figura source/Camelia_pose_accion.png

La figura puede tener fondo blanco o transparente. El resultado,
entrega/camelia_poster.png, es EXACTAMENTE la imagen que debe compilarse
en assets/targets.mind (tools/compile_targets.mjs lo comprueba con su huella SHA-256).
"""
import argparse
import hashlib
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from cutout import ROOT, bbox, foreground_mask, load_rgba, to_transparent, update_config

W, H = 2480, 3508
FONTS = os.path.join(ROOT, "tools", "fonts")
ORO = (184, 145, 62)
PERGAMINO = (242, 230, 207)
NOCHE = (27, 20, 15)


def cover(img, w, h, focus_y=0.5):
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = (img.width - w) // 2
    y = int((img.height - h) * focus_y)
    return img.crop((x, y, x + w, y + h))


def vertical_shade(top_h, bottom_h):
    a = np.zeros((H, 1), np.float32)
    t = np.linspace(1, 0, top_h) ** 1.4
    a[:top_h, 0] = 0.9 * t
    b = np.linspace(0, 1, bottom_h) ** 1.4
    a[H - bottom_h:, 0] = 0.92 * b
    alpha = (np.repeat(a, W, axis=1) * 255).astype(np.uint8)
    layer = Image.new("RGBA", (W, H), NOCHE + (0,))
    layer.putalpha(Image.fromarray(alpha))
    return layer


def centered(d, y, text, font, fill, spacing=0):
    if spacing:
        widths = [d.textlength(c, font=font) for c in text]
        total = sum(widths) + spacing * (len(text) - 1)
        x = (W - total) / 2
        for c, w in zip(text, widths):
            d.text((x, y), c, font=font, fill=fill)
            x += w + spacing
    else:
        w = d.textlength(text, font=font)
        d.text(((W - w) / 2, y), text, font=font, fill=fill)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arena", required=True)
    ap.add_argument("--figura", required=True, help="Camelia en pose de acción, cuerpo completo")
    ap.add_argument("--focus-y", type=float, default=0.55, help="0 = parte alta de la arena, 1 = parte baja")
    ap.add_argument("--figura-alto", type=float, default=0.62, help="alto de la figura respecto al póster")
    args = ap.parse_args()

    poster = cover(Image.open(args.arena).convert("RGB"), W, H, args.focus_y).convert("RGBA")
    poster.alpha_composite(vertical_shade(1150, 1000))

    rgba = load_rgba(args.figura)
    fg = foreground_mask(rgba)
    fig = to_transparent(rgba, fg)
    y0, y1, x0, x1 = bbox(fig[..., 3] > 16)
    fig = Image.fromarray(fig[y0:y1, x0:x1])
    fh = int(H * args.figura_alto)
    fw = round(fig.width * fh / fig.height)
    if fw > W * 0.95:
        fw = int(W * 0.95)
        fh = round(fig.height * fw / fig.width)
    fig = fig.resize((fw, fh), Image.LANCZOS)
    feet_y = int(H * 0.86)
    fx, fy = (W - fw) // 2, feet_y - fh

    # sombra suave en el suelo
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([W / 2 - fw * 0.38, feet_y - 40, W / 2 + fw * 0.38, feet_y + 40], fill=(20, 12, 6, 150))
    poster.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(30)))
    poster.alpha_composite(fig, (fx, fy))

    d = ImageDraw.Draw(poster)
    cinzel9 = ImageFont.truetype(os.path.join(FONTS, "cinzel-latin-900-normal.woff"), 400)
    cinzel7 = ImageFont.truetype(os.path.join(FONTS, "cinzel-latin-700-normal.woff"), 58)
    credit = ImageFont.truetype(os.path.join(FONTS, "cinzel-latin-700-normal.woff"), 50)
    italic = ImageFont.truetype(os.path.join(FONTS, "cormorant-garamond-latin-500-italic.woff"), 96)

    centered(d, 230, "LA GLADIADORA DE LOS NOMBRES", cinzel7, ORO, spacing=14)
    centered(d, 330, "CAMELIA", cinzel9, PERGAMINO, spacing=20)
    d.rectangle([W / 2 - 300, 800, W / 2 + 300, 806], fill=ORO)
    centered(d, H - 420, "Recupera los nombres de los cautivos para liberarlos.", italic, PERGAMINO)
    centered(d, H - 250, "UN JUEGO DE ANA ELIZABETH NOVOA AGUILAR", credit, ORO, spacing=8)

    out = os.path.join(ROOT, "entrega", "camelia_poster.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    poster.convert("RGB").save(out, optimize=True)
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()

    # Colocación de la RA en unidades del póster (ancho = 1, origen en el centro)
    aspect = H / W
    update_config({
        "poster": {"file": "entrega/camelia_poster.png", "width": W, "height": H, "sha256": sha},
        "placement": {
            "cameliaHeight": 0.5,
            "cameliaFeetY": round(-aspect / 2 + (H - feet_y) / W, 4),
            "cameliaX": 0.29,  # a la derecha, para no tapar la figura del póster
            "brocheSize": 0.22,
            # sobre la cabeza de la Camelia animada
            "brochePosition": f"0.29 {round(-aspect / 2 + (H - feet_y) / W + 0.5 + 0.15, 3)} 0.06",
        },
    })
    print(f"Póster: {out} ({W}x{H}) sha256={sha[:16]}…")


if __name__ == "__main__":
    main()
