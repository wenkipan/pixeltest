#!/usr/bin/env python3
from pathlib import Path

src = Path('generated/source_preview.b64')
dst = Path('generated/source_preview_wrapped.txt')
s = ''.join(src.read_text(encoding='ascii').split())
width = 120
dst.write_text('\n'.join(s[i:i+width] for i in range(0, len(s), width)) + '\n', encoding='ascii')
print(f'wrote {dst} with {(len(s)+width-1)//width} lines')
