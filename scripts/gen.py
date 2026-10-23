
import bpy, math, os
from mathutils import Vector

def mat(name, rgba, metal=0.0, rough=0.4):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    return m

M = {
 "Rouge_Panneau": lambda: mat("Rouge_Panneau",(0.65,0.02,0.02,1),0,0.35),
 "Blanc_Retro":   lambda: mat("Blanc_Retro",(0.9,0.9,0.88,1),0,0.3),
 "Bleu_Panneau":  lambda: mat("Bleu_Panneau",(0.0,0.12,0.55,1),0,0.35),
 "Noir_Pictogramme": lambda: mat("Noir_Pictogramme",(0.02,0.02,0.02,1),0,0.5),
 "Aluminium_Dos": lambda: mat("Aluminium_Dos",(0.6,0.6,0.62,1),0.9,0.35),
}

def _shape(kind, size, z, th, mname, col, rot=0.0):
    """Forme 2D extrudée dans le plan XY (face = +Z)."""
    if kind == "disc":
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=size/2, depth=th, location=(0,0,z))
    elif kind in ("tri", "tri_inv"):
        R = size/math.sqrt(3)
        bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=R, depth=th, location=(0,0,z))
    elif kind == "oct":
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=size/2/math.cos(math.pi/8), depth=th, location=(0,0,z))
    elif kind == "rect":
        w,h = size
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,z))
        o = bpy.context.object; o.scale = (w,h,th)
    o = bpy.context.object
    if kind == "tri": o.rotation_euler[2] = 0.0
    if kind == "tri_inv": o.rotation_euler[2] = math.pi
    if kind == "oct": o.rotation_euler[2] = math.pi/8
    if rot: o.rotation_euler[2] += rot
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o.data.materials.clear(); o.data.materials.append(M[mname]())
    return o

def _text(body, size, z, th, mname="Noir_Pictogramme", loc=(0,0)):
    c = bpy.data.curves.new("t","FONT"); c.body = body; c.size = size
    c.align_x = "CENTER"; c.align_y = "CENTER"; c.extrude = th/2
    o = bpy.data.objects.new("txt", c); bpy.context.collection.objects.link(o)
    o.location = (loc[0], loc[1], z)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    o.data.materials.clear(); o.data.materials.append(M[mname]())
    return o

def _bar(w,h,z,th,mname,loc=(0,0),rot=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0],loc[1],z))
    o = bpy.context.object; o.scale=(w,h,th); o.rotation_euler[2]=rot
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o.data.materials.clear(); o.data.materials.append(M[mname]())
    return o

def make_sign(code, spec):
    """spec: kind, size, border(mat), fill(mat), border_ratio, picto(list of callables), name"""
    col = bpy.data.collections.new(code); bpy.context.scene.collection.children.link(col)
    layer = bpy.context.view_layer.layer_collection.children[col.name]
    bpy.context.view_layer.active_layer_collection = layer
    k, s = spec["kind"], spec["size"]
    th = 0.002
    objs = []
    # dos aluminium
    objs.append(_shape(k, s*1.0 if k!="rect" else s, 0.0, 0.0015, "Aluminium_Dos", None))
    objs[-1].name = f"{code}_dos"
    z = 0.0015/2 + th/2
    ob = _shape(k, s, z, th, spec["border"], None); ob.name = f"{code}_bord"; objs.append(ob)
    br = spec.get("border_ratio", 0.88)
    inner = (s*br) if k!="rect" else (s[0]-0.012, s[1]-0.012)
    if k in ("tri","tri_inv"): inner = s*br*0.82
    z2 = z + th
    oi = _shape(k, inner, z2, th, spec["fill"], None); oi.name = f"{code}_fond"; objs.append(oi)
    zp = z2 + th
    for i,fn in enumerate(spec.get("picto",[])):
        p = fn(zp, th, s); p.name = f"{code}_picto{i}"; objs.append(p)
    # rattacher à la collection et orienter face à -Y
    for o in objs:
        for c in o.users_collection: c.objects.unlink(o)
        col.objects.link(o)
    root = bpy.data.objects.new(code, None); col.objects.link(root)
    for o in objs: o.parent = root
    root.rotation_euler[0] = math.pi/2
    root["code_iisr"] = code; root["nom"] = spec.get("name",""); root["dimension_m"] = str(s)
    root["statut"] = "provisoire : police et cotes à vérifier contre IISR"
    return root, col
