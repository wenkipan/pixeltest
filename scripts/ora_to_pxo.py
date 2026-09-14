#!/usr/bin/env python3
"""Convert a layered OpenRaster file to Pixelorama 1.2.x PXO.

The output uses the data schema from an existing Pixelorama-authored PXO in
redraw/fountain or redraw/lamp_post, then replaces canvas, layer and frame data.
This keeps the generated file native/editable while avoiding brittle GUI input.
"""
from pathlib import Path
from PIL import Image
import copy
import io
import json
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def template_data():
    for path in (
        ROOT / "redraw/fountain/fountain.pxo",
        ROOT / "redraw/lamp_post/lamp_post.pxo",
    ):
        if path.exists():
            with zipfile.ZipFile(path) as zf:
                return json.loads(zf.read("data.json"))
    raise SystemExit("No Pixelorama-authored template PXO found")


def load_ora(path: Path):
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("stack.xml"))
        size = (int(root.attrib["w"]), int(root.attrib["h"]))
        stack = root.find("stack")
        top_to_bottom = list(stack.findall("layer"))
        # Pixelorama stores project layers bottom -> top.
        layers = []
        for elem in reversed(top_to_bottom):
            name = elem.attrib.get("name", "Layer")
            src = elem.attrib["src"]
            image = Image.open(io.BytesIO(zf.read(src))).convert("RGBA")
            if image.size != size:
                raise ValueError(f"{name}: {image.size} != {size}")
            layers.append((name, image))
        return size, layers


def write_pxo(ora_path: Path, pxo_path: Path):
    size, layers = load_ora(ora_path)
    names = [name for name, _ in layers]
    data = copy.deepcopy(template_data())
    data["size_x"], data["size_y"] = size
    data["tile_mode_x_basis_x"] = size[0]
    data["tile_mode_y_basis_y"] = size[1]
    data["current_frame"] = 0
    data["current_layer"] = max(0, len(names) - 1)
    data["fps"] = 6.0
    data["tags"] = []
    data["layers"] = [
        {
            "animated_params": 'Dictionary[String, Dictionary]({\n"opacity": {}\n})',
            "blend_mode": 0,
            "clipping_mask": False,
            "effects": [],
            "locked": False,
            "metadata": {},
            "name": name,
            "new_cels_linked": False,
            "opacity": 1.0,
            "parent": -1,
            "type": 0,
            "ui_color": "(0.0, 0.0, 0.0, 0.0)",
            "visible": True,
        }
        for name in names
    ]
    data["frames"] = [{
        "cels": [
            {"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
            for _ in names
        ],
        "duration": 1.0,
        "metadata": {},
    }]
    profile = data.get("export_profile", {})
    profile["number_of_frames"] = "1"
    profile["file_name"] = json.dumps(pxo_path.stem)
    profile["directory_path"] = json.dumps(str(pxo_path.parent))
    data["export_profile"] = profile

    preview = Image.new("RGBA", size, (0, 0, 0, 0))
    for _, image in layers:
        preview = Image.alpha_composite(preview, image)

    pxo_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(pxo_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("data.json", json.dumps(data, separators=(",", ":")))
        zf.writestr("mimetype", b"application/x-pixelorama", compress_type=zipfile.ZIP_STORED)
        bio = io.BytesIO()
        preview.save(bio, "PNG")
        zf.writestr("preview.png", bio.getvalue())
        zf.writestr("image_data/frames/1/", b"")
        for index, (_, image) in enumerate(layers, 1):
            zf.writestr(f"image_data/frames/1/layer_{index}", image.tobytes())
            zf.writestr(f"image_data/frames/1/indices_layer_{index}", b"\x00")

    print(f"wrote {pxo_path} ({size[0]}x{size[1]}, {len(layers)} layers)")


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: ora_to_pxo.py INPUT.ora OUTPUT.pxo")
    write_pxo(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())


if __name__ == "__main__":
    main()
