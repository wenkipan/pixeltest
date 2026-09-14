#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw
import io, zipfile, xml.etree.ElementTree as ET, json

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
}

def canv(size): return Image.new('RGBA',size,T)

def composite(size,layers,order=None):
    by=dict(layers); out=canv(size)
    for n in (order or [n for n,_ in layers]): out=Image.alpha_composite(out,by[n])
    return out

def save_ora(asset,size,layers,merged,top_to_bottom=None):
    folder=OUT/asset; folder.mkdir(parents=True,exist_ok=True); (folder/'layers').mkdir(exist_ok=True)
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
    merged.resize((size[0]*4,size[1]*4),Image.Resampling.NEAREST).save(folder/f'{asset}_preview_4x.png')


def draw_tree():
    size=(96,128); layers=[]
    sh=canv(size); d=ImageDraw.Draw(sh); d.ellipse((21,106,78,121),fill=PAL['shadow']); layers.append(('shadow',sh))
    tr=canv(size); d=ImageDraw.Draw(tr)
    d.polygon([(39,79),(57,79),(62,112),(55,116),(40,115),(34,111)],fill=PAL['outline'])
    d.polygon([(42,79),(54,79),(57,110),(53,113),(41,112),(38,109)],fill=PAL['wood_d'])
    d.rectangle((45,84,49,108),fill=PAL['wood']); d.line((51,86,54,105),fill=PAL['wood_l']); d.line((41,94,45,91),fill=PAL['wood_l'])
    layers.append(('trunk',tr))
    fd=canv(size); d=ImageDraw.Draw(fd)
    clusters=[(18,33,53,75),(38,18,76,64),(55,38,88,82),(15,57,55,94),(40,55,78,101),(61,61,91,95),(30,31,74,86)]
    for b in clusters:d.ellipse(b,fill=PAL['green_d'])
    for b in [(20,29,32,42),(59,22,73,35),(72,47,86,61),(12,65,28,78),(33,87,48,99),(70,79,84,91)]: d.rectangle(b,fill=PAL['green_d'])
    layers.append(('foliage_dark',fd))
    fm=canv(size); d=ImageDraw.Draw(fm)
    for b in [(24,35,49,61),(42,26,67,54),(59,43,80,68),(23,62,48,86),(45,58,69,87),(62,67,82,86)]:d.ellipse(b,fill=PAL['green'])
    for b in [(29,41,37,48),(50,31,60,38),(68,49,75,57),(31,70,38,79),(52,65,60,73),(70,74,76,81)]:d.rectangle(b,fill=PAL['green_l'])
    layers.append(('foliage_mid',fm))
    fl=canv(size); d=ImageDraw.Draw(fl)
    for pts in [[(29,42),(35,37),(41,40),(38,47),(32,49)],[(50,31),(57,28),(63,33),(59,40),(53,39)],[(67,49),(73,46),(78,50),(75,57),(69,57)],[(32,67),(38,63),(44,67),(41,74),(35,75)],[(52,61),(58,57),(64,61),(61,69),(55,68)]]:
        d.polygon(pts,fill=PAL['green_l'])
    for p in [(32,40),(55,31),(72,50),(35,66),(57,60),(67,72),(47,46),(43,78)]: d.rectangle((p[0],p[1],p[0]+2,p[1]+2),fill=PAL['leaf_hi'])
    layers.append(('foliage_light',fl))
    hi=canv(size); d=ImageDraw.Draw(hi)
    for p in [(30,39),(55,29),(72,49),(38,64),(59,59),(25,57),(48,35)]:d.point(p,fill=PAL['cream'])
    layers.append(('highlights',hi))
    merged=composite(size,layers)
    save_ora('tree_round',size,layers,merged)
    return merged


def stone_tile(seed):
    size=(32,32); im=Image.new('RGBA',size,PAL['stone']); d=ImageDraw.Draw(im)
    offsets=[0,5,2,7,3,0][seed%6]
    y=1; rows=[7,7,8,7,7]
    for ri,h in enumerate(rows):
        x=(-offsets-(ri%2)*9)%18-18
        widths=[13,15,12,16,14,11]; k=0
        while x<32:
            w=widths[(seed+ri+k)%len(widths)]
            d.rectangle((x,y,x+w,y+h-2),fill=PAL['stone_l'] if (ri+k+seed)%4==0 else PAL['stone'])
            d.line((x,y+h-1,x+w,y+h-1),fill=PAL['stone_d'])
            d.line((x+w+1,y,x+w+1,y+h-1),fill=PAL['stone_d'])
            if (ri+k+seed)%3==0:d.point((x+3,y+2),fill=(205,190,164,255))
            x += w+2; k+=1
        y += h
    cracks=[[(8,11),(9,12),(9,14),(11,15)],[(22,5),(21,7),(22,9)],[(15,23),(17,22),(18,20)],[(5,26),(7,25),(9,26)],[(25,17),(23,18),(22,20)],[(12,6),(14,7),(15,9)]]
    pts=cracks[seed%6]
    for a,b in zip(pts,pts[1:]):d.line((a[0],a[1],b[0],b[1]),fill=PAL['stone_d'])
    return im


def draw_tiles():
    size=(96,64); layers=[]; merged=canv(size)
    positions=[(0,0),(32,0),(64,0),(0,32),(32,32),(64,32)]
    for i,pos in enumerate(positions):
        tile=stone_tile(i)
        layer=canv(size); layer.alpha_composite(tile,pos); name=f'stone_{chr(97+i)}'; layers.append((name,layer)); merged.alpha_composite(tile,pos)
        folder=OUT/'stone_tiles_32'; (folder/'individual').mkdir(parents=True,exist_ok=True); tile.save(folder/'individual'/f'{name}.png')
    save_ora('stone_tiles_32',size,layers,merged,top_to_bottom=[n for n,_ in layers][::-1])
    return merged


def draw_banner():
    size=(48,112); layers=[]
    sh=canv(size); d=ImageDraw.Draw(sh); d.ellipse((13,101,37,109),fill=PAL['shadow']); layers.append(('shadow',sh))
    pole=canv(size); d=ImageDraw.Draw(pole)
    d.rectangle((22,8,27,101),fill=PAL['outline']); d.rectangle((23,9,25,99),fill=PAL['wood_d']); d.line((25,12,25,96),fill=PAL['wood_l'])
    d.polygon([(20,7),(24,2),(28,7),(27,11),(21,11)],fill=PAL['gold_d']); d.rectangle((22,7,26,9),fill=PAL['gold'])
    d.polygon([(15,98),(34,98),(38,104),(35,108),(14,108),(11,104)],fill=PAL['outline']); d.rectangle((15,101,34,106),fill=PAL['wood_d'])
    layers.append(('pole',pole))
    cloth=canv(size); d=ImageDraw.Draw(cloth)
    d.polygon([(5,24),(25,18),(43,24),(41,75),(29,88),(24,82),(18,88),(7,76)],fill=PAL['outline'])
    d.polygon([(7,25),(25,20),(41,25),(39,73),(29,85),(24,79),(19,85),(9,74)],fill=PAL['blue_d'])
    d.polygon([(10,27),(25,23),(37,27),(36,69),(28,80),(24,75),(20,80),(12,70)],fill=PAL['blue'])
    layers.append(('cloth',cloth))
    em=canv(size); d=ImageDraw.Draw(em)
    d.rectangle((23,36,25,61),fill=PAL['cream']); d.polygon([(24,34),(19,41),(22,42),(24,39),(26,42),(29,41)],fill=PAL['cream'])
    d.line((24,49,17,45),fill=PAL['cream'],width=2); d.line((24,49,31,45),fill=PAL['cream'],width=2)
    d.line((24,56,18,61),fill=PAL['cream'],width=2); d.line((24,56,30,61),fill=PAL['cream'],width=2)
    layers.append(('emblem',em))
    hi=canv(size); d=ImageDraw.Draw(hi); d.line((11,29,11,63),fill=PAL['blue_l']); d.line((14,27,25,24),fill=(116,190,225,255)); layers.append(('highlights',hi))
    merged=composite(size,layers)
    save_ora('blue_banner',size,layers,merged)
    return merged


def draw_fountain():
    size=(192,160); layers=[]
    sh=canv(size); d=ImageDraw.Draw(sh); d.ellipse((20,123,172,151),fill=(20,25,31,70)); layers.append(('shadow',sh))
    base=canv(size); d=ImageDraw.Draw(base)
    d.ellipse((17,78,175,151),fill=PAL['outline']); d.ellipse((21,75,171,145),fill=PAL['stone_d']); d.ellipse((28,72,164,137),fill=PAL['stone_l']); d.ellipse((34,77,158,132),fill=PAL['blue_d'])
    d.rectangle((45,128,147,144),fill=PAL['stone']); d.rectangle((54,136,138,148),fill=PAL['stone_d'])
    d.rectangle((82,139,110,154),fill=PAL['outline']); d.rectangle((86,140,106,151),fill=PAL['stone_l'])
    for x in [28,42,150,164]:d.rectangle((x,102,x+7,124),fill=PAL['stone_d'])
    layers.append(('stone_base',base))
    water=canv(size); d=ImageDraw.Draw(water)
    d.ellipse((39,81,153,129),fill=PAL['blue']); d.ellipse((48,87,144,122),fill=PAL['blue_l'])
    for y,x0,x1 in [(98,55,75),(112,116,140),(119,68,95),(93,103,132)]: d.arc((x0,y-5,x1,y+5),0,180,fill=PAL['water_hi'],width=2)
    for x in [77,82,108,113]: d.rectangle((x,51,x+3,87),fill=PAL['blue_l']); d.line((x+1,53,x+1,84),fill=PAL['water_hi'])
    layers.append(('water',water))
    ped=canv(size); d=ImageDraw.Draw(ped)
    d.rectangle((69,75,122,106),fill=PAL['outline']); d.rectangle((73,75,118,102),fill=PAL['stone']); d.rectangle((78,70,113,82),fill=PAL['stone_l']); d.rectangle((82,63,109,74),fill=PAL['stone_d'])
    d.rectangle((88,50,103,67),fill=PAL['stone_l']); d.rectangle((90,48,101,55),fill=PAL['stone'])
    layers.append(('pedestal',ped))
    st=canv(size); d=ImageDraw.Draw(st)
    d.polygon([(94,20),(87,32),(89,50),(84,64),(106,64),(101,50),(103,33)],fill=PAL['stone_d'])
    d.polygon([(93,17),(88,22),(89,28),(95,31),(101,27),(101,21),(97,17)],fill=PAL['stone_l'])
    d.polygon([(88,28),(72,20),(61,27),(75,39),(88,42)],fill=PAL['outline']); d.polygon([(87,31),(73,23),(65,27),(76,36),(88,39)],fill=PAL['stone_l'])
    d.polygon([(101,28),(117,19),(130,25),(116,39),(102,42)],fill=PAL['outline']); d.polygon([(102,31),(116,22),(126,26),(115,36),(102,39)],fill=PAL['stone_l'])
    d.line((78,27,86,35),fill=PAL['stone_d'],width=2); d.line((112,27,104,35),fill=PAL['stone_d'],width=2)
    layers.append(('statue',st))
    hi=canv(size); d=ImageDraw.Draw(hi)
    for p in [(92,20),(74,26),(119,25),(80,74),(109,74),(31,99),(157,100),(92,84)]: d.rectangle((p[0],p[1],p[0]+2,p[1]+1),fill=PAL['white'])
    layers.append(('highlights',hi))
    merged=composite(size,layers)
    save_ora('fountain',size,layers,merged)
    return merged


def mini_scene(tiles,tree,banner,fountain):
    W,H=640,416; scene=Image.new('RGBA',(W,H),(221,205,178,255))
    tileset=[stone_tile(i) for i in range(6)]
    for gy,y in enumerate(range(0,H,32)):
        for gx,x in enumerate(range(0,W,32)):
            scene.alpha_composite(tileset[(gx*3+gy*5)%6],(x,y))
    d=ImageDraw.Draw(scene)
    for box in [(30,34,180,120),(460,34,610,120),(34,282,180,388),(460,282,610,388)]:
        d.rounded_rectangle(box,18,fill=PAL['green_d'],outline=PAL['stone_d'],width=5)
        d.rounded_rectangle((box[0]+7,box[1]+7,box[2]-7,box[3]-7),14,fill=PAL['green'])
    scene.alpha_composite(fountain,(224,125))
    scene.alpha_composite(tree,(68,18)); scene.alpha_composite(tree,(474,18)); scene.alpha_composite(tree,(70,259)); scene.alpha_composite(tree,(472,259))
    scene.alpha_composite(banner,(180,230)); scene.alpha_composite(banner,(412,230))
    lamp_path=ROOT/'redraw'/'lamp_post'/'lamp_post.png'
    if not lamp_path.exists(): lamp_path=Path('/mnt/data/pixelorama_redraw_v1/lamp_post.png')
    if lamp_path.exists():
        lamp=Image.open(lamp_path).convert('RGBA')
        for p in [(192,28),(416,28),(192,270),(416,270)]: scene.alpha_composite(lamp,p)
    PREV.mkdir(parents=True,exist_ok=True); scene.save(PREV/'reassembled_plaza_v2.png')
    scene.resize((W*2,H*2),Image.Resampling.NEAREST).save(PREV/'reassembled_plaza_v2_2x.png')


def main():
    OUT.mkdir(parents=True,exist_ok=True); PREV.mkdir(parents=True,exist_ok=True)
    tree=draw_tree(); tiles=draw_tiles(); banner=draw_banner(); fountain=draw_fountain(); mini_scene(tiles,tree,banner,fountain)
    manifest={
      'grid':[32,32], 'status':'redrawn-from-blank',
      'assets':{
        'lamp_post':{'canvas':[32,112],'layers':6,'status':'already validated in Pixelorama'},
        'tree_round':{'canvas':[96,128],'layers':6},
        'stone_tiles_32':{'canvas':[96,64],'tiles':6,'tile_size':[32,32]},
        'blue_banner':{'canvas':[48,112],'layers':5},
        'fountain':{'canvas':[192,160],'layers':6}
      }
    }
    (ROOT/'manifest_v2.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('built v2 asset pack')
if __name__=='__main__': main()
