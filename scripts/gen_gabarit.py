"""Gabarits paramétriques direction / texte / cartouches / dynamiques — dans Blender.
Exécuté dans le service Blender (exec) : result = run_gabarits([...specs...]).
Police : Noto Sans CJK Regular (glyphes latins = Source Sans, SIL OFL 1.1, fichier distribue avec Blender) = SUBSTITUT provisoire des alphabets IISR L1/L2/L4/L5.
Hauteur de caractère = hauteur de capitale, choisie dans la gamme IISR.
"""
import bpy, math, os, re, json, bmesh
from mathutils import Vector, Matrix
exec(open('/projects/catalogue_panneaux/gen_svg.py').read())  # getmat, cleanup, export_sign

TH = 0.0004
GAMMES = [0.4, 0.32, 0.25, 0.2, 0.16, 0.125, 0.1, 0.08, 0.0625, 0.05, 0.04, 0.032, 0.025]
def _l(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _rgb(r, g, b):
    return (_l(r), _l(g), _l(b), 1)


PAL = {
    'vert': ('Vert_Panneau', _rgb(0, 112, 74)), 'bleu': ('Bleu_Panneau', _rgb(0, 70, 140)),
    'blanc': ('Blanc_Retro', _rgb(240, 240, 235)), 'noir': ('Noir_Pictogramme', _rgb(20, 20, 20)),
    'jaune': ('Jaune_Panneau', _rgb(255, 204, 0)), 'rouge': ('Rouge_Panneau', _rgb(200, 16, 46)),
    'orange': ('Orange_Panneau', _rgb(240, 120, 0)), 'marron': ('Marron_Panneau', _rgb(89, 52, 28)),
    'ambre': ('Ambre_Dynamique', _rgb(255, 170, 20)), 'gris': ('Gris_Panneau', _rgb(110, 110, 110)),
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
    hw = s * 0.11; hh = s * 0.30; hl = s * 0.40
    base = [(-s / 2, -hw), (s / 2 - hl, -hw), (s / 2 - hl, -hh), (s / 2, 0), (s / 2 - hl, hh), (s / 2 - hl, hw), (-s / 2, hw)]
    a = math.radians(deg); c, sn = math.cos(a), math.sin(a)
    return [(x * c - y * sn, x * sn + y * c) for x, y in base]


class Build:
    def __init__(self, code):
        self.code = code; self.parts = []; self.z = 0; self.caps = []
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
        cu = bpy.data.curves.new('t', 'FONT'); cu.font = get_inter(); cu.body = s; cu.size = 1.0; cu.align_x = align; cu.align_y = 'CENTER'
        cu.fill_mode = FILLMODE[0]; cu.extrude = TH / 2; cu.shear = 0.2 if italic else 0.0; cu.space_character = spacing; cu.space_word = spacing
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
        self.caps.append(round(cap * 1000, 1))
        return cap


FILLMODE = ['BOTH']
CAPRATIO = [0.72]
_INTER = []
FONTPATH = ['/opt/blender/4.0/datafiles/fonts/Noto Sans CJK Regular.woff2']


def get_inter():
    if not _INTER:
        _INTER.append(bpy.data.fonts.load(FONTPATH[0]))
    return _INTER[0]


def calibrate():
    cu = bpy.data.curves.new('c', 'FONT'); cu.font = get_inter(); cu.body = 'H'; cu.size = 1.0
    o = bpy.data.objects.new('c', cu); bpy.context.scene.collection.objects.link(o)
    me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    ys = [v.co.y for v in me.vertices]; CAPRATIO[0] = (max(ys) - min(ys)) or 0.72
    bpy.data.meshes.remove(me); bpy.data.objects.remove(o); bpy.data.curves.remove(cu)
    return CAPRATIO[0]



def row(b, txt, x0, x1, y, cap, col, maxw=None):
    # mention a gauche (x0) et distance eventuelle a droite (x1), separees par |
    if '|' in txt:
        m, d = txt.split('|', 1)
        c = b.text(m, x0, y, cap, col, False, align='LEFT', maxw=(maxw - 0.25) if maxw else None)
        b.text(d, x1, y, c, col, False, align='RIGHT')
    else:
        b.text(txt, x0, y, cap, col, False, align='LEFT', maxw=maxw)


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
        b.text(l.replace('|', '  '), 0, y, cap, mat(S['fg']), S.get('italic', False), maxw=W * 0.86)


def fleche_panneau(W, H, p, sens):
    pts = [(-W / 2, -H / 2), (W / 2 - p, -H / 2), (W / 2, 0), (W / 2 - p, H / 2), (-W / 2, H / 2)]
    return [(-x, y) for x, y in pts][::-1] if sens == 180 else pts


def inset_fleche(W, H, p, sens, d):
    k = p * (H / 2 - d) / (H / 2)
    return fleche_panneau(W - 2 * d, H - 2 * d, k, sens)


def tpl_dirfleche(b, W, H, S):
    ar = S.get('arrow', 0)
    cap = min(0.16, H * 0.2)
    ls = S['lines'][:4]; n = len(ls)
    if ar in (0, 180):
        # panneau de direction en forme de flèche (extrémité pointue), liseré
        p = min(H * 0.38, W * 0.25); d = 0.02
        b.poly([fleche_panneau(W, H, p, ar)], mat(S['fg']), 'cadre')
        b.poly([inset_fleche(W, H, p, ar, d)], mat(S['bg']), 'fond', dx=(-d * 0.0))
        x0 = (-W / 2 + 0.12) if ar == 0 else (-W / 2 + p + 0.12)
        for i, l in enumerate(ls):
            y = H / 2 - H * (i + 1) / (n + 1)
            row(b, l, x0, W / 2 - p - 0.08, y, cap, mat(S['fg']), maxw=W - p - 0.3)
    else:
        # panneau rectangulaire, flèche fine verticale/oblique en tête, mentions alignées à gauche
        frame(b, W, H, S['bg'], S['fg'], r=0.04)
        al = min(H * 0.6, W * 0.16); cap = min(0.16, H * 0.26)
        b.poly([arrow_pts(al, ar, 0.55)], mat(S['fg']), 'fl', dx=-W / 2 + 0.1 + al * 0.5, dy=0)
        x0 = -W / 2 + 0.12 + al * 1.1
        for i, l in enumerate(ls):
            y = H / 2 - H * (i + 1) / (n + 1)
            row(b, l, x0, W / 2 - 0.1, y, cap, mat(S['fg']), maxw=W - (x0 + W / 2) - 0.12)


def tpl_presign(b, W, H, S):
    # presignalisation a diagramme (type D42/D43) : trace fin, mentions au bout des branches
    frame(b, W, H, S['bg'], S['fg'], r=0.04)
    sw = 0.03; xs = -W / 2 + 0.35; yb = -H * 0.05
    b.poly([[(xs - sw, -H / 2 + 0.12), (xs + sw, -H / 2 + 0.12), (xs + sw, H / 2 - 0.4), (xs - sw, H / 2 - 0.4)]], mat(S['fg']), 'tronc')
    b.poly([arrow_pts(0.36, 90)], mat(S['fg']), 'tete', dx=xs, dy=H / 2 - 0.3)
    b.poly([[(xs, yb - sw), (xs + 0.34, yb - sw), (xs + 0.34, yb + sw), (xs, yb + sw)]], mat(S['fg']), 'br')
    b.poly([arrow_pts(0.3, 0)], mat(S['fg']), 'tb', dx=xs + 0.4, dy=yb)
    ls = S['lines'][:3]
    x1 = W / 2 - 0.1
    if ls:
        row(b, ls[0], xs + 0.28, x1, H / 2 - 0.3, 0.125, mat(S['fg']), maxw=x1 - xs - 0.28)
    for l, dy in zip(ls[1:3], (0.14, -0.14)):
        row(b, l, xs + 0.62, x1, yb + dy, 0.1, mat(S['fg']), maxw=x1 - xs - 0.62)


def tpl_affectation(b, W, H, S):
    frame(b, W, H, S['bg'], S['fg'], r=0.04)
    n = S.get('voies', 3)
    for i in range(n):
        x = -W / 2 + W * (i + 0.5) / n
        down = S.get('famille') == 'DA'
        b.poly([arrow_pts(min(H * 0.4, W / n * 0.7), (-90 if i < n - 1 else -45) if down else (90 if i < n - 1 else 45))], mat(S['fg']), 'v', dx=x, dy=-H * 0.17)
        if i < n - 1:
            xs = -W / 2 + W * (i + 1) / n
            b.poly([[(-0.01, -H / 2 + 0.1), (0.01, -H / 2 + 0.1), (0.01, H / 2 - 0.42), (-0.01, H / 2 - 0.42)]], mat(S['fg']), 'sep', dx=xs)
    b.text(S['lines'][0], 0, H / 2 - 0.2, 0.125 if S.get('famille') == 'DA' else 0.1, mat(S['fg']), False, maxw=W * 0.8)


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


def tpl_dircomp(b, W, H, S):
    """Panneau de direction compose PAR CONSTRUCTION (dir_regles.composer) : pile de registres,
    liseré (clair sur fond foncé, noir sur fond clair), registres en flèche pour D2x/Dv/Dc/Dp,
    rectangles alignés (talons/pointes alignés), hauteur de caractère = Hc de chaque registre."""
    G = S['geo']; Wg = G['largeur']; top = H / 2
    for R in G['registres']:
        reg = R['registre']; h = R['h']; cap = R['cap']; fond = reg['fond']; fl = reg.get('fleche')
        clair = fond in ('blanc', 'jaune')
        lis = max(0.012, cap * 0.12); txt = 'noir' if clair else 'blanc'; col_lis = 'noir' if clair else 'blanc'
        cy = top - h / 2; top -= h
        arrowshaped = fl in ('g', 'd') and S.get('arrowshape', True)
        marge = cap * 1.0
        if arrowshaped:
            p = min(h * 0.5, Wg * 0.2); sens = 0 if fl == 'd' else 180
            b.poly([fleche_panneau(Wg, h, p, sens)], mat(col_lis), 'lis', dy=cy)
            b.poly([inset_fleche(Wg, h, p, sens, lis)], mat(fond), 'reg', dy=cy)
            x0 = (-Wg / 2 + marge) if sens == 0 else (-Wg / 2 + p + marge)
            x1 = (Wg / 2 - p - marge * 0.5) if sens == 0 else (Wg / 2 - marge)
        else:
            b.poly([rrect(Wg, h, 0.01)], mat(col_lis), 'lis', dy=cy)
            b.poly([rrect(Wg - 2 * lis, h - 2 * lis, 0.005)], mat(fond), 'reg', dy=cy)
            x0 = -Wg / 2 + marge; x1 = Wg / 2 - marge
            DEG = {'d': 0, 'g': 180, 'h': 90, 'b': -90, 'hd': 45, 'hg': 135}
            if fl in DEG:
                al = min(h * 0.8, 4 * cap)
                b.poly([arrow_pts(al, DEG[fl], 0.55)], mat(txt), 'fl', dx=Wg / 2 - marge - al / 2, dy=cy)
                x1 = Wg / 2 - marge - al * 1.1
        ms = reg['mentions']; n = max(1, len(ms)); ht = R.get('h_txt', h)
        nv = R.get('voies', 0)
        if nv:
            lh = R['lane_h']; al = lh * 0.8
            for k in range(nv):
                deg = -45 if (reg.get('sortie') and k == nv - 1) else -90
                b.poly([arrow_pts(al, deg, 0.55)], mat(txt), 'voie', dx=-Wg / 2 + Wg * (k + 0.5) / nv, dy=cy - h / 2 + lh / 2)
        for i, m in enumerate(ms):
            y = cy + h / 2 - ht * (i + 0.5) / n
            line = m['texte'] + ('|' + m['dist'] if m.get('dist') else '')
            row(b, line, x0, x1, y, cap, mat(txt), maxw=(x1 - x0))

TPL['dircomp'] = tpl_dircomp


def tpl_dirschema(b, W, H, S):
    """Panneaux-schémas D42a (carrefour), D42b (giratoire), D52 (échangeur) : traits épais noirs sur fond blanc,
    cadre foncé, encart de distance ; unité u = Hc (IISR art. 83). Schéma = hypothèse de dessin."""
    K = S['sch']; u = K['u']; kind = K['kind']; lw = 0.7 * u; N = 'noir'
    frame(b, W, H, 'blanc', N, border=0.35 * u, r=0.04)
    def seg(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * lw / 2, dx / L * lw / 2
        return [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]
    def tri(tip, deg, s=2.0 * u):
        a = math.radians(deg); c, sn = math.cos(a), math.sin(a)
        base = [(0, 0), (-s, s * 0.55), (-s, -s * 0.55)]
        return [(tip[0] + x * c - y * sn, tip[1] + x * sn + y * c) for x, y in base]
    def disc(p, rr):
        return [(p[0] + rr * math.cos(2 * math.pi * k / 16), p[1] + rr * math.sin(2 * math.pi * k / 16)) for k in range(16)]
    def line(pts):
        for i in range(len(pts) - 1): b.poly([seg(pts[i], pts[i + 1])], mat(N), 'trait')
        for p in pts[1:-1]: b.poly([disc(p, lw / 2)], mat(N), 'raccord')
    def arrow(pts, deg):
        p, q = pts[-2], pts[-1]; L = math.hypot(q[0] - p[0], q[1] - p[1]); k = max(0.0, (L - 1.8 * u) / L)
        line(pts[:-1] + [(p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)]); b.poly([tri(q, deg)], mat(N), 'pointe')
    L = K['labels']; cap = u
    def lab(t, x, y):
        if t: b.text(t, x, y, cap, mat(N), False, align='CENTER')
    if kind == 'carrefour':
        line([(0, -8 * u), (0, 0)])
        arrow([(0, 0), (0, 4.6 * u)], 90); arrow([(0, 0), (-6.6 * u, 0)], 180); arrow([(0, 0), (6.6 * u, 0)], 0)
        lab(L.get('haut'), 0, 6.9 * u); lab(L.get('gauche'), -7.6 * u, 2.5 * u); lab(L.get('droite'), 7.6 * u, 2.5 * u)
    elif kind == 'giratoire':
        cx, cy, r = 0, 0, 3.0 * u
        ring = lambda rr: [(cx + rr * math.cos(2 * math.pi * i / 48), cy + rr * math.sin(2 * math.pi * i / 48)) for i in range(48)]
        b.poly([ring(r + lw / 2), ring(r - lw / 2)], mat(N), 'anneau')
        line([(0, -8 * u), (0, -r)])
        arrow([(0, r), (0, 6.0 * u)], 90); arrow([(-r, 0), (-8.0 * u, 0)], 180); arrow([(r, 0), (8.0 * u, 0)], 0)
        lab(L.get('haut'), 0, 7.9 * u); lab(L.get('gauche'), -8.6 * u, 2.5 * u); lab(L.get('droite'), 8.6 * u, 2.5 * u)
    else:  # echangeur
        line([(-4 * u, -8 * u), (-4 * u, 1.0 * u)]); arrow([(-4 * u, 1.0 * u), (-4 * u, 5.0 * u)], 90)
        arrow([(-4 * u, -3 * u), (3 * u, 1.5 * u), (3 * u, 5.0 * u)], 90)
        lab(L.get('haut'), -4 * u, 7.0 * u); lab(L.get('droite'), 4.6 * u, 7.0 * u)
    if K.get('encart'):
        bw, bh = 5.4 * u, 2.3 * u; bx, by = -W / 2 + 0.35 * u + 0.6 * u + bw / 2, -H / 2 + 0.35 * u + 0.6 * u + bh / 2
        b.poly([rrect(bw, bh, 0.01)], mat(N), 'encart_c', dx=bx, dy=by)
        b.poly([rrect(bw - 0.3 * u, bh - 0.3 * u, 0.005)], mat('blanc'), 'encart_f', dx=bx, dy=by)
        b.text(K['encart'], bx, by, cap, mat(N), False, align='CENTER')

TPL['dirschema'] = tpl_dirschema




BG_TRANSP = [True]


def render_png(root, path, W, H, px=384):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading; sh.light = 'FLAT'; sh.color_type = 'MATERIAL'; sh.show_cavity = False
    sc.render.film_transparent = BG_TRANSP[0]
    if not BG_TRANSP[0]:
        sc.world.use_nodes = False; sc.world.color = (0.62, 0.66, 0.70); sh.background_type = 'WORLD'
    asp = min(max(W / H, 0.25), 4.0)
    sc.world = sc.world or bpy.data.worlds.new('w')
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
                    'police': 'Noto Sans CJK Regular (latin = Source Sans, SIL OFL 1.1) - substitut des alphabets IISR', 'hauteur_caractere_mm': ';'.join(str(c) for c in sorted(set(b.caps), reverse=True)), 'gamme_mm': ';'.join(str(c) for c in sorted(set(b.caps), reverse=True)), 'capratio_police': round(CAPRATIO[0], 4), 'alphabet_cible': S.get('alphabet', 'L1'),
                    'couleur_fond': S.get('bg', ''), 'aspect': 'generique schematique (a valider)',
                    'licence': 'CC0 (geometrie generee) ; code MIT', 'auteur': 'catalogue 3D panneaux (gabarit parametrique)',
                    'source': 'IISR - dessin schematique', 'dimension_source': 'hypothese', 'dimensions_m': f'{W}x{H}'}
            meta.update(S.get('meta', {}))
            for k, v in meta.items(): b.root[k] = v
            fn, dims = export_sign(b.root, outdir)
            BG_TRANSP[0] = bool(S.get('dos', S['tpl'] not in ('croix',)))
            render_png(b.root, vigdir + code + '.png', W, H)
            res.append({'code': code, 'glb': os.path.basename(fn), 'dims': dims, 'faces': sum(len(o.data.polygons) for o in b.parts)})
        except Exception as e:
            res.append({'code': code, 'erreur': repr(e)[:200]})
    return res
