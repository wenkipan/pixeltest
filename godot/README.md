# Godot handoff

This directory is a lightweight handoff contract for the redrawn Pixelorama assets.

- Logical grid: **32x32**.
- Import textures with nearest-neighbor filtering.
- Prop origin: bottom-center unless overridden in `data/handoff.json`.
- Build a Godot `TileSet` atlas from the terrain sheets listed in `data/handoff.json`.
- Use the collision footprint metadata rather than the full visual bounds for Y-sort/navigation.
- Animation sources are native Pixelorama PXO projects with 4 frames each; export spritesheets with Pixelorama CLI.
