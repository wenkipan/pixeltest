# Tile / Prop rebuild v1

This branch now contains **two different experiments**:

1. `generated/` — automatic extraction / masking from the reference image. This is useful for analysis, but it is **not** a true redraw.
2. `redraw/` — fresh pixel art drawn onto an empty canvas, then opened and saved in Pixelorama as layered `.pxo` projects.

## True Pixelorama redraw: lamp post

The first real redraw is the plaza lamp:

- `redraw/lamp_post/lamp_post.pxo` — layered Pixelorama project, created and saved with Pixelorama v1.2.2.
- `redraw/lamp_post/lamp_post.png` — freshly drawn 32×112 sprite. No pixels are cropped from `pix.png`.
- `redraw/lamp_post/lamp_post_preview_6x.png` — nearest-neighbor enlarged preview.
- `redraw/lamp_post/layers/` — editable source layers: shadow, pole/base, lamp frame, glass, highlights, glow.
- `redraw/lamp_post/lamp_post.ora` — OpenRaster layered interchange file used to bootstrap the Pixelorama project.
- `scripts/redraw_lamp_post.py` — reproducible drawing script.

The `.pxo` was verified by Pixelorama CLI export, including `--split-layers`, so the project is genuinely layered rather than a flattened screenshot.

## Earlier extraction experiment

`generated/` contains the previous Tile/Prop extraction test. It samples and masks areas of the source image and should be treated only as a decomposition prototype.

## Next

Continue with fresh redraws for the round tree, market stall and fountain, then build a reusable stone-road TileSet from newly drawn 32×32 tiles.
