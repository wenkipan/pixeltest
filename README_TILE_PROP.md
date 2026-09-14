# Pixelorama Tile / Prop Rebuild

This branch contains two clearly separated experiments:

- `generated/` — the early crop/mask extraction experiment. Keep it only as a baseline showing what **not** to use for the final game assets.
- `redraw/` — the real rebuild. Assets are drawn from blank canvases, stored as native Pixelorama `.pxo`, and validated by Pixelorama CLI.

## Functional v4 asset pack

Core props:
- `redraw/lamp_post/`
- `redraw/tree_round/`
- `redraw/blue_banner/`
- `redraw/fountain/`

Market / decoration:
- `redraw/props/market_stall_blue/`
- `redraw/props/market_stall_cream/`
- `redraw/props/market_stall_red/`
- `redraw/props/market_crates/`
- `redraw/props/flower_clusters/`
- `redraw/props/bench_barrel_kit/`
- `redraw/props/conifer_tree/`

Terrain:
- `redraw/stone_tiles_32/`
- `redraw/tiles/curb_tiles_32/`
- `redraw/tiles/grass_edge_tiles_32/`
- `redraw/tiles/stairs_tiles_32/`
- `redraw/tiles/wall_tiles_32/`

Architecture:
- `redraw/architecture/turret_blue/`
- `redraw/architecture/red_roof_segment/`
- `redraw/architecture/wall_gate/`

Animation:
- `redraw/animation/fountain_water/` — 4 frames
- `redraw/animation/flag_wave/` — 4 frames
- `redraw/animation/lamp_glow/` — 4 frames

## Proof and handoff

- `preview/reassembled_plaza_v4.png` / `_2x.png` — a new plaza assembled only from reusable redrawn assets.
- `manifest_v2.json` — dimensions, layers/modules, grid metadata and animation metadata.
- `godot/` — lightweight Godot handoff with a scene skeleton and asset/anchor/collision metadata.
- `validated_v3/` and `validated_v4/` — Pixelorama CLI validation output.

## Reproducible build

- `scripts/build_phase3_5.py` + payload: market, terrain border and vegetation assets.
- `scripts/ora_to_pxo.py`: deterministic layered ORA -> native Pixelorama PXO conversion.
- `scripts/build_phase6_9.py` + payload: architecture, native animation PXOs, reassembly proof and Godot handoff.
- `.github/workflows/generate-redraw-v3.yml` and `generate-redraw-v4.yml`: rebuild and validate the pack with official Pixelorama 1.2.2.

See `ROADMAP.md` for the full phased plan, validation rules and current status.
