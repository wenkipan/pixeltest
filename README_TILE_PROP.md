# Tile / Prop rebuild v1

This branch tests a real **asset decomposition** workflow instead of treating the whole reference as one flat image.

## Working assumptions

- Reference is treated as ~2x enlarged pixel art.
- Asset pixels are reconstructed at half the displayed resolution.
- Initial world grid: **32x32 asset pixels**.
- Ground uses reusable tiles.
- Fountain / lamp / banner / tree / market stall are independent props with transparent backgrounds.

## Files

- `assets/tiles/stone_tiles_32.png` - 6 reusable 32x32 pavement variants.
- `assets/props/*.png` - isolated prop sprites.
- `assets/layout.json` - source bboxes, sizes, anchors and scale notes.
- `preview/prop_sheet.png` - prop extraction review sheet.
- `preview/reassembled_plaza.png` - a new mini scene assembled from the reusable pieces.
- `scripts/extract_tiles_props.py` - reproducible extraction script.

## Why this is different from the first pass

The first pass only reconstructed the image's pixel structure. This pass introduces two reusable asset classes:

1. **Tile**: repeatable 32x32 ground modules.
2. **Prop**: sprites larger than one tile, with their own transparent canvas and bottom-center anchor.

The generated assets can be opened directly in Pixelorama. The next iteration should hand-clean silhouettes, split fountain water/statue/base into layers, and convert road/flowerbed edges into an autotile-style set.
