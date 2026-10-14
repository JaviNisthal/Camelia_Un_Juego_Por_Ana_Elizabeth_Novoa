"""Crea un vídeo .y4m de cámara simulada para la prueba automática:
primero el póster (con algo de movimiento e inclinación) y después una mesa vacía,
para comprobar el reconocimiento y la pérdida del póster.

Uso: python3 tools/make_test_video.py [entrega/camelia_poster.png] [revision/camara_simulada.y4m]
"""
import os
import sys

import numpy as np
from PIL import Image

from cutout import ROOT

W, H, FPS = 640, 480, 15
SECONDS_ON, SECONDS_OFF = 10, 5


def quad_coeffs(dst, src):
    a = []
    for (x, y), (u, v) in zip(dst, src):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    b = np.array(src).reshape(8)
    return np.linalg.solve(np.array(a, float), b)


def frame(poster, t, show):
    bg = Image.new("RGB", (W, H), (96, 92, 88))
    if show:
        ph = 400
        pw = ph * poster.width / poster.height
        cx = W / 2 + 25 * np.sin(t * 1.3)
        cy = H / 2 + 10 * np.cos(t * 0.9)
        k = 0.06 * np.sin(t * 0.7)  # inclinación en perspectiva
        dst = [(cx - pw / 2 * (1 - k), cy - ph / 2), (cx + pw / 2 * (1 + k), cy - ph / 2),
               (cx + pw / 2 * (1 + k), cy + ph / 2), (cx - pw / 2 * (1 - k), cy + ph / 2)]
        src = [(0, 0), (poster.width, 0), (poster.width, poster.height), (0, poster.height)]
        warped = poster.transform((W, H), Image.PERSPECTIVE, quad_coeffs(dst, src), Image.BILINEAR)
        mask = Image.new("L", poster.size, 255).transform((W, H), Image.PERSPECTIVE, quad_coeffs(dst, src))
        bg.paste(warped, (0, 0), mask)
    return bg


def main():
    poster_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "entrega", "camelia_poster.png")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "revision", "camara_simulada.y4m")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    poster = Image.open(poster_path).convert("RGB")
    poster = poster.resize((poster.width // 4, poster.height // 4), Image.LANCZOS)
    total = (SECONDS_ON + SECONDS_OFF) * FPS
    with open(out, "wb") as f:
        f.write(f"YUV4MPEG2 W{W} H{H} F{FPS}:1 Ip A1:1 C420jpeg\n".encode())
        for n in range(total):
            t = n / FPS
            ycbcr = np.array(frame(poster, t, t < SECONDS_ON).convert("YCbCr"))
            y = ycbcr[..., 0]
            cb = ycbcr[..., 1].reshape(H // 2, 2, W // 2, 2).mean(axis=(1, 3)).astype(np.uint8)
            cr = ycbcr[..., 2].reshape(H // 2, 2, W // 2, 2).mean(axis=(1, 3)).astype(np.uint8)
            f.write(b"FRAME\n")
            f.write(y.tobytes() + cb.tobytes() + cr.tobytes())
    print(f"Vídeo de prueba: {out} ({SECONDS_ON}s con póster + {SECONDS_OFF}s sin póster, en bucle)")


if __name__ == "__main__":
    main()
