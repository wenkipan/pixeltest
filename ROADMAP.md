# Pixelorama RPG Plaza Rebuild — Complete Plan

## Goal
Rebuild the reference plaza as **editable, reusable pixel assets** rather than cropped pieces of the source image. The reference PNG is visual guidance only; final assets in `redraw/` are authored from blank canvases.

## Non-negotiable rules
1. **No source-pixel reuse** in `redraw/`: no crop, alpha-mask extraction, copy/paste, or resampling from `pix.png` into final assets.
2. Final assets have editable native **Pixelorama `.pxo`** sources.
3. Props are layered by material/function; terrain uses reusable 32x32 modules.
4. Native PXO files are validated with Pixelorama CLI export; layered assets also use split-layer validation.
5. Main map grid is **32x32 px**. Props may overhang multiple cells.
6. Bottom-center is the default prop anchor unless metadata says otherwise.

## Phase 0 — Tooling & validation — DONE
- Pixelorama 1.2.2 runs in the sandbox and GitHub Actions.
- Deterministic layered OpenRaster -> native PXO conversion is available in `scripts/ora_to_pxo.py`.
- Pixelorama CLI validation covers flattened export, split layers, frame count and spritesheets.
- `manifest_v2.json` records the reusable asset pack.

## Phase 1 — Core visual language — DONE
Shared warm-stone / cool-outline / blue-accent palette and clustered pixel highlights.

Validated core assets:
- lamp post
- round tree
- blue banner
- six 32x32 pavement variants

## Phase 2 — Landmark fountain — DONE
Layered fountain with shadow, stone/base, water, pedestal/statue details and highlights. The water was later separated into a native four-frame animation.

## Phase 3 — Market kit — DONE (functional v1)
Reusable market assets:
- blue striped stall
- cream stall
- red/cream stall
- produce / pottery / mixed crate modules
- reusable shelf/counter structure inside the stall layers

The stalls are authored independently rather than cut out of the reference.

## Phase 4 — Terrain / border TileSet — DONE (functional v1)
32x32 modular terrain pieces:
- pavement variants
- curb/border sheet: 12 tiles
- grass-edge sheet: 8 tiles
- stairs: 3 tiles
- wall/battlement sheet: 8 tiles

This is enough for a reusable plaza proof. A production game can still expand the autotile combinations later.

## Phase 5 — Vegetation & decoration — DONE (functional v1)
- round deciduous tree
- conifer tree
- flower-cluster sheet: 8 modules
- bench/barrel decoration kit
- market crate sheet: 8 modules

More silhouette variants can be added as polish without changing the pipeline.

## Phase 6 — Architecture kit — DONE (functional v1)
- blue turret
- red roof segment
- large stone wall/gate + steps
- low-wall/battlement 32x32 modules

All architecture assets are native layered PXO and pass Pixelorama flattened/split-layer validation.

## Phase 7 — Animation — DONE
Native Pixelorama animations:
- `fountain_water`: 4 frames @ 8 fps
- `flag_wave`: 4 frames @ 7 fps
- `lamp_glow`: 4 frames @ 5 fps

Pixelorama CLI frame counts and spritesheet exports are validated against the authored frames.

## Phase 8 — Reassembly proof — DONE
`preview/reassembled_plaza_v4.png` is assembled entirely from the redrawn reusable assets: tiled ground, vegetation islands, fountain, banners, lamps, market stalls and architecture. It does not use source-image crops.

## Phase 9 — Godot handoff — DONE (skeleton / metadata handoff)
`godot/` contains:
- `project.godot`
- `data/handoff.json` with grid, texture/PXO paths, anchors, collision footprints and animation metadata
- `scenes/plaza_demo.tscn` scene skeleton with Ground / Terrain / Props / Actors groups and Y-sort-ready structure

This handoff is intentionally lightweight: the next game-specific step is importing the atlas textures into a real Godot TileSet and tuning collisions/navigation in the target game project.

## Phase 10 — Reference fidelity polish — IN PROGRESS
The pipeline is no longer the bottleneck. Current work is iterative visual matching against the supplied reference while preserving the modular asset structure.

The sandbox has progressed through art-polish passes v5 -> v10. V10 now matches the reference more closely in the following macro areas:
- 920x532 logical composition (approximately 2x display scale)
- fountain shifted to the reference's left-of-center position
- landscaped fountain ring, stairs and curb segmentation
- six main market-stall placements and far-edge stall hints
- lamp/banner/turret positions
- smaller irregular stone paving
- denser market goods, pottery, crates and signs
- more organic tree texture and landscaped flowerbeds
- lower blue turret / red-roof edge composition

See `docs/ART_POLISH_V10.md` for the current discrepancy checklist.

V10 is **not considered final**. The next passes must move the visual improvements into the individual native PXO assets, with priority on angel anatomy/feathers, market-object density, irregular garden borders, facade/roof detail, tree silhouette variation and final palette/value balancing.

## Validation checklist
For the current functional asset pack:
- [x] Native Pixelorama `.pxo` sources exist.
- [x] Pixelorama CLI can open/export the tested PXO files.
- [x] Static layered assets pass split-layer export checks.
- [x] Flattened Pixelorama exports match authored composites in validation workflows.
- [x] Animated PXO files report 4 frames and export pixel-identical spritesheets.
- [x] Transparent prop backgrounds are preserved.
- [x] `redraw/` assets are drawn from blank canvases, not copied from the source PNG.
- [x] 32x32 terrain grid and prop anchors are represented in metadata/handoff files.
- [x] Reassembly proof exists using reusable assets only.
- [ ] High-fidelity reference match is complete.

## Current milestone
**Functional rebuild v4 is complete; fidelity polish has reached v10 and remains in progress.** The goal is now to converge the native Pixelorama assets toward the reference without sacrificing editability or modular reuse.
