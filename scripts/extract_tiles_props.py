#!/usr/bin/env python3
"""Generate the first Tile/Prop decomposition from pix.png.

Dependencies: Pillow, numpy.
"""
from PIL import Image, ImageDraw, ImageEnhance
from pathlib import Path
from collections import deque
import numpy as np
import json

SOURCE = Path("pix.png")
OUT = Path("generated")
SCALE = 2
TILE = 32

TILE_COORDS = [
    (1520,112,"stone_a"), (1184,160,"stone_b"),
    (992,192,"stone_c"), (864,736,"stone_d"),
    (720,848,"stone_e"), (1360,208,"stone_f"),
]

PROP_BOXES = {
    "fountain_cluster": (575,190,1125,715),
    "lamp_post": (590,155,675,380),
    "blue_banner": (565,650,655,930),
}

def logicalize(img, factor=2, colors=96):
    w, h = img.size
    nw, nh = max(1, w // factor), max(1, h // factor)
    alpha = img.getchannel("A").resize((nw, nh), Image.Resampling.BOX)
    rgb = img.convert("RGB").resize((nw, nh), Image.Resampling.BOX)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.06)
    rgb = rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                       dither=Image.Dither.NONE).convert("RGB")
    rgb.putalpha(alpha)
    return rgb

def remove_connected_pavement(img, threshold=72):
    arr = np.array(img.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.int16)
    h, w = rgb.shape[:2]
    border = np.concatenate([rgb[0], rgb[-1], rgb[:,0], rgb[:,-1]], axis=0)
    median = np.median(border, axis=0)
    dist = np.sqrt(((rgb - median) ** 2).sum(axis=2))
    candidate = dist < threshold
    seen = np.zeros((h,w), dtype=bool)
    q = deque()
    for x in range(w):
        for y in (0,h-1):
            if candidate[y,x] and not seen[y,x]:
                seen[y,x] = True; q.append((y,x))
    for y in range(h):
        for x in (0,w-1):
            if candidate[y,x] and not seen[y,x]:
                seen[y,x] = True; q.append((y,x))
    while q:
        y,x = q.popleft()
        for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0 <= yy < h and 0 <= xx < w and candidate[yy,xx] and not seen[yy,xx]:
                seen[yy,xx] = True; q.append((yy,xx))
    arr[seen,3] = 0
    return Image.fromarray(arr, "RGBA")

def keep_largest_alpha_component(img, min_alpha=32):
    arr = np.array(img)
    mask = arr[:,:,3] > min_alpha
    h,w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    best = []
    for y in range(h):
        for x in range(w):
            if not mask[y,x] or seen[y,x]:
                continue
            comp=[]; q=[(y,x)]; seen[y,x]=True
            for yy,xx in q:
                comp.append((yy,xx))
                for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx]=True; q.append((ny,nx))
            if len(comp) > len(best): best = comp
    keep = np.zeros_like(mask, dtype=bool)
    for y,x in best: keep[y,x]=True
    dil = keep.copy()
    ys,xs = np.where(keep)
    for y,x in zip(ys,xs):
        dil[max(0,y-1):min(h,y+2), max(0,x-1):min(w,x+2)] = True
    arr[~dil,3] = 0
    return Image.fromarray(arr, "RGBA")

def save_prop_from_pavement(src, bbox, name, colors=96):
    p = remove_connected_pavement(src.crop(bbox))
    p = keep_largest_alpha_component(logicalize(p, SCALE, colors))
    bb = p.getchannel("A").getbbox()
    if bb: p = p.crop(bb)
    p.save(OUT/"props"/f"{name}.png")
    return p

def main():
    (OUT/"tiles").mkdir(parents=True, exist_ok=True)
    (OUT/"props").mkdir(parents=True, exist_ok=True)
    src = Image.open(SOURCE).convert("RGBA")

    atlas = Image.new("RGBA", (TILE*3, TILE*2), (0,0,0,0))
    for i,(x,y,name) in enumerate(TILE_COORDS):
        tile = logicalize(src.crop((x,y,x+64,y+64)), SCALE, 64)
        tile = tile.resize((TILE,TILE), Image.Resampling.NEAREST)
        tile.save(OUT/"tiles"/f"{name}.png")
        atlas.alpha_composite(tile, ((i%3)*TILE, (i//3)*TILE))
    atlas.save(OUT/"tiles"/"stone_tiles_32.png")

    built = {}
    for name,bbox in PROP_BOXES.items():
        p = save_prop_from_pavement(src, bbox, name, 96 if name == "fountain_cluster" else 64)
        built[name] = {"source_bbox_display": bbox, "asset_size": p.size, "anchor": "bottom-center"}

    tree_bbox=(245,300,435,550)
    crop=src.crop(tree_bbox)
    mask=Image.new("L", crop.size, 0)
    poly=[(95,0),(135,10),(175,55),(188,125),(170,175),(145,195),(135,245),
          (55,245),(45,200),(18,175),(3,115),(15,55),(55,15)]
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    crop.putalpha(mask)
    tree=logicalize(crop,SCALE,72)
    bb=tree.getchannel("A").getbbox()
    if bb: tree=tree.crop(bb)
    tree.save(OUT/"props"/"tree_round.png")
    built["tree_round"]={"source_bbox_display":tree_bbox,"asset_size":tree.size,"anchor":"bottom-center"}

    stall_bbox=(1250,470,1590,845)
    crop=src.crop(stall_bbox)
    mask=Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).polygon([(25,0),(270,0),(300,55),(300,320),(270,370),(20,370),(5,330),(5,70)], fill=255)
    crop.putalpha(mask)
    stall=logicalize(crop,SCALE,96)
    bb=stall.getchannel("A").getbbox()
    if bb: stall=stall.crop(bb)
    stall.save(OUT/"props"/"market_stall_blue_cluster.png")
    built["market_stall_blue_cluster"]={"source_bbox_display":stall_bbox,"asset_size":stall.size,"anchor":"bottom-center"}

    meta={
        "logical_scale":{"source_pixels_per_asset_pixel":SCALE,"tile_size":[TILE,TILE]},
        "tiles":[{"id":n,"source_bbox_display":[x,y,x+64,y+64]} for x,y,n in TILE_COORDS],
        "props":built,
    }
    (OUT/"layout.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
