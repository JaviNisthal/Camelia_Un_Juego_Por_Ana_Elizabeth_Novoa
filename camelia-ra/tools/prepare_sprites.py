"""Recorta las ocho poses de la lámina, las alinea y genera el GIF y la lámina para RA.

Uso:
  python3 tools/prepare_sprites.py source/Camelia_sprites_caminata.png
  python3 tools/prepare_sprites.py source/Camelia_sprites_caminata.png --order 1,2,3,4,5,6,7,8 --fps 10

Qué hace:
  1. Quita el fondo blanco (solo el blanco unido al borde; el blanco interior se conserva).
  2. Detecta las 8 figuras y descarta título y números (piezas pequeñas o muy anchas).
  3. Alinea todas por la línea de los pies y por el centro de cabeza y torso, sin cambiar la escala.
  4. Genera revisión (hoja con guías, papel cebolla e informe con saltos entre fotogramas).
  5. Escribe entrega/camelia_caminata.gif, entrega/fotogramas/*.png,
     assets/camelia_sprite.png y la sección "sprite" de assets/config.json.
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

from cutout import ROOT, blobs, foreground_mask, load_rgba, to_transparent, update_config

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def find_figures(fg, count):
    labels, parts = blobs(fg, dilate=3)
    candidates = []
    for b in parts:
        h, w = b["y1"] - b["y0"], b["x1"] - b["x0"]
        if w > 3 * h:  # tiras de texto (título)
            continue
        candidates.append(b)
    figures = candidates[:count]
    if len(figures) < count:
        raise SystemExit(f"Solo encontré {len(figures)} figuras; revisa la lámina o usa --tol.")
    smallest = min(f["area"] for f in figures)
    rest = [b for b in candidates[count:]]
    if rest and rest[0]["area"] > 0.5 * smallest:
        print(f"AVISO: hay una pieza extra grande (área {rest[0]['area']}) que no se usó; revisa revision/hoja_revision.png")
    # orden de lectura: filas por altura, luego izquierda a derecha
    figures.sort(key=lambda b: (b["y0"] + b["y1"]) / 2)
    med_h = np.median([b["y1"] - b["y0"] for b in figures])
    rows, current = [], [figures[0]]
    for b in figures[1:]:
        if abs((b["y0"] + b["y1"]) / 2 - (current[-1]["y0"] + current[-1]["y1"]) / 2) > 0.5 * med_h:
            rows.append(current)
            current = [b]
        else:
            current.append(b)
    rows.append(current)
    ordered = [b for row in rows for b in sorted(row, key=lambda b: b["x0"])]
    return labels, ordered, [len(r) for r in rows]


def cut(rgba_t, fg, labels, b, removed):
    """Recorta una figura y quita piezas pequeñas sueltas en su franja superior
    o inferior (números o letras que quedaron pegados a la figura)."""
    sl = b["slice"]
    piece = rgba_t[sl].copy()
    keep = (labels[sl] == b["label"]) & fg[sl]
    parts, n = ndimage.label(keep)
    h = keep.shape[0]
    total = keep.sum()
    for i, psl in enumerate(ndimage.find_objects(parts), start=1):
        area = (parts[psl] == i).sum()
        in_band = psl[0].stop <= 0.15 * h or psl[0].start >= 0.85 * h
        if area < 0.03 * total and in_band:
            keep[parts == i] = False
            removed.append((sl[1].start + psl[1].start, sl[0].start + psl[0].start,
                            sl[1].start + psl[1].stop, sl[0].start + psl[0].stop))
    piece[~keep] = 0
    ys, xs = np.where(keep)
    return piece[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def align(pieces, pad):
    infos = []
    for p in pieces:
        a = p[..., 3] > 127
        ys, xs = np.where(a)
        top, base = ys.min(), ys.max() + 1
        upper = a.copy()
        upper[top + int(0.55 * (base - top)):] = False  # cabeza y torso
        anchor_x = np.where(upper)[1].mean()
        infos.append({"top": top, "base": base, "ax": anchor_x, "h": base - top,
                      "left": anchor_x - xs.min(), "right": xs.max() + 1 - anchor_x})
    up = max(i["base"] for i in infos)  # alto máximo sobre la línea de pies
    left = max(i["left"] for i in infos)
    right = max(i["right"] for i in infos)
    W = int(np.ceil(left + right)) + 2 * pad
    H = int(up) + 2 * pad
    out = []
    for p, i in zip(pieces, infos):
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        x = int(round(pad + left - i["ax"]))
        y = int(H - pad - i["base"])
        canvas.alpha_composite(Image.fromarray(p), (x, y))
        out.append(canvas)
    return out, infos, (W, H), pad, left


def masks_small(frames, h=96):
    """Versión pequeña premultiplicada (color * alfa) de cada fotograma."""
    out = []
    for f in frames:
        w = max(1, round(f.width * h / f.height))
        a = np.array(f.resize((w, h), Image.BILINEAR)).astype(np.float32) / 255
        out.append(a[..., :3] * a[..., 3:4])
    return out


def dist(a, b, legs_only=False):
    """Diferencia media de color; distingue pierna cercana y lejana."""
    if legs_only:
        a, b = a[a.shape[0] // 2:], b[b.shape[0] // 2:]
    return float(np.abs(a - b).mean())


def analyse(frames):
    ms = masks_small(frames)
    n = len(ms)
    return [dist(ms[k], ms[(k + 1) % n], legs_only=True) for k in range(n)]


def review_sheet(frames, pad, path, labels):
    W, H = frames[0].size
    gap = 20
    sheet = Image.new("RGB", (len(frames) * (W + gap) + gap, H + 70), (236, 230, 220))
    d = ImageDraw.Draw(sheet)
    for k, f in enumerate(frames):
        x = gap + k * (W + gap)
        # cuadros para ver la transparencia
        for yy in range(0, H, 16):
            for xx in range(0, W, 16):
                if (xx // 16 + yy // 16) % 2:
                    d.rectangle([x + xx, 50 + yy, x + min(xx + 15, W - 1), 50 + min(yy + 15, H - 1)], fill=(214, 206, 194))
        sheet.paste(f, (x, 50), f)
        d.line([x, 50 + H - pad, x + W, 50 + H - pad], fill=(200, 30, 30), width=2)
        d.line([x + W // 2, 50, x + W // 2, 50 + H], fill=(30, 80, 200), width=1)
        d.text((x + 6, 10), labels[k], fill=(30, 20, 15), font=font(26))
    sheet.save(path)


def onion(frames, path):
    W, H = frames[0].size
    out = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    colours = [(200, 40, 40), (40, 120, 200), (40, 160, 80), (180, 120, 20),
               (140, 60, 170), (20, 150, 150), (200, 90, 140), (90, 90, 90)]
    for k, f in enumerate(frames):
        a = np.array(f)[..., 3]
        layer = np.zeros((H, W, 4), np.uint8)
        layer[..., :3] = colours[k % len(colours)]
        layer[..., 3] = (a * 0.28).astype(np.uint8)
        out.alpha_composite(Image.fromarray(layer))
    out.convert("RGB").save(path)


def save_gif(frames, path, height, fps, matte=None):
    scale = height / frames[0].height
    size = (round(frames[0].width * scale), height)
    out = []
    for f in frames:
        f = f.resize(size, Image.LANCZOS)
        if matte:
            bg = Image.new("RGBA", size, matte + (255,))
            bg.alpha_composite(f)
            out.append(bg.convert("RGB").quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE))
        else:
            a = np.array(f)[..., 3]
            rgb = f.convert("RGB").quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
            idx = np.array(rgb)
            idx[a < 128] = 255
            p = Image.fromarray(idx.astype(np.uint8), "P")
            pal = rgb.getpalette()[:255 * 3] + [0, 0, 0]
            p.putpalette(pal)
            p.info["transparency"] = 255
            out.append(p)
    kw = dict(save_all=True, append_images=out[1:], duration=round(1000 / fps), loop=0, disposal=2, optimize=False)
    if not matte:
        kw["transparency"] = 255
    out[0].save(path, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--order", help="orden de los fotogramas detectados, p. ej. 1,2,3,4,5,6,7,8")
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--tol", type=int, default=28, help="tolerancia del blanco de fondo")
    ap.add_argument("--ar-height", type=int, default=512)
    ap.add_argument("--gif-height", type=int, default=480)
    args = ap.parse_args()

    rev = os.path.join(ROOT, "revision")
    os.makedirs(rev, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "entrega", "fotogramas"), exist_ok=True)

    rgba = load_rgba(args.sheet)
    fg = foreground_mask(rgba, args.tol)
    rgba_t = to_transparent(rgba, fg)
    labels, figs, rows = find_figures(fg, args.frames)
    print(f"Figuras detectadas: {len(figs)} en filas {rows}")

    # marca las piezas detectadas sobre la lámina original
    dbg = Image.fromarray(rgba).convert("RGB")
    d = ImageDraw.Draw(dbg)
    for k, b in enumerate(figs, start=1):
        d.rectangle([b["x0"], b["y0"], b["x1"], b["y1"]], outline=(220, 0, 0), width=4)
        d.text((b["x0"] + 6, b["y0"] + 4), str(k), fill=(220, 0, 0), font=font(40))
    removed = []
    pieces = [cut(rgba_t, fg, labels, b, removed) for b in figs]
    for box in removed:
        d.rectangle(box, outline=(0, 90, 220), width=3)
    if removed:
        print(f"Piezas pequeñas descartadas (azul en revision/deteccion.png): {len(removed)}")
    dbg.save(os.path.join(rev, "deteccion.png"))
    order = list(range(len(pieces)))
    if args.order:
        order = [int(x) - 1 for x in args.order.split(",")]
        assert sorted(order) == list(range(len(pieces))), "--order debe usar cada número una vez"
    pieces = [pieces[i] for i in order]
    names = [f"#{i + 1}" for i in order]

    pad = 12
    frames, infos, (W, H), pad, _ = align(pieces, pad)
    heights = [i["h"] for i in infos]

    review_sheet(frames, pad, os.path.join(rev, "hoja_revision.png"), names)
    onion(frames, os.path.join(rev, "papel_cebolla.png"))
    steps = analyse(frames)

    lines = ["INFORME DE CAMINATA", f"Lámina: {os.path.basename(args.sheet)}",
             f"Orden usado (numeración de revision/deteccion.png): {','.join(str(i + 1) for i in order)}",
             f"Lienzo común: {W}x{H}px, línea de pies a {pad}px del borde inferior",
             "Alto de cada figura (px): " + ", ".join(str(h) for h in heights),
             f"Variación de alto: {100 * (max(heights) - min(heights)) / np.median(heights):.1f}% (normal en caminata: hasta ~5%)",
             "Cambio entre fotogramas consecutivos (zona de piernas, diferencia media de color; 0 = idénticos):"]
    for k, s in enumerate(steps):
        lines.append(f"  {names[k]} -> {names[(k + 1) % len(names)]}: {s:.3f}")
    med = float(np.median(steps))
    jumps = [k for k, s in enumerate(steps) if s > 2 * med]
    if jumps:
        lines.append("POSIBLE SALTO en: " + ", ".join(f"{names[k]}->{names[(k + 1) % len(names)]}" for k in jumps))
    stalls = [k for k, s in enumerate(steps) if s < 0.25 * med]
    if stalls:
        lines.append("POSIBLE FOTOGRAMA REPETIDO o pausa en: " + ", ".join(f"{names[k]}->{names[(k + 1) % len(names)]}" for k in stalls))
    if (max(heights) - min(heights)) / np.median(heights) > 0.05:
        lines.append("AVISO: la escala varía más de lo normal; revisa si alguna pose está dibujada más grande.")
    if not jumps and not stalls:
        lines.append("Sin saltos bruscos medidos. Confirma a ojo el GIF y revision/papel_cebolla.png:")
        lines.append("la métrica no distingue bien poses simétricas (pierna izquierda/derecha).")
    report = "\n".join(lines)
    print(report)
    with open(os.path.join(rev, "informe_caminata.txt"), "w", encoding="utf-8") as f:
        f.write(report + "\n")

    # fotogramas a resolución completa
    for k, fr in enumerate(frames, start=1):
        fr.save(os.path.join(ROOT, "entrega", "fotogramas", f"camelia_caminata_{k:02d}.png"))

    # GIF para la actividad
    save_gif(frames, os.path.join(ROOT, "entrega", "camelia_caminata.gif"), args.gif_height, args.fps)
    save_gif(frames, os.path.join(ROOT, "entrega", "camelia_caminata_fondo_arena.gif"), args.gif_height, args.fps,
             matte=(217, 185, 138))

    # lámina horizontal para la textura animada de la RA
    fh = args.ar_height
    fw = round(W * fh / H)
    sprite = Image.new("RGBA", (fw * len(frames), fh), (0, 0, 0, 0))
    for k, fr in enumerate(frames):
        sprite.alpha_composite(fr.resize((fw, fh), Image.LANCZOS), (k * fw, 0))
    sprite.save(os.path.join(ROOT, "assets", "camelia_sprite.png"), optimize=True)
    update_config({"sprite": {"frames": len(frames), "columns": len(frames), "rows": 1, "fps": args.fps,
                              "frameWidth": fw, "frameHeight": fh, "feetPadding": round(pad * fh / H)}})
    print("Listo: entrega/camelia_caminata.gif, entrega/fotogramas/, assets/camelia_sprite.png, revision/")


if __name__ == "__main__":
    main()
