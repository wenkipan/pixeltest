#!/usr/bin/env python3
from PIL import Image
from pathlib import Path

src = Image.open('pix.png').convert('RGB')
for size, quality, name in [
    (384, 72, 'source_preview.jpg'),
    (96, 50, 'source_preview_tiny.jpg'),
]:
    im = src.copy()
    im.thumbnail((size, size), Image.Resampling.LANCZOS)
    out = Path('generated') / name
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, 'JPEG', quality=quality, optimize=True)
    print(f'wrote {out}: {im.size}')
