#!/usr/bin/env python3
"""Redraw the plaza lamp as fresh pixel art, without copying source pixels.

The reference image is used only by eye. This script draws new geometry and colors
onto an empty 32x112 canvas and exports editable layers plus an OpenRaster file.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import io, zipfile, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'redraw' / 'lamp_post'
LAYERS = OUT / 'layers'
W, H = 32, 112
TRANSPARENT = (0, 0, 0, 0)

OUTLINE=(25,30,42,255); DARK=(37,44,60,255); MID=(58,65,78,255)
LIGHT=(85,89,95,255); IRON_HI=(103,105,105,255)
GLASS_DARK=(142,70,29,255); GLASS=(215,125,38,255)
GLASS_HI=(255,216,124,255); GLASS_CORE=(255,238,179,255)

def canvas(): return Image.new('RGBA', (W,H), TRANSPARENT)

def build_layers():
    LAYERS.mkdir(parents=True, exist_ok=True)
    result=[]
    shadow=canvas(); d=ImageDraw.Draw(shadow)
    d.ellipse((8,101,24,108), fill=(20,20,28,70)); d.ellipse((10,102,22,106), fill=(20,20,28,45))
    result.append(('shadow', shadow))
    pole=canvas(); d=ImageDraw.Draw(pole)
    d.polygon([(8,99),(10,95),(12,94),(12,90),(20,90),(20,94),(22,95),(24,99),(23,104),(9,104)], fill=OUTLINE)
    d.rectangle((10,99,22,103), fill=DARK); d.rectangle((12,96,20,101), fill=MID)
    d.rectangle((13,95,19,98), fill=DARK); d.rectangle((14,94,18,97), fill=IRON_HI)
    d.rectangle((11,91,21,94), fill=OUTLINE); d.rectangle((12,91,20,92), fill=MID)
    d.rectangle((13,40,19,92), fill=OUTLINE); d.rectangle((14,41,18,91), fill=DARK)
    d.rectangle((15,42,16,89), fill=MID); d.point((17,48), fill=LIGHT)
    d.polygon([(11,40),(12,37),(20,37),(21,40),(20,43),(12,43)], fill=OUTLINE); d.rectangle((13,38,19,41), fill=MID)
    result.append(('pole_base', pole))
    body=canvas(); d=ImageDraw.Draw(body)
    d.polygon([(16,4),(13,8),(14,11),(11,13),(11,16),(21,16),(21,13),(18,11),(19,8)], fill=OUTLINE)
    d.rectangle((15,5,17,9), fill=DARK); d.point((16,4), fill=IRON_HI)
    d.polygon([(8,18),(11,13),(21,13),(24,18),(22,22),(10,22)], fill=OUTLINE)
    d.polygon([(10,18),(13,15),(20,15),(22,18),(21,20),(11,20)], fill=MID); d.rectangle((13,15,16,16), fill=LIGHT)
    d.polygon([(9,21),(23,21),(22,39),(19,45),(13,45),(10,39)], fill=OUTLINE)
    d.rectangle((10,23,12,38), fill=DARK); d.rectangle((20,23,22,38), fill=DARK)
    d.polygon([(10,38),(22,38),(20,44),(12,44)], fill=OUTLINE); d.rectangle((13,40,19,43), fill=MID)
    d.point((11,24), fill=IRON_HI); d.line((12,22,20,22), fill=LIGHT)
    result.append(('lamp_frame', body))
    glass=canvas(); d=ImageDraw.Draw(glass)
    d.polygon([(12,23),(20,23),(20,36),(18,39),(14,39),(12,36)], fill=GLASS_DARK)
    d.polygon([(13,24),(19,24),(19,35),(18,37),(14,37),(13,35)], fill=GLASS)
    d.rectangle((14,25,18,34), fill=GLASS_HI); d.rectangle((15,26,17,34), fill=GLASS_CORE); d.point((14,25), fill=(255,246,210,255))
    result.append(('glass', glass))
    hi=canvas(); d=ImageDraw.Draw(hi)
    d.point((12,18), fill=IRON_HI); d.point((13,17), fill=IRON_HI); d.point((14,42), fill=LIGHT); d.point((15,43), fill=LIGHT)
    d.line((14,47,14,72), fill=(83,88,98,255)); d.point((14,77), fill=(83,88,98,255)); d.point((13,97), fill=IRON_HI)
    d.line((11,101,15,101), fill=(86,91,100,255)); result.append(('highlights', hi))
    glow=canvas(); d=ImageDraw.Draw(glow)
    for box,a in [((6,17,26,45),22),((8,19,24,43),36),((10,21,22,41),52)]: d.ellipse(box, fill=(255,168,48,a))
    result.append(('glow', glow))
    return result

def save_ora(layers, merged):
    top=['highlights','glass','lamp_frame','pole_base','shadow','glow']; by_name=dict(layers)
    image_el=ET.Element('image', {'version':'0.0.1','w':str(W),'h':str(H),'name':'lamp_post'}); stack=ET.SubElement(image_el,'stack',{'name':'root'})
    for name in top: ET.SubElement(stack,'layer', {'name':name,'src':f'data/{name}.png','visibility':'visible','opacity':'1.0','composite-op':'svg:src-over'})
    xml=ET.tostring(image_el, encoding='utf-8', xml_declaration=True); thumb=merged.copy(); thumb.thumbnail((256,256),Image.Resampling.NEAREST)
    with zipfile.ZipFile(OUT/'lamp_post.ora','w') as z:
        z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED); z.writestr('stack.xml',xml)
        b=io.BytesIO(); merged.save(b,'PNG'); z.writestr('mergedimage.png',b.getvalue()); b=io.BytesIO(); thumb.save(b,'PNG'); z.writestr('Thumbnails/thumbnail.png',b.getvalue())
        for name in top:
            b=io.BytesIO(); by_name[name].save(b,'PNG'); z.writestr(f'data/{name}.png',b.getvalue())

def main():
    OUT.mkdir(parents=True, exist_ok=True); layers=build_layers()
    for i,(name,img) in enumerate(layers): img.save(LAYERS/f'{i:02d}_{name}.png')
    order=['glow','shadow','pole_base','lamp_frame','glass','highlights']; by_name=dict(layers); merged=canvas()
    for name in order: merged=Image.alpha_composite(merged, by_name[name])
    merged.save(OUT/'lamp_post.png'); merged.resize((W*6,H*6),Image.Resampling.NEAREST).save(OUT/'lamp_post_preview_6x.png'); save_ora(layers, merged)
    print(f'wrote {OUT}')

if __name__ == '__main__': main()
