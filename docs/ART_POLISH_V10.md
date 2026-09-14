# Art Polish V10

This is the current fidelity pass for the Pixelorama plaza rebuild.

## Status

The reusable Pixelorama asset pipeline is already functional (native PXO sources, Pixelorama CLI validation, animations, Godot handoff). V10 focuses only on visual matching against the supplied plaza reference.

## What changed from the functional v4 proof

- Rebuilt the scene at the reference's implied logical resolution: **920 x 532**, previewed at approximately 2x.
- Shifted the fountain left to match the reference composition and reduced its basin scale.
- Added the landscaped stone/green ring and front steps around the fountain.
- Added more angel statue feather, robe and stone shading detail.
- Repositioned market stalls to match the reference: upper-left cream stall, left red/cream stall, lower-left cream stall, upper-right cream stall, lower-right blue-striped stall, and far-right partial stall.
- Added dense produce, pottery, crates, signs and side shelving around market stalls.
- Added thinner landscaped curbs, flowers, shrubs and more organic tree texture.
- Aligned the two lower blue turrets and lower-right red roof to the reference composition.
- Added small-scale warm stone paving with broken highlights, mortar variation and wear pixels.
- Added banner/lamp positions and lower flower-fence details based on the reference layout.

## Fidelity rule

`pix.png` remains reference-only. No crop, resampling, alpha-mask extraction or source-pixel pasting is used in the redrawn assets. The scene is assembled from blank-canvas/redrawn primitives and the project's existing reusable redrawn assets.

## Current discrepancy list

V10 is much closer in composition, but is **not marked complete**. Remaining differences are primarily art-density rather than pipeline issues:

1. Angel anatomy and wing feathers need another hand-pixel pass.
2. Market shelves need additional object silhouettes and material shading.
3. Garden islands need more irregular border geometry and clustered foliage.
4. Building/turret facades at the bottom edge need richer masonry and roof detail.
5. Tree silhouettes need more variation and fewer repeated clusters.
6. Some far-edge market/fence objects are still schematic.
7. Final palette/value balancing should be done after the object-detail pass.

The next iterations should keep the same asset decomposition and move these visual refinements back into individual PXO assets rather than baking them only into the proof composition.
