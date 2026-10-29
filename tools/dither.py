"""Ordered-dither the card covers.

    python tools/dither.py [--width 180] [--levels 3] [--matrix 4] [--color] [--invert auto|yes|no] [files...]

Reads assets/shots/*-cover.png (or the files given) and writes *-cover-dither.png
beside each one at low resolution: grayscale, contrast-stretched, then a Bayer
ordered dither down to `levels` tones between near-black and light gray. Mostly
light images are inverted so they sit in the dark theme. The
cards render them with image-rendering: pixelated, so the pixels stay crisp at
any size. Needs Pillow and numpy.
"""
import argparse
import glob
import os

import numpy as np
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DARK, LIGHT = 14, 225  # tone range, picked to sit inside the site's dark theme


def bayer(n):
    m = np.array([[0, 2], [3, 1]])
    while m.shape[0] < n:
        m = np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])
    return (m + 0.5) / m.size - 0.5  # centred thresholds in (-0.5, 0.5)


def dither(path, width, levels, matrix, color, invert=None):
    im = Image.open(path).convert('RGB' if color else 'L')
    im = ImageOps.autocontrast(im, cutoff=1)
    h = round(im.height * width / im.width)
    px = np.asarray(im.resize((width, h), Image.LANCZOS), float) / 255
    if invert or (invert is None and px.mean() > 0.55):
        px = 1 - px  # light-theme screenshots go dark so every card sits in the dark page

    n = len(matrix)
    t = np.tile(matrix, (h // n + 1, width // n + 1))[:h, :width]
    if color:
        t = t[..., None]
    q = np.clip(np.round(px * (levels - 1) + t), 0, levels - 1) / (levels - 1)

    dst = path[:-4] + '-dither.png'
    Image.fromarray((DARK + q * (LIGHT - DARK)).round().astype(np.uint8)).save(dst, optimize=True)
    print(os.path.relpath(dst, ROOT), (width, h), f'{os.path.getsize(dst) / 1024:.1f} KB')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='*')
    ap.add_argument('--width', type=int, default=180)
    ap.add_argument('--levels', type=int, default=3, help='tones per channel')
    ap.add_argument('--matrix', type=int, default=4, help='Bayer matrix size: 2, 4 or 8')
    ap.add_argument('--color', action='store_true', help='dither each RGB channel instead of grayscale')
    ap.add_argument('--invert', choices=['auto', 'yes', 'no'], default='auto',
                    help='invert light images (auto: when the mean tone is above 55%%)')
    a = ap.parse_args()
    files = a.files or sorted(glob.glob(os.path.join(ROOT, 'assets', 'shots', '*-cover.png')))
    for f in files:
        dither(f, a.width, a.levels, bayer(a.matrix), a.color, {'auto': None, 'yes': True, 'no': False}[a.invert])


if __name__ == '__main__':
    main()
