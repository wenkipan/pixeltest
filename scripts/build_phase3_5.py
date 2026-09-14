#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw
import io, zipfile, xml.etree.ElementTree as ET, json, math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'redraw'
PREV=ROOT/'preview'
T=(0,0,0,0)
PAL={
'outline':(37,43,52,255),'dark':(56,62,66,255),'stone_d':(126,116,102,255),'stone':(184,168,145,255),'stone_l':(224,207,178,255),
'blue_d':(30,78,119,255),'blue':(42,124,177,255),'blue_l':(87,179,220,255),'water_hi':(190,238,244,255),
'green_d':(43,86,46,255),'green':(75,126,55,255),'green_l':(116,166,69,255),'leaf_hi':(168,193,90,255),
'wood_d':(79,50,34,255),'wood':(127,77,43,255),'wood_l':(177,112,62,255),
'gold_d':(137,84,24,255),'gold':(207,142,49,255),'gold_l':(247,207,106,255),
'cream':(232,216,187,255),'white':(244,237,217,255),'shadow':(24,30,35,78),
'red_d':(128,54,36,255),'red':(190,75,44,255),'red_l':(228,122,74,255),
'orange':(224,133,55,255),'yellow':(237,190,76,255),'purple':(111,78,139,255),'pink':(211,111,129,255),
'earth':(104,74,52,255),'grass_bg':(58,108,51,255),
}

def canv(size): return Image.new('RGBA',size,T)

def composite(size,layers,order=None):
    by=dict(layers); out=canv(size)
    for n in (order or [n for n,_ in layers]): out=Image.alpha_composite(out,by[n])
    return out

def save_ora(rel,size,layers,merged,top_to_bottom=None,preview_scale=4):
    folder=OUT/rel; folder.mkdir(parents=True,exist_ok=True); (folder/'layers').mkdir(exist_ok=True)
    asset=Path(rel).name
    if top_to_bottom is None: top_to_bottom=[n for n,_ in layers][::-1]
    by=dict(layers)
    image_el=ET.Element('image',{'version':'0.0.1','w':str(size[0]),'h':str(size[1]),'name':asset})
    stack=ET.SubElement(image_el,'stack',{'name':'root'})
    for n in top_to_bottom:
        ET.SubElement(stack,'layer',{'name':n,'src':f'data/{n}.png','visibility':'visible','opacity':'1.0','composite-op':'svg:src-over'})
    xml=ET.tostring(image_el,encoding='utf-8',xml_declaration=True)
    thumb=merged.copy(); thumb.thumbnail((256,256),Image.Resampling.NEAREST)
    with zipfile.ZipFile(folder/f'{asset}.ora','w') as z:
        z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
        z.writestr('stack.xml',xml)
        for path,img in [('mergedimage.png',merged),('Thumbnails/thumbnail.png',thumb)]:
            b=io.BytesIO(); img.save(b,'PNG'); z.writestr(path,b.getvalue())
        for n in top_to_bottom:
            b=io.BytesIO(); by[n].save(b,'PNG'); z.writestr(f'data/{n}.png',b.getvalue())
    for i,(n,img) in enumerate(layers): img.save(folder/'layers'/f'{i:02d}_{n}.png')
    merged.save(folder/f'{asset}.png')
    merged.resize((size[0]*preview_scale,size[1]*preview_scale),Image.Resampling.NEAREST).save(folder/f'{asset}_preview_{preview_scale}x.png')
    return merged

def draw_shadow(d, box): d.ellipse(box,fill=PAL['shadow'])

def draw_wood_frame(d,x0,y0,x1,y1):
    # Chunky timber frame with dark outlines and warm highlights.
    d.rectangle((x0,y0,x1,y1),fill=PAL['outline'])
    d.rectangle((x0+3,y0+3,x1-3,y1-3),fill=PAL['wood_d'])
    d.line((x0+5,y0+4,x0+5,y1-4),fill=PAL['wood_l'])

def draw_crate(d,x,y,kind=0):
    d.rectangle((x,y,x+27,y+24),fill=PAL['outline'])
    d.rectangle((x+2,y+2,x+25,y+22),fill=PAL['wood'])
    d.line((x+3,y+5,x+24,y+19),fill=PAL['wood_d'],width=2)
    d.line((x+24,y+5,x+3,y+19),fill=PAL['wood_d'],width=2)
    d.line((x+4,y+3,x+23,y+3),fill=PAL['wood_l'])
    # contents
    colors=[(PAL['red'],PAL['red_l']),(PAL['orange'],PAL['yellow']),(PAL['green'],PAL['green_l']),(PAL['blue'],PAL['blue_l']),(PAL['purple'],PAL['pink']),(PAL['cream'],PAL['stone_l'])]
    c1,c2=colors[kind%len(colors)]
    for i,(dx,dy) in enumerate([(5,4),(11,5),(17,4),(7,10),(14,11),(20,10)]):
        d.rectangle((x+dx,y+dy,x+dx+4,y+dy+4),fill=c1)
        if i%2==0:d.point((x+dx+1,y+dy+1),fill=c2)

def draw_pottery(d,x,y,variant=0):
    cols=[PAL['gold_d'],PAL['red_d'],PAL['blue_d'],PAL['earth']]
    base=cols[variant%4]
    for i,(dx,dy,s) in enumerate([(0,4,8),(10,1,7),(19,5,8)]):
        d.rectangle((x+dx+2,y+dy,x+dx+s-2,y+dy+2),fill=PAL['outline'])
        d.rectangle((x+dx,y+dy+3,x+dx+s,y+dy+10),fill=PAL['outline'])
        d.rectangle((x+dx+2,y+dy+4,x+dx+s-2,y+dy+9),fill=base)
        d.point((x+dx+3,y+dy+5),fill=PAL['gold_l'])

def draw_awning(layer,size,scheme='blue'):
    d=ImageDraw.Draw(layer); w,h=size
    # awning at y 18..49, scallops below.
    x0,x1=8,w-9; y0,y1=18,47
    d.polygon([(x0+5,y0),(x1-5,y0),(x1,y0+8),(x1-2,y1),(x0+2,y1),(x0,y0+8)],fill=PAL['outline'])
    inner=(x0+3,y0+3,x1-3,y1-3)
    stripe_cols=(PAL['blue'],PAL['cream']) if scheme=='blue' else ((PAL['cream'],PAL['white']) if scheme=='cream' else (PAL['red'],PAL['cream']))
    stripe_w=12
    for i,x in enumerate(range(inner[0],inner[2]+1,stripe_w)):
        col=stripe_cols[i%2]
        d.rectangle((x,inner[1],min(inner[2],x+stripe_w-1),inner[3]),fill=col)
        if i%2==0:d.line((x+1,inner[1]+1,x+1,inner[3]-1),fill=tuple(min(255,c+18) for c in col[:3])+(255,))
    # valance / scallops
    for i,x in enumerate(range(x0+3,x1-5,12)):
        col=stripe_cols[i%2]
        d.rectangle((x,y1-1,x+10,y1+7),fill=PAL['outline'])
        d.rectangle((x+1,y1,x+9,y1+5),fill=col)
        d.rectangle((x+3,y1+6,x+7,y1+7),fill=col)

def draw_stall(rel,scheme='blue',goods='produce',size=(128,112)):
    layers=[]; w,h=size
    sh=canv(size); d=ImageDraw.Draw(sh); draw_shadow(d,(16,h-14,w-12,h-4)); layers.append(('shadow',sh))
    frame=canv(size); d=ImageDraw.Draw(frame)
    # vertical posts and top beam
    for x in (14,w-19): draw_wood_frame(d,x,23,x+8,h-14)
    draw_wood_frame(d,12,52,w-11,60)
    # counter + lower shelves
    d.rectangle((18,65,w-19,101),fill=PAL['outline']); d.rectangle((21,68,w-22,98),fill=PAL['wood_d'])
    for yy in (77,89): d.rectangle((22,yy,w-23,yy+4),fill=PAL['wood']); d.line((23,yy+1,w-24,yy+1),fill=PAL['wood_l'])
    # little side legs
    leg_y=max(82,h-17)
    d.rectangle((24,leg_y,31,h-8),fill=PAL['outline']); d.rectangle((w-32,leg_y,w-25,h-8),fill=PAL['outline'])
    layers.append(('frame',frame))
    aw=canv(size); draw_awning(aw,size,scheme); layers.append(('awning',aw))
    shelf=canv(size); d=ImageDraw.Draw(shelf)
    # back cubbies
    for bx in range(25,w-34,24):
        d.rectangle((bx,62,bx+20,77),fill=PAL['outline']); d.rectangle((bx+2,64,bx+18,75),fill=(74,54,39,255))
    layers.append(('shelves',shelf))
    gd=canv(size); d=ImageDraw.Draw(gd)
    if goods=='produce':
        for i,bx in enumerate(range(26,w-35,24)):
            for j,(dx,dy) in enumerate([(2,3),(8,2),(13,5),(5,8),(11,9)]):
                col=[PAL['orange'],PAL['red'],PAL['green_l'],PAL['yellow']][(i+j)%4]
                d.rectangle((bx+dx,64+dy,bx+dx+4,64+dy+4),fill=col)
                if (i+j)%2==0:d.point((bx+dx+1,64+dy+1),fill=PAL['cream'])
        draw_crate(d,22,80,0); draw_crate(d,52,80,2); draw_crate(d,82,80,1)
    elif goods=='pottery':
        for i,bx in enumerate(range(25,w-38,27)): draw_pottery(d,bx,63,i)
        for i,bx in enumerate((24,53,82)): draw_pottery(d,bx,82,i+1)
    else:
        for i,bx in enumerate(range(25,w-38,26)):
            d.rectangle((bx,64,bx+16,74),fill=PAL['outline']); d.rectangle((bx+2,66,bx+14,72),fill=[PAL['blue'],PAL['gold'],PAL['green']][i%3])
        draw_crate(d,22,80,4); draw_pottery(d,55,84,2); draw_crate(d,82,80,3)
    layers.append(('goods',gd))
    hi=canv(size); d=ImageDraw.Draw(hi)
    d.line((18,26,18,h-17),fill=PAL['wood_l']); d.line((w-16,26,w-16,h-17),fill=PAL['wood_l'])
    d.line((20,69,w-22,69),fill=PAL['gold_l'])
    layers.append(('highlights',hi))
    merged=composite(size,layers)
    return save_ora(rel,size,layers,merged)

def market_crates():
    size=(128,64); layers=[]; merged=canv(size)
    positions=[(2,2),(34,2),(66,2),(98,2),(2,34),(34,34),(66,34),(98,34)]
    for i,,ÜäÌzwù