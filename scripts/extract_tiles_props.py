#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageEnhance
from pathlib import Path
from collections import deque
import numpy as np
import json

SOURCE = Path('pix.png')
OUT = Path('generated')
BASE_W, BASE_H = 1839, 1064
TILE = 32

TILE_COORDS_BASE = [
    (0,144,'stone_a'), (32,96,'stone_b'), (96,128,'stone_c'),
    (128,64,'stone_d'), (112,160,'stone_e'), (144,192,'stone_f'),
]
PROP_BOXES_BASE = {
    'fountain_cluster': (575,190,1125,715),
    'lamp_post': (590,155,675,380),
    'blue_banner': (565,650,655,930),
    'tree_round': (260,280,430,550),
    'market_stall_blue_cluster': (1280,460,1545,835),
}

def scale_point(x,y,sx,sy): return (round(x*sx), round(y*sy))
def scale_bbox(b,sx,sy):
    x0,y0,x1,y1=b
    return (round(x0*sx),round(y0*sy),round(x1*sx),round(y1*sy))

def quantize_rgba(img, target_size, colors=96):
    alpha = img.getchannel('A').resize(target_size, Image.Resampling.BOX)
    rgb = img.convert('RGB').resize(target_size, Image.Resampling.BOX)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.06)
    rgb = rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                       dither=Image.Dither.NONE).convert('RGB')
    rgb.putalpha(alpha)
    return rgb

def remove_connected_background(img, threshold=70):
    arr=np.array(img.convert('RGBA'))
    rgb=arr[:,:,:3].astype(np.int16)
    h,w=rgb.shape[:2]
    border=np.concatenate([rgb[0],rgb[-1],rgb[:,0],rgb[:,-1]],axis=0)
    median=np.median(border,axis=0)
    dist=np.sqrt(((rgb-median)**2).sum(axis=2))
    candidate=dist < threshold
    seen=np.zeros((h,w),dtype=bool); q=deque()
    for x in range(w):
        for y in (0,h-1):
            if candidate[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
    for y in range(h):
        for x in (0,w-1):
            if candidate[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
    while q:
        y,x=q.popleft()
        for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0<=yy<h and 0<=xx<w and candidate[yy,xx] and not seen[yy,xx]:
                seen[yy,xx]=True; q.append((yy,xx))
    arr[seen,3]=0
    return Image.fromarray(arr,'RGBA')

def crop_alpha(img):
    bb=img.getchannel('A').getbbox()
    return img.crop(bb) if bb else img

def fountain_mask(size):
    w,h=size
    m=Image.new('L',size,0); d=ImageDraw.Draw(m)
    d.ellipse((int(.06*w),int(.30*h),int(.94*w),int(.99*h)),fill=255)
    pts=[(.18,.20),(.31,.12),(.39,.03),(.50,.10),(.61,.04),(.77,.14),(.83,.30),
         (.68,.45),(.64,.56),(.36,.56),(.32,.45)]
    d.polygon([(int(x*w),int(y*h)) for x,y in pts],fill=255)
    return m

def tree_mask(size):
    w,h=size
    m=Image.new('L',size,0); d=ImageDraw.Draw(m)
    d.ellipse((int(.08*w),0,int(.92*w),int(.76*h)),fill=255)
    d.polygon([(int(.37*w),int(.60*h)),(int(.63*w),int(.60*h)),
               (int(.70*w),int(.98*h)),(int(.30*w),int(.98*h))],fill=255)
    return m

def stall_mask(size):
    w,h=size
    m=Image.new('L',size,0); d=ImageDraw.Draw(m)
    d.polygon([(int(.02*w),int(.02*h)),(int(.96*w),int(.02*h)),(int(.99*w),int(.16*h)),
               (int(.97*w),int(.96*h)),(int(.03*w),int(.96*h)),(int(.01*w),int(.15*h))],fill=255)
    return m

def save_prop(src,bbox_base,name,sx,sy,colors=96,mask_fn=None,remove_bg=True):
    bbox=scale_bbox(bbox_base,sx,sy)
    crop=src.crop(bbox).convert('RGBA')
    if remove_bg:
        crop=remove_connected_background(crop)
    if mask_fn:
        mask=mask_fn(crop.size)
        a=np.minimum(np.array(crop.getchannel('A')),np.array(mask)).astype(np.uint8)
        crop.putalpha(Image.fromarray(a,'L'))
    bw=bbox_base[2]-bbox_base[0]; bh=bbox_base[3]-bbox_base[1]
    target=(max(1,round(bw/2)), max(1,round(bh/2)))
    p=quantize_rgba(crop,target,colors)
    p=crop_alpha(p)
    p.save(OUT/'props'/f'{name}.png')
    return p,bbox

def checker(size,cell=8):
    im=Image.new('RGBA',size,(238,238,238,255)); d=ImageDraw.Draw(im)
    for y in range(0,size[1],cell):
        for x in range(0,size[0],cell):
            if (x//cell+y//cell)%2:
                d.rectangle((x,y,min(size[0]-1,x+cell-1),min(size[1]-1,y+cell-1)),fill=(215,215,215,255))
    return im

def make_preview(assets):
    cells=[]
    for name,img in assets:
        scale=min(1.0,180/max(img.width,1),160/max(img.height,1))
        disp=img if scale>=1 else img.resize((max(1,int(img.width*scale)),max(1,int(img.height*scale))),Image.Resampling.NEAREST)
        cell=checker((220,200),10); x=(220-disp.width)//2; y=(170-disp.height)//2
        cell.alpha_composite(disp,(x,max(0,y)))
        ImageDraw.Draw(cell).text((8,178),name,fill=(20,20,20,255))
        cells.append(cell)
    cols=3; rows=(len(cells)+cols-1)//cols
    sheet=Image.new('RGBA',(cols*220,rows*200),(255,255,255,255))
    for i,c in enumerate(cells): sheet.alpha_composite(c,((i%cols)*220,(i//cols)*200))
    sheet.save(OUT/'preview'/'assets_sheet.png')

def main():
    for p in (OUT/'tiles',OUT/'props',OUT/'preview'): p.mkdir(parents=True,exist_ok=True)
    src=Image.open(SOURCE).convert('RGBA'); sw,sh=src.size
    sx,sy=sw/BASE_W, sh/BASE_H
    atlas=Image.new('RGBA',(TILE*3,TILE*2),(0,0,0,0)); tile_meta=[]
    for i,(bx,by,name) in enumerate(TILE_COORDS_BASE):
        x,y=scale_point(bx,by,sx,sy); x2,y2=scale_point(bx+64,by+64,sx,sy)
        tile=quantize_rgba(src.crop((x,y,x2,y2)),(TILE,TILE),64)
        tile.save(OUT/'tiles'/f'{name}.png'); atlas.alpha_composite(tile,((i%3)*TILE,(i//3)*TILE))
        tile_meta.append({'id':name,'source_bbox':[x,y,x2,y2],'source_bbox_base':[bx,by,bx+64,by+64]})
    atlas.save(OUT/'tiles'/'stone_tiles_32.png')

    props=[]; prop_meta={}
    specs={
      'fountain_cluster':(96,fountain_mask,False),
      'lamp_post':(64,None,True),
      'blue_banner':(64,None,True),
      'tree_round':(72,tree_mask,False),
      'market_stall_blue_cluster':(96,stall_mask,False),
    }
    for name,b in PROP_BOXES_BASE.items():
        colors,mask_fn,remove_bg=specs[name]
        p,bbox=save_prop(src,b,name,sx,sy,colors,mask_fn,remove_bg)
        props.append((name,p))
        prop_meta[name]={'source_bbox':bbox,'source_bbox_base':list(b),'asset_size':list(p.size),'anchor':'bottom-center'}

    make_preview([('stone_tiles_32',atlas)]+props)
    meta={'source_size':[sw,sh],'baseline_size':[BASE_W,BASE_H],'source_scale':[sx,sy],
          'logical_scale':{'tile_size':[TILE,TILE]},'tiles':tile_meta,'props':prop_meta}
    (OUT/'layout.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    (OUT/'source_info.json').write_text(json.dumps({'source_size':[sw,sh],'baseline_size':[BASE_W,BASE_H],'scale':[sx,sy]},indent=2),encoding='utf-8')

if __name__=='__main__': main()
