#!/usr/bin/env python3
from PIL import Image
from pathlib import Path

src = Image.open('pix.png').convert('RGB')
src.thumbnail((384, 384), Image.Resampling.LANCZOS)
out = Path('generated/source_preview.jpg')
out.parent.mkdir(parents=True, exist_ok=True)
src.save(out, 'JPEG', quality=72, optimize=True)
print(f'wrote {out}: {src.size}')
