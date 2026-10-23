
import bpy, math, re, json, os
from mathutils import Vector
GLB='/projects/catalogue_panneaux/glb_svg/'
OUT='/projects/catalogue_panneaux/compositions/'
MAN={m['code']:m for m in json.load(open('/projects/catalogue_panneaux/manifeste.json'))}

def _mat(name,rgba,metal,rough):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=rgba; b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    return m

def load_sign(code):
    before=set(bpy.data.objects.keys())
    bpy.ops.import_scene.gltf(filepath=GLB+re.sub(r'[^A-Za-z0-9_.-]','_',code)+'.glb')
    new=[o for o in bpy.data.objects if o.name not in before]
    root=[o for o in new if o.parent is None][0]
    return root, MAN[code]['dims_m'], new

def _cyl(name,r,z0,z1,y,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=z1-z0,location=(0,y,(z0+z1)/2))
    o=bpy.context.object; o.name=name; o.data.materials.append(mat); return o

def assemble(cfg):
    sup=cfg['support']; dia=sup.get('diametre',0.0603); hb=sup.get('hauteur_bord_inferieur',1.0)
    ecart=cfg.get('ecart',0.02); enterre=sup.get('enterre',0.6); depass=sup.get('depassement_haut',0.05)
    root=bpy.data.objects.new(cfg['name'],None); bpy.context.scene.collection.objects.link(root)
    steel=_mat('Acier_Galvanise',(0.55,0.57,0.6,1),0.9,0.4)
    z=hb; parts=[]; objs=[]
    for el in reversed(cfg['elements']):          # liste donnée de haut en bas
        r,(w,h,t),new=load_sign(el['code'])
        r.location=(el.get('dx',0.0),0.0,z+h/2); r.parent=root
        parts.append(dict(code=el['code'],z_bas=round(z,3),z_haut=round(z+h,3),largeur=w,hauteur=h))
        z+=h+ecart
    top=z-ecart
    pole=_cyl(cfg['name']+'_poteau',dia/2,-enterre,top+depass,dia/2+0.003,steel); pole.parent=root
    for p in parts:
        for f in (0.25,0.75):
            zz=p['z_bas']+p['hauteur']*f
            bpy.ops.mesh.primitive_torus_add(major_radius=dia/2+0.002,minor_radius=0.003,location=(0,dia/2+0.003,zz),major_segments=32,minor_segments=8)
            c=bpy.context.object; c.name=cfg['name']+'_collier'; c.data.materials.append(steel); c.parent=root
    root['configuration']=json.dumps({k:v for k,v in cfg.items()},ensure_ascii=False)
    root['elements_calcules']=json.dumps(parts,ensure_ascii=False)
    root['sources_regles']=cfg.get('sources','E030 (sections de supports) ; E073 (hauteur du panneau inférieur)')
    root['statut']=cfg.get('statut','paramètres par défaut IISR ; hauteur et retrait à confirmer par contexte')
    return root,parts,top

def export_comp(root):
    os.makedirs(OUT,exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in [root]+list(root.children_recursive): o.select_set(True)
    bpy.context.view_layer.objects.active=root
    fn=OUT+re.sub(r'[^A-Za-z0-9_.-]','_',root.name)+'.glb'
    bpy.ops.export_scene.gltf(filepath=fn,use_selection=True,export_format='GLB',export_extras=True)
    return fn
