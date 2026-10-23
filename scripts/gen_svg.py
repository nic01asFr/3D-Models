
import bpy, math, os, re, urllib.request, colorsys
from mathutils import Vector
SVGDIR='/projects/catalogue_panneaux/svg/'
UA={'User-Agent':'catalogue-panneaux/0.1 (laval.nicolas13@gmail.com)'}

def fetch(n, path):
    import time
    d=SVGDIR+n
    if not os.path.exists(d):
        for k in range(6):
            try:
                time.sleep(1.5)
                req=urllib.request.Request('https://upload.wikimedia.org/wikipedia/commons/'+path,headers=UA)
                data=urllib.request.urlopen(req,timeout=30).read()
                open(d,'wb').write(data)
                break
            except Exception as e:
                if '429' in str(e) and k<5: time.sleep(10*(k+1)); continue
                raise
    return d

def colname(rgb):
    r,g,b=rgb; h,s,v=colorsys.rgb_to_hsv(r,g,b)
    if v<0.2: return 'Noir_Pictogramme',(0.02,0.02,0.02,1)
    if s<0.15: return ('Blanc_Retro',(0.9,0.9,0.88,1)) if v>0.6 else ('Gris_Panneau',(0.4,0.4,0.4,1))
    if h<0.04 or h>0.94: return 'Rouge_Panneau',(0.65,0.02,0.02,1)
    if 0.04<=h<0.11: return 'Orange_Panneau',(0.9,0.4,0.0,1)
    if 0.11<=h<0.2: return 'Jaune_Panneau',(0.95,0.75,0.0,1)
    if 0.2<=h<0.45: return 'Vert_Panneau',(0.0,0.4,0.2,1)
    if 0.5<=h<0.72: return 'Bleu_Panneau',(0.0,0.12,0.55,1)
    return 'Autre_%02x%02x%02x'%tuple(int(x*255) for x in rgb),(r,g,b,1)

def getmat(name,rgba,metal=0.0,rough=0.35):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=rgba; b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    return m

def clear_scene_objects():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)

def make_from_svg(code, svgname, path, width_m, meta, height_m=None):
    f=fetch(svgname,path)
    txt=open(f,encoding='utf-8',errors='ignore').read()
    before=set(bpy.data.objects.keys())
    bpy.ops.import_curve.svg(filepath=f)
    new=[o for o in bpy.data.objects if o.name not in before and o.type=='CURVE']
    # ordre documentaire
    def pos(o):
        base=re.sub(r'\.\d+$','',o.name)
        m=re.search(r'id="%s"'%re.escape(base),txt)
        return m.start() if m else 10**9
    new.sort(key=pos)
    meta=dict(meta)
    if len(new)>1:
        big0=max(new,key=lambda o:o.dimensions.x*o.dimensions.y)
        bb=[big0.matrix_world@Vector(c_) for c_ in big0.bound_box]
        bx0,bx1=min(p_.x for p_ in bb),max(p_.x for p_ in bb); by0,by1=min(p_.y for p_ in bb),max(p_.y for p_ in bb)
        keep=[];drop=[]
        for o in new:
            c_=sum((o.matrix_world@Vector(q) for q in o.bound_box),Vector())/8
            (keep if bx0-1e-6<=c_.x<=bx1+1e-6 and by0-1e-6<=c_.y<=by1+1e-6 else drop).append(o)
        for o in drop: bpy.data.objects.remove(o)
        new=keep; meta['elements_hors_forme_ignores']=len(drop)
    # bbox union
    pts=[]
    for o in new:
        for c in o.bound_box: pts.append(o.matrix_world@Vector(c))
    x0,x1=min(p.x for p in pts),max(p.x for p in pts); y0,y1=min(p.y for p in pts),max(p.y for p in pts)
    W=x1-x0; H=y1-y0
    k=width_m/W if height_m is None else None
    if height_m is not None: kx=width_m/W; ky=height_m/H
    else: kx=ky=k
    cx,cy=(x0+x1)/2,(y0+y1)/2
    col=bpy.data.collections.new(code); bpy.context.scene.collection.children.link(col)
    root=bpy.data.objects.new(code,None); col.objects.link(root)
    th=0.0004
    big=max(new,key=lambda o:o.dimensions.x*o.dimensions.y)
    parts=[]
    for i,o in enumerate(new):
        rgb=o.active_material.diffuse_color[:3] if o.active_material else (0,0,0)
        nm,rgba=colname(rgb)
        o.data.dimensions='2D'; o.data.fill_mode='BOTH'; o.data.extrude=th/2
        o.data.bevel_depth=0
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
        bpy.ops.object.convert(target='MESH')
        m=bpy.context.object
        m.data.transform(__import__('mathutils').Matrix.Translation((-cx,-cy,0)))
        m.data.transform(__import__('mathutils').Matrix.Diagonal((kx,ky,1,1)))
        m.location=(0,0,0.0015+i*th)
        m.data.materials.clear(); m.data.materials.append(getmat(nm,rgba))
        m.name=f'{code}_p{i:02d}'
        parts.append(m)
    # dos : copie de la plus grande forme
    bi=new.index(big) if big in new else 0
    src=parts[new.index(big)]
    back=src.copy(); back.data=src.data.copy(); bpy.context.scene.collection.objects.link(back)
    back.location=(0,0,0.0); back.name=f'{code}_dos'
    back.data.materials.clear(); back.data.materials.append(getmat('Aluminium_Dos',(0.6,0.6,0.62,1),0.9,0.35))
    # épaissir le dos
    for v in back.data.vertices: v.co.z*=1.0
    parts.append(back)
    for m in parts:
        for c in list(m.users_collection): c.objects.unlink(m)
        col.objects.link(m); m.parent=root
    root.rotation_euler[0]=math.pi/2
    for k_,v_ in meta.items(): root[k_]=v_
    root['code_iisr']=code
    return root


def export_sign(root, outdir):
    os.makedirs(outdir,exist_ok=True)
    bpy.context.view_layer.update()
    pts=[]
    for o in root.children_recursive:
        if o.type=='MESH':
            for c in o.bound_box: pts.append(o.matrix_world@Vector(c))
    dims=[max(p.x for p in pts)-min(p.x for p in pts), max(p.z for p in pts)-min(p.z for p in pts), max(p.y for p in pts)-min(p.y for p in pts)]
    bpy.ops.object.select_all(action='DESELECT')
    for o in [root]+list(root.children_recursive): o.select_set(True)
    bpy.context.view_layer.objects.active=root
    fn=outdir+re.sub(r'[^A-Za-z0-9_.-]','_',root.name)+'.glb'
    bpy.ops.export_scene.gltf(filepath=fn,use_selection=True,export_format='GLB',export_extras=True)
    return fn,[round(d,4) for d in dims]

def cleanup():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for m in list(bpy.data.meshes):
        if m.users==0: bpy.data.meshes.remove(m)
    for cu in list(bpy.data.curves):
        if cu.users==0: bpy.data.curves.remove(cu)

def run_batch(items, outdir='/projects/catalogue_panneaux/glb_svg/'):
    res=[]
    for it in items:
        try:
            r=make_from_svg(it['code'],it['svg'],it['path'],it['width_m'],it['meta'],it.get('height_m'))
            fn,d=export_sign(r,outdir)
            res.append({'code':it['code'],'ok':True,'file':fn,'dims_m':d,'parts':len(r.children),'ignores':r.get('elements_hors_forme_ignores',0)})
        except Exception as e:
            res.append({'code':it['code'],'ok':False,'err':str(e)[:160]})
        cleanup()
    return res
