"""Objets non plats ou sans source : feux, balises, dispositifs, formes-types (silhouettes).
Etend gen_gabarit.py : TPL['dessin'] (liste de primitives) et TPL['forme'] (forme-type + code)."""
exec(open('/projects/catalogue_panneaux/gen_gabarit.py').read())


def circle(r, cx=0.0, cy=0.0, n=40):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def tri_pts(side, k=1.0):
    h = side * 0.866025 * k; s = side * k
    return [(0, 2 * h / 3), (-s / 2, -h / 3), (s / 2, -h / 3)]


def add_back(b, pts):
    back = bpy.data.objects.new(f'{b.code}_dos', bpy.data.meshes.new(f'{b.code}_dos'))
    bm = bmesh.new(); vs = [bm.verts.new((x, y, 0)) for x, y in pts]
    f = bm.faces.new(vs); r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.z += 0.0012
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(back.data); bm.free()
    back.data.materials.append(alu()); b.col.objects.link(back); back.parent = b.root


def solid(b, kind, cx, y0, r1, r2, h, col):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=28, radius1=r1, radius2=r2, depth=h)
    me = bpy.data.meshes.new('s'); bm.to_mesh(me); bm.free()
    me.transform(Matrix.Rotation(-math.pi / 2, 4, 'X')); me.transform(Matrix.Translation((cx, y0 + h / 2, 0.0015 + max(r1, r2))))
    ob = bpy.data.objects.new(f'{b.code}_sol{len(b.parts):02d}', me); ob.data.materials.append(mat(col))
    b.col.objects.link(ob); ob.parent = b.root; b.parts.append(ob)


def rect_pts(cx, cy, w, h):
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]


def rot(pts, deg, cx=0, cy=0):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def symbole(name, d):
    """Boucles (liste de listes de points) d'un symbole de diamètre d, centré en 0."""
    if name.startswith('fleche'):
        deg = {'fleche_d': 0, 'fleche_g': 180, 'fleche_h': 90, 'fleche_b': -90, 'fleche_hd': 45, 'fleche_hg': 135}[name]
        return [arrow_pts(d * 0.8, deg)]
    if name == 'pieton':
        return [circle(0.09 * d, 0, 0.32 * d, 16), rect_pts(0, 0.05 * d, 0.2 * d, 0.38 * d), rect_pts(-0.06 * d, -0.26 * d, 0.07 * d, 0.34 * d), rect_pts(0.06 * d, -0.26 * d, 0.07 * d, 0.34 * d)]
    if name == 'velo':
        return [circle(0.2 * d, -0.26 * d, -0.1 * d, 24), circle(0.15 * d, -0.26 * d, -0.1 * d, 24), circle(0.2 * d, 0.26 * d, -0.1 * d, 24), circle(0.15 * d, 0.26 * d, -0.1 * d, 24), rot(rect_pts(0, 0.05 * d, 0.5 * d, 0.05 * d), 20)]
    if name in ('bus', 'tram'):
        L = [rect_pts(0, 0, 0.62 * d, 0.4 * d), rect_pts(-0.18 * d, 0.05 * d, 0.14 * d, 0.12 * d), rect_pts(0.0, 0.05 * d, 0.14 * d, 0.12 * d), rect_pts(0.18 * d, 0.05 * d, 0.14 * d, 0.12 * d)]
        if name == 'tram': L.append(rect_pts(0, 0.3 * d, 0.3 * d, 0.04 * d))
        return L
    if name == 'croix':
        return [rot(rect_pts(0, 0, 0.8 * d, 0.14 * d), 45), rot(rect_pts(0, 0, 0.8 * d, 0.14 * d), -45)]
    if name == 'barre_g': return [rot(rect_pts(0, 0, 0.8 * d, 0.16 * d), 45)]
    if name == 'barre_d': return [rot(rect_pts(0, 0, 0.8 * d, 0.16 * d), -45)]
    return []


def tpl_dessin(b, W, H, S):
    for it in S['items']:
        k = it[0]
        if k == 'rect':
            _, cx, cy, w, h, col, dp = it[:7]; r = it[7] if len(it) > 7 else 0
            b.poly([rrect(w, h, r) if r else rect_pts(0, 0, w, h)], mat(col), 'r', dx=cx, dy=cy, depth=dp)
        elif k == 'poly':
            _, pts, col, dp = it; b.poly([pts], mat(col), 'p', depth=dp)
        elif k == 'disc':
            _, cx, cy, r, col, dp = it; b.poly([circle(r, cx, cy)], mat(col), 'd', depth=dp)
        elif k == 'ring':
            _, cx, cy, r, rin, col, dp = it; b.poly([circle(r, cx, cy), circle(rin, cx, cy)], mat(col), 'o', depth=dp)
        elif k == 'sym':
            _, name, cx, cy, d, col = it; b.poly(symbole(name, d), mat(col), 's', dx=cx, dy=cy)
        elif k == 'solid':
            _, cx, y0, r1, r2, h, col = it; solid(b, 'cone', cx, y0, r1, r2, h, col)
        elif k == 'text':
            _, s, cx, cy, cap, col = it[:6]; b.text(s, cx, cy, cap, mat(col), False, maxw=it[6] if len(it) > 6 else None)
        elif k == 'bands':   # bandes alternées horizontales : cx,cy,w,h,n,col1,col2,depth
            _, cx, cy, w, h, n, c1, c2, dp = it
            for i in range(n):
                b.poly([rect_pts(0, 0, w, h / n)], mat(c1 if i % 2 == 0 else c2), 'b', dx=cx, dy=cy + h / 2 - h * (i + 0.5) / n, depth=dp)


def tpl_forme(b, W, H, S):
    f = S['forme']; code = S['lines'][0]
    if f == 'triangle':
        add_back(b, tri_pts(W)); b.poly([tri_pts(W)], mat('rouge'), 'ext'); b.poly([tri_pts(W, 0.72)], mat('blanc'), 'int', dy=-W * 0.02)
        b.text(code, 0, -W * 0.1, 0.1, mat('noir'), maxw=W * 0.4)
    elif f in ('disque_rouge', 'disque_bleu'):
        R = W / 2; add_back(b, circle(R))
        if f == 'disque_rouge':
            b.poly([circle(R)], mat('rouge'), 'ext'); b.poly([circle(R * 0.8)], mat('blanc'), 'int')
            tc = 'noir'
        else:
            b.poly([circle(R)], mat('bleu'), 'ext'); b.poly([circle(R * 0.92)], mat('bleu'), 'int'); tc = 'blanc'
        top = S.get('haut')
        if top: b.text(top, 0, R * 0.38, 0.05, mat(tc), maxw=W * 0.6)
        b.text(code if not S.get('valeur') else S['valeur'], 0, 0 if not top else -R * 0.08, 0.125 if S.get('valeur') else 0.08, mat(tc), maxw=W * 0.6)
        if S.get('barre'): b.poly([rot(rect_pts(0, 0, W * 0.86, W * 0.07), 45)], mat('noir'), 'barre')
    else:
        add_back(b, rrect(W, H, 0.04)); frame(b, W, H, S['bg'], S['fg'], border=0.02, r=0.04)
        ls = S['lines'][:3]; n = len(ls)
        for i, l in enumerate(ls):
            b.text(l, 0, H / 2 - H * (i + 1) / (n + 1), min(0.1, H * 0.3), mat(S['fg']), maxw=W * 0.88)
        if S.get('barre'): b.poly([rot(rect_pts(0, 0, max(W, H) * 0.95, 0.05), 45)], mat('noir'), 'barre')


TPL['dessin'] = tpl_dessin
TPL['forme'] = tpl_forme
