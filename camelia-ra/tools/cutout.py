"""Utilidades compartidas: quitar fondo blanco, separar piezas y recortar."""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def foreground_mask(rgba, tol=28):
    """Primer plano = todo lo que no sea el blanco conectado con el borde.
    El blanco interior (brillos, ojos) se conserva."""
    rgb = rgba[..., :3].astype(np.int16)
    if rgba[..., 3].min() < 250:  # ya trae transparencia
        return rgba[..., 3] > 16
    near_white = (255 - rgb).max(axis=2) <= tol
    labels, _ = ndimage.label(near_white)
    border = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    border = border[border > 0]
    background = np.isin(labels, border)
    return ~background


def to_transparent(rgba, fg, band=2):
    """Devuelve RGBA con fondo transparente. En el borde aplica 'color a alfa'
    contra blanco para no dejar halo."""
    out = rgba.copy().astype(np.float32)
    if rgba[..., 3].min() < 250:
        return rgba
    alpha = fg.astype(np.float32)
    # banda exterior pegada a la silueta
    grown = ndimage.binary_dilation(fg, iterations=band)
    edge = grown & ~fg
    rgb = out[..., :3]
    a = ((255.0 - rgb).max(axis=2) / 255.0).clip(0, 1)
    alpha[edge] = a[edge]
    safe = np.maximum(alpha, 1e-3)[..., None]
    unmixed = ((rgb - 255.0 * (1 - alpha[..., None])) / safe).clip(0, 255)
    rgb[edge] = unmixed[edge]
    out[..., 3] = alpha * 255
    out[~grown] = 0
    return out.round().astype(np.uint8)


def blobs(fg, dilate=6):
    """Piezas separadas (tras unir fragmentos cercanos). Devuelve lista de
    dicts ordenada por área descendente."""
    joined = ndimage.binary_dilation(fg, iterations=dilate) if dilate else fg
    labels, n = ndimage.label(joined)
    out = []
    for i, sl in enumerate(ndimage.find_objects(labels), start=1):
        region = (labels[sl] == i) & fg[sl]
        area = int(region.sum())
        if area == 0:
            continue
        out.append({"label": i, "slice": sl, "area": area,
                    "y0": sl[0].start, "y1": sl[0].stop, "x0": sl[1].start, "x1": sl[1].stop})
    out.sort(key=lambda b: -b["area"])
    return labels, out


def bbox(mask):
    ys, xs = np.where(mask)
    return ys.min(), ys.max() + 1, xs.min(), xs.max() + 1


def update_config(patch):
    path = os.path.join(ROOT, "assets", "config.json")
    cfg = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
            cfg[k].update(v)
        else:
            cfg[k] = v
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    return cfg
