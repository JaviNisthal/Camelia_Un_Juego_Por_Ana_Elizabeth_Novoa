"""Extrae el broche de la lámina de elementos del juego.

Paso 1 (ver piezas numeradas):
  python3 tools/extract_brooch.py source/Camelia_elementos_juego.png
  -> revision/elementos_indice.png

Paso 2 (exportar la pieza elegida, o un recuadro manual x0,y0,x1,y1):
  python3 tools/extract_brooch.py source/Camelia_elementos_juego.png --pieza 3
  python3 tools/extract_brooch.py source/Camelia_elementos_juego.png --recuadro 120,80,520,480
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from cutout import ROOT, bbox, blobs, foreground_mask, load_rgba, to_transparent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--pieza", type=int)
    ap.add_argument("--recuadro")
    ap.add_argument("--size", type=int, default=512)
    args = ap.parse_args()

    rgba = load_rgba(args.sheet)
    if args.recuadro:
        x0, y0, x1, y1 = map(int, args.recuadro.split(","))
        rgba = rgba[y0:y1, x0:x1]
    fg = foreground_mask(rgba)
    rgba_t = to_transparent(rgba, fg)
    labels, parts = blobs(fg, dilate=4)
    parts = [p for p in parts if p["area"] > 0.002 * fg.size]
    parts.sort(key=lambda p: (p["y0"] // 200, p["x0"]))

    if not args.pieza and not args.recuadro:
        os.makedirs(os.path.join(ROOT, "revision"), exist_ok=True)
        im = Image.fromarray(rgba).convert("RGB")
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        for k, p in enumerate(parts, start=1):
            d.rectangle([p["x0"], p["y0"], p["x1"], p["y1"]], outline=(220, 0, 0), width=3)
            d.text((p["x0"] + 4, p["y0"] + 2), str(k), fill=(220, 0, 0), font=f)
        path = os.path.join(ROOT, "revision", "elementos_indice.png")
        im.save(path)
        print(f"{len(parts)} piezas. Mira {path} y repite con --pieza N")
        return

    if args.recuadro:
        keep = fg
    else:
        p = parts[args.pieza - 1]
        keep = (labels == p["label"]) & fg
    piece = rgba_t.copy()
    piece[~keep] = 0
    y0, y1, x0, x1 = bbox(keep)
    piece = Image.fromarray(piece[y0:y1, x0:x1])
    side = max(piece.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(piece, ((side - piece.width) // 2, (side - piece.height) // 2))
    sq = sq.resize((args.size, args.size), Image.LANCZOS)
    for out in (os.path.join(ROOT, "assets", "broche.png"), os.path.join(ROOT, "entrega", "broche.png")):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sq.save(out, optimize=True)
    print("Listo: assets/broche.png y entrega/broche.png")


if __name__ == "__main__":
    main()
