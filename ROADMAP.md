# Pixelorama RPG Plaza Rebuild — Complete Plan

## Goal
Rebuild the reference plaza as **editable, reusable pixel assets** rather than cropped pieces of the source image. The reference image is visual guidance only; final assets are drawn on blank canvases.

## Non-negotiable rules
1. **No source-pixel reuse** in `redraw/`: no crop, alpha-mask extraction, copy/paste, or resampling from `pix.png` into final assets.
2. Every final asset has an editable **Pixelorama `.pxo`** source.
3. Props are layered by material/function; tiles are reusable 32x32 modules.
4. Every `.pxo` must pass Pixelorama CLI export and split-layer validation.
5. Main map grid is **32x32 px**. Props may be any multiple/overhang of the grid.
6. Bottom-center is the default prop anchor unless metadata says otherwise.

## Target repository structure
```text
redraw/
  tiles/
    stone_tiles_32/
    curb_tiles_32/
    grass_edge_tiles_32/
    flowerbed_edge_tiles_32/
    stairs_tiles_32/
  props/
    lamp_post/
    tree_round/
    blue_banner/
    fountain/
    market_stall_blue/
    market_stall_white/
    crates/
    flower_clusters/
    benches_barrels/
  architecture/
    turret_blue/
    roof_red/
    wall_gate/
  animation/
    fountain_water/
    flag_wave/
preview/
  reassembled_plaza_*.png
scripts/
  build_pack_v2.py
  save_ora_as_pxo_gui.py
manifest_v2.json
```

## Phase 0 — Tooling & validation
- Install/run Pixelorama in the sandbox.
- Standardize OpenRaster -> Pixelorama `.pxo` conversion.
- Standardize Pixelorama CLI validation (`--export`, `--split-layers`).
- Add a manifest describing canvas size, grid footprint, anchor, and layers.

**Acceptance:** a generated `.pxo` reopens in Pixelorama and split-layer export returns the expected layer count.

## Phase 1 — Core visual language
Create a shared palette and pixel treatment:
- warm beige stone, cool dark outlines, saturated blue accents,
- 1 px dark outline with selective broken outlines,
- 2–4 shade ramps per material,
- clustered highlights rather than anti-aliasing.

**Assets:** lamp post, round tree, blue banner, six 32x32 pavement tiles.

## Phase 2 — Landmark prop
Redraw the central fountain as a layered scene asset:
- shadow
- stone base
- water
- pedestal
- statue
- highlights

Then split water into an animation track in a later phase.

## Phase 3 — Market kit
Build modular market pieces, not whole-screen crops:
- blue striped awning stall
- cream awning stall
- red/cream stall
- shelving module
- produce crates
- pottery crates
- counter/table
- small sign / basket / barrel set

Each stall should be composed from shared sub-assets where possible.

## Phase 4 — Terrain / border TileSet
Build autotile-friendly 32x32 modules:
- pavement variants
- curb straight / inner corner / outer corner / cap
- grass-to-stone transitions
- flowerbed borders
- stairs top/middle/bottom
- low wall straight/corners

Target: enough pieces to recreate the plaza's paths without baking the whole map into one image.

## Phase 5 — Vegetation & decoration kit
- round tree variants A/B/C
- conifer tree
- bushes
- flower clusters in several palettes
- planters
- benches / barrels / crates

Use a shared trunk/leaf palette and vary silhouette, highlight clusters and footprint.

## Phase 6 — Architecture kit
- blue turret roof
- red roof segment
- stone wall / battlement
- large gate/steps
- selected facade modules

Architecture can span multiple grid cells and should use explicit anchor + collision metadata.

## Phase 7 — Animation
- fountain water: 4–8 frames
- banner/flag: 4 frames
- lamp glow: optional 2–4 frame pulse

Export spritesheets with Pixelorama CLI and record frame tags in metadata.

## Phase 8 — Reassembly proof
Build a new plaza composition from only the redrawn assets:
- tiled ground
- four vegetation islands
- central fountain
- lamps and banners
- market kit

The proof image must be assembled from reusable assets only.

## Phase 9 — Game-engine handoff
For Godot:
- `TileSet` atlas for terrain
- `.tscn` props for fountain/tree/stall/lamp
- collision footprints
- Y-sort anchors
- optional navigation blockers

## Validation checklist per asset
- [ ] Pixelorama `.pxo` exists.
- [ ] Opens without error.
- [ ] Expected layer count exported by Pixelorama CLI.
- [ ] Flattened Pixelorama export matches authored composite.
- [ ] Transparent background where appropriate.
- [ ] No pixels copied from the source PNG.
- [ ] Grid footprint + bottom-center anchor recorded.
- [ ] 4x preview exists for visual review.

## Current execution status
- [x] Pixelorama 1.2.2 running in sandbox.
- [x] Lamp post `.pxo` validated.
- [x] Round tree redrawn and `.pxo` validated.
- [x] Six pavement tiles redrawn and `.pxo` validated.
- [x] Blue banner redrawn and `.pxo` validated.
- [x] Fountain v1 redrawn and `.pxo` validated.
- [x] Reassembled plaza v2 proof generated from redrawn assets.
- [ ] Market kit.
- [ ] Terrain border/autotile kit.
- [ ] Additional vegetation.
- [ ] Architecture kit.
- [ ] Animations.
- [ ] Godot handoff.
