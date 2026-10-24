"""Gabarits paramétriques direction / texte / cartouches / dynamiques — dans Blender.
Exécuté dans le service Blender (exec) : result = run_gabarits([...specs...]).
Police : Bfont Blender (Inter, SIL OFL) = SUBSTITUT provisoire des alphabets IISR L1/L2/L4/L5.
Hauteur de caractère = hauteur de capitale, choisie dans la gamme IISR.
"""
import bpy, math, os, re, json, bmesh
from mathutils import Vector, Matrix
exec(open('/projects/catalogue_panneaux/gen_svg.py').read())  # getmat, cleanup, export_sign

TH = 0.0004
GAMMES = [0.4, 0.32, 0.25, 0.2, 0.16, 0.125, 0.1, 0.08, 0.0625, 0.05, 0.04, 0.032, 0.025]
PAL = {
    'vert': ('Vert_Panneau', (0.0, 0.4, 0.2, 1)), 'bleu': ('Bleu_Panneau', (0.0, 0.12, 0.55, 1)),
    'blanc': ('Blanc_Retro', (0.9, 0.9, 0.88, 1)), 'noir': ('Noir_Pictogramme', (0.02, 0.02, 0.02, 1)),
    'jaune': ('Jaune_Panneau', (0.95, 0.75, 0.0, 1)), 'rouge': ('Rouge_Panneau', (0.65, 0.02, 0.02, 1)),
    'orange': ('Orange_Panneau', (0.9, 0.4, 0.0, 1)), 'marron': ('Marron_Panneau', (0.35, 0.2, 0.1, 1)),
    'ambre': ('Ambre_Dynamique', (1.0, 0.65, 0.05, 1)), 'gris': ('Gris_Panneau', (0.4, 0.4, 0.4, 1)),
}


def mat(name):
    nm, rgba = PAL[name]
    m = getmat(nm, rgba)
    m.diffuse_color = rgba
    return m


def alu():
    m = getmat('Aluminium_Dos', (0.6, 0.6, 0.62, 1), 0.9, 0.35)
    m.diffuse_color = (0.6, 0.6, 0.62, 1)
    return m


def rrect(w, h, r, n=5):
    r = min(r, w / 2, h / 2)
    if r <= 1e-6:
        return [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def arrow_pts(s, deg=0, tail=0.55):
    """Flèche pleine de longueur s (vers +X), tourne de deg."""
    hw = s * 0.16; hh = s * 0.34; hl = s * 0.42
    base = [(-s / 2, -hw), (s / 2 - hl, -hw), (s / 2 - hl, -hh), (s / 2, 0), (s / 2 - hl, hh), (s / 2 - hl, hw), (-s / 2, hw)]
    a = math.radians(deg); c, sn = math.cos(a), math.sin(a)
    return [(x * c - y * sn, x * sn + y * c) for x, y in base]


class Build:
    def __init__(self, code):
        self.code = code; self.parts = []; self.z = 0
        self.col = bpy.data.collections.new(code); bpy.context.scene.collection.children.link(self.col)
        self.root = bpy.data.objects.new(code, None); self.col.objects.link(self.root)

    def _finish(self, obj, material, name, dx=0, dy=0):
        dg = bpy.context.evaluated_depsgraph_get()
        ev = obj.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev)
        me.transform(Matrix.Translation((dx, dy, 0)))
        ob = bpy.data.objects.new(name, me)
        d = getattr(self, '_d', None) or TH
        ob.location = (0, 0, 0.0015 + self.z * TH + (d - TH) / 2)
        ob.data.materials.append(material)
        self.col.objects.link(ob); ob.parent = self.root
        bpy.data.objects.remove(obj)
        self.parts.append(ob); self.z += max(1, int(math.ceil(d / TH - 1e-9))); self._d = None
        return ob

    def poly(self, loops, material, name='f', dx=0, dy=0, depth=None):
        cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'; cu.extrude = (depth or TH) / 2
        for pts in loops:
            sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
            for i, (x, y) in enumerate(pts): sp.points[i].co = (x, y, 0, 1)
            sp.use_cyclic_u = True
        o = bpy.data.objects.new(name, cu); self.col.objects.link(o); self._d = depth
        return self._finish(o, material, f'{self.code}_{name}{self.z:02d}', dx, dy)

    def text(self, s, cx, cy, cap, color, italic=False, spacing=1.0, align='CENTER', maxw=None):
        """Texte dont la hauteur de capitale est cap (m), réduite dans la gamme si largeur > maxw."""
        k = CAPRATIO[0]
        cu = bpy.data.curves.new('t', 'FONT'); cu.body = s; cu.size = 1.0; cu.align_x = align; cu.align_y = 'CENTER'
        cu.extrude = TH / 2; cu.shear = 0.2 if italic else 0.0; cu.space_character = spacing; cu.space_word = spacing
        o = bpy.data.objects.new('t', cu); self.col.objects.link(o)
        dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        xs = [v.co.x for v in me.vertices] or [0, 1]; w1 = max(xs) - min(xs); bpy.data.meshes.remove(me)
        if maxw and w1 > 0:
            cap_max = maxw / w1 * k
            cap = min(cap, cap_max)
            cap = max([g for g in GAMMES if g <= cap + 1e-9] or [cap])
        em = cap / k
        cu.size = em
        dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); me = bpy.data.meshes.new_from_object(ev)
        ob = bpy.data.objects.new(f'{self.code}_txt{self.z:02d}', me)
        ob.location = (cx, cy - 0.0, 0.0015 + self.z * TH)
        ob.data.materials.append(color); self.col.objects.link(ob); ob.parent = self.root
        bpy.data.objects.remove(o); self.parts.append(ob); self.z += 1
        return cap


CAPRATIO = [0.72]


def calibrate():
    cu = bpy.data.curves.new('c', 'FONT'); cu.body = 'H'; cu.size = 1.0
    o = bpy.data.objects.new('c', cu); bpy.context.scene.collection.objects.link(o)
    me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    ys = [v.co.y for v in me.vertices]; CAPRATIO[0] = (max(ys) - min(ys)) or 0.72
    bpy.data.meshes.remove(me); bpy.data.objects.remove(o); bpy.data.curves.remove(cu)
    return CAPRATIO[0]


# ---------------------------------------------------------------- gabarits
def frame(b, W, H, bg, fg, border=0.02, r=0.04):
    b.poly([rrect(W, H, r)], mat(fg), 'cadre')
    b.poly([rrect(W - 2 * border, H - 2 * border, max(r - border, 0.005))], mat(bg), 'fond')


def tpl_position(b, W, H, S):
    frame(b, W, H, S['bg'], S['fg'], r=0.04)
    lines = S['lines'][:2]
    cap = min(0.125 if len(lines) == 1 else 0.1, H * 0.3)
    n = len(lines)
    for i, l in enumerate(lines):
        y = (H / 2 - H * (i + 1) / (n + 1))
        b.text(l, 0, y, cap, mat(S['fg']), S.get('italic', False), maxw=W * 0.86)


def tpl_dirfleche(b, W, H, S):
    frame(b, W, H, S['bg'], S['fg'], r=0.04)
    rows = S['lines'][:3]; n = len(rows)
    rh = (H - 0.1) / n
    ar = S.get('arrow', 180)
    for i, l in enumerate(rows):
        y = H / 2 - 0.05 - rh * (i + 0.5)
        b.poly([arrow_pts(min(rh * 0.8, 0.45), ar)], mat(S['fg']), 'fl', dx=-W / 2 + 0.05 + min(rh * 0.8, 0.45) / 2, dy=y)
        b.text(l, -W / 2 + 0.2 + min(rh * 0.8, 0.45), y, min(0.125, rh * 0.45), mat(S['fg']), False, align='LEFT', maxw=W - 0.4 - min(rh * 0.8, 0.45))


def tpl_presign(b, W, H, S):
    frame(b, W, H, S['bg'], S['fg'], r=0.04)
    sw = 0.05
    b.poly([[(-sw, -H / 2 + 0.15), (sw, -H / 2 + 0.15), (sw, H / 2 - 0.55), (-sw, H / 2 - 0.55)]], mat(S['fg']), 'tige', dx=-W / 4)
    b.poly([arrow_pts(0.5, 90)], mat(S['fg']), 'fl', dx=-W / 4, dy=H / 2 - 0.4)
    b.poly([arrow_pts(0.45, 0)], mat(S['fg']), 'br', dx=-W / 4 + 0.3, dy=0.0)
    n = min(len(S['lines']), 3)
    for i in range(n):
        y = H / 2 - 0.25 - (H - 0.5) * i / max(n - 1, 1) if n > 1 else 0
        b.text(S['lines'][i], W / 8 + 0.05, y, 0.1, mat(S['fg']), False, maxw=W * 0.55)


def tpl_affectation(b, W, H, S):
    frame(b, W, H, S['bg'], S['fg'], r=0.04)
    n = S.get('voies', 3)
    for i in range(n):
        x = -W / 2 + W * (i + 0.5) / n
        b.poly([arrow_pts(H * 0.45, 90 if i < n - 1 else 45)], mat(S['fg']), 'v', dx=x, dy=-H * 0.1)
        if i < n - 1:
            xs = -W / 2 + W * (i + 1) / n
            b.poly([[(-0.01, -H / 2 + 0.1), (0.01, -H / 2 + 0.1), (0.01, H / 2 - 0.1), (-0.01, H / 2 - 0.1)]], mat(S['fg']), 'sep', dx=xs)
    b.text(S['lines'][0], 0, H / 2 - 0.2, 0.1, mat(S['fg']), False, maxw=W * 0.8)


def tpl_cartouche(b, W, H, S):
    frame(b, W, H, S['bg'], S['fg'], border=0.015, r=0.04)
    b.text(S['lines'][0], 0, 0, min(0.125, H * 0.5), mat(S['fg']), False, maxw=W * 0.8)


def tpl_croix(b, W, H, S):
    L = S.get('L', 1.2); w = L * 0.17
    for col, wd in (('rouge', w), ('blanc', w * 0.7)):
        for ang in (45, -45):
            a = math.radians(ang); c, s = math.cos(a), math.sin(a)
            pts = [(-L / 2, -wd / 2), (L / 2, -wd / 2), (L / 2, wd / 2), (-L / 2, wd / 2)]
            b.poly([[(x * c - y * s, x * s + y * c) for x, y in pts]], mat(col), 'bras')
    if S.get('bis'):
        for k, x in enumerate((-0.25, 0.25)):
            b.poly([[(x - 0.07, L * 0.6), (x + 0.07, L * 0.6), (x + 0.07, L * 0.6 + 0.14), (x - 0.07, L * 0.6 + 0.14)]], mat('rouge'), 'feu')


def tpl_balisePN(b, W, H, S):
    frame(b, W, H, 'blanc', 'rouge', border=0.01, r=0.01)
    n = S.get('barres', 1)
    for i in range(n):
        x = -W / 2 + W * (i + 0.5) / n
        b.poly([[(x - 0.05, -H / 2 + 0.05), (x + 0.05, -H / 2 + 0.05), (x + 0.05, H / 2 - 0.05), (x - 0.05, H / 2 - 0.05)]], mat('rouge'), 'b')


def tpl_dynamique(b, W, H, S):
    frame(b, W, H, 'noir', 'gris', border=0.02, r=0.03)
    ls = S['lines'][:3]; n = len(ls)
    for i, l in enumerate(ls):
        y = H / 2 - H * (i + 1) / (n + 1)
        b.text(l, 0, y, min(0.2 if n == 1 else 0.125, H * 0.3), mat(S.get('couleur', 'ambre')), False, spacing=1.1, maxw=W * 0.85)


def tpl_deviation(b, W, H, S):
    frame(b, W, H, 'jaune', 'noir', border=0.02, r=0.04)
    rows = S['lines'][:3]; n = len(rows); rh = (H - 0.1) / n
    for i, l in enumerate(rows):
        y = H / 2 - 0.05 - rh * (i + 0.5)
        if i == 0 and S.get('arrow') is not None:
            b.poly([arrow_pts(min(rh * 0.8, 0.45), S['arrow'])], mat('noir'), 'fl', dx=W / 2 - 0.05 - min(rh * 0.8, 0.45) / 2, dy=y)
        b.text(l, -W / 2 + 0.15, y, min(0.1, rh * 0.45), mat('noir'), False, align='LEFT', maxw=W - 0.6)


def tpl_plaque(b, W, H, S):
    frame(b, W, H, S['bg'], S['fg'], border=0.01, r=0.02)
    ls = S['lines'][:2]; n = len(ls)
    for i, l in enumerate(ls):
        y = H / 2 - H * (i + 1) / (n + 1)
        b.text(l, 0, y, min(0.05, H * 0.28), mat(S['fg']), False, maxw=W * 0.88)


TPL = {'position': tpl_position, 'dirfleche': tpl_dirfleche, 'presign': tpl_presign, 'affectation': tpl_affectation,
       'cartouche': tpl_cartouche, 'croix': tpl_croix, 'balisePN': tpl_balisePN, 'dynamique': tpl_dynamique,
       'deviation': tpl_deviation, 'plaque': tpl_plaque}


def render_png(root, path, W, H, px=384):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading; sh.light = 'FLAT'; sh.color_type = 'MATERIAL'; sh.show_cavity = False
    sc.render.film_transparent = True
    asp = W / H
    sc.render.resolution_x = px if asp >= 1 else int(px * asp); sc.render.resolution_y = int(px / asp) if asp >= 1 else px
    sc.view_settings.view_transform = 'Standard'
    cam = bpy.data.objects.get('_cam')
    if not cam:
        cd = bpy.data.cameras.new('_cam'); cd.type = 'ORTHO'; cam = bpy.data.objects.new('_cam', cd); bpy.context.scene.collection.objects.link(cam)
    cam.data.ortho_scale = max(W, H) * 1.04
    cam.location = (0, -3, 0); cam.rotation_euler = (math.pi / 2, 0, 0)
    sc.camera = cam; sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def run_gabarits(specs, outdir='/projects/catalogue_panneaux/glb_gab/', vigdir='/projects/catalogue_panneaux/vig_gab/'):
    os.makedirs(vigdir, exist_ok=True); os.makedirs(outdir, exist_ok=True)
    calibrate(); res = []
    for S in specs:
        code = S['code']
        try:
            for o in list(bpy.data.objects):
                if o.name != '_cam': bpy.data.objects.remove(o)
            for c in list(bpy.data.collections): bpy.data.collections.remove(c)
            b = Build(code)
            W, H = S['w'], S['h']
            TPL[S['tpl']](b, W, H, S)
            if S.get('dos', S['tpl'] not in ('croix',)):
                back = bpy.data.objects.new(f'{code}_dos', bpy.data.meshes.new(f'{code}_dos'))
                bm = bmesh.new()
                pts = S['dospts'] if S.get('dospts') else rrect(W, H, 0.04)
                vs = [bm.verts.new((x, y, 0)) for x, y in pts]
                f = bm.faces.new(vs); r = bmesh.ops.extrude_face_region(bm, geom=[f])
                for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.z += 0.0012
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
                bm.to_mesh(back.data); bm.free()
                back.data.materials.append(alu()); b.col.objects.link(back); back.parent = b.root
            b.root.rotation_euler[0] = math.pi / 2
            meta = {'code_iisr': code, 'gabarit': S['tpl'], 'contenu_exemple': True, 'statut_dimension': 'provisoire',
                    'police': 'Bfont Blender (Inter, SIL OFL) - substitut des alphabets IISR', 'alphabet_cible': S.get('alphabet', 'L1'),
                    'couleur_fond': S.get('bg', ''), 'aspect': 'generique schematique (a valider)',
                    'licence': 'CC0 (geometrie generee) ; code MIT', 'auteur': 'catalogue 3D panneaux (gabarit parametrique)',
                    'source': 'IISR - dessin schematique', 'dimension_source': 'hypothese', 'dimensions_m': f'{W}x{H}'}
            meta.update(S.get('meta', {}))
            for k, v in meta.items(): b.root[k] = v
            fn, dims = export_sign(b.root, outdir)
            render_png(b.root, vigdir + code + '.png', W, H)
            res.append({'code': code, 'glb': os.path.basename(fn), 'dims': dims, 'faces': sum(len(o.data.polygons) for o in b.parts)})
        except Exception as e:
            res.append({'code': code, 'erreur': repr(e)[:200]})
    return res
