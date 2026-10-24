"""Pictogrammes parametriques (lot L6) -> specs 'dessin'. Pur Python. Tout est HYPOTHESE de dessin (formes IISR non disponibles en vecteur)."""
import math, json, csv, textwrap

def circ(r, cx=0.0, cy=0.0, n=40):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
def tri(side, k=1.0, cy=0.0):
    h = side * 0.866025 * k; s = side * k
    return [(0, 2 * h / 3 + cy), (-s / 2, -h / 3 + cy), (s / 2, -h / 3 + cy)]
def rot(pts, deg, cx=0, cy=0):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]
def rc(cx, cy, w, h):
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
def arc(cx, cy, r, a0, a1, n=14):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
def stroke(path, w):
    L, R = [], []
    for i, (x, y) in enumerate(path):
        if i == 0: dx, dy = path[1][0] - x, path[1][1] - y
        elif i == len(path) - 1: dx, dy = x - path[i - 1][0], y - path[i - 1][1]
        else: dx, dy = path[i + 1][0] - path[i - 1][0], path[i + 1][1] - path[i - 1][1]
        n = math.hypot(dx, dy) or 1; nx, ny = -dy / n * w / 2, dx / n * w / 2
        L.append((x + nx, y + ny)); R.append((x - nx, y - ny))
    return L + R[::-1]
def head(x, y, deg, s):
    return rot([(x + s, y), (x - s * 0.2, y + s * 0.62), (x - s * 0.2, y - s * 0.62)], deg, x, y)
def arrow_path(path, w, hs):
    xe, ye = path[-1]; k = hs * 0.8
    q = list(path)
    while len(q) > 2 and math.hypot(q[-1][0] - q[-2][0], q[-1][1] - q[-2][1]) < 1e-9: q.pop()
    # retire les points trop proches de la pointe
    while len(q) > 2 and math.hypot(xe - q[-2][0], ye - q[-2][1]) < k: q.pop(-2)
    (x0, y0) = q[-2]; deg = math.degrees(math.atan2(ye - y0, xe - x0)); c, sn = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    bx, by = xe - k * c, ye - k * sn
    p2 = q[:-1] + [(bx, by)]
    return [stroke(p2, w), head(bx, by, deg, hs * 1.3)]

def P(pts, col): return ['poly', pts, col, None]
def PP(loops, col): return [P(l, col) for l in loops]
def D(cx, cy, r, col): return ['disc', cx, cy, r, col, None]
def RG(cx, cy, r, ri, col): return ['ring', cx, cy, r, ri, col, None]
def R(cx, cy, w, h, col, rad=0): return ['rect', cx, cy, w, h, col, None, rad]
def T(s, cx, cy, cap, col, maxw=None): return ['text', s, cx, cy, cap, col] + ([maxw] if maxw else [])

def sym_car(cx, cy, d, col='noir'):
    return [P(rc(cx, cy - 0.04 * d, 0.7 * d, 0.2 * d), col), P([(cx - 0.2 * d, cy + 0.06 * d), (cx - 0.1 * d, cy + 0.2 * d), (cx + 0.15 * d, cy + 0.2 * d), (cx + 0.25 * d, cy + 0.06 * d)], col),
            D(cx - 0.22 * d, cy - 0.15 * d, 0.07 * d, col), D(cx + 0.22 * d, cy - 0.15 * d, 0.07 * d, col)]
def sym_bus(cx, cy, d, col='noir', tram=False, win='blanc'):
    it = [P(rc(cx, cy, 0.7 * d, 0.42 * d), col)] + [P(rc(cx + k * 0.19 * d, cy + 0.06 * d, 0.13 * d, 0.13 * d), win) for k in (-1, 0, 1)]
    it += [D(cx - 0.22 * d, cy - 0.22 * d, 0.06 * d, col), D(cx + 0.22 * d, cy - 0.22 * d, 0.06 * d, col)]
    if tram: it += [P(rc(cx, cy + 0.32 * d, 0.34 * d, 0.04 * d), col), P(rc(cx, cy + 0.26 * d, 0.03 * d, 0.1 * d), col)]
    return it
def sym_feu(cx, cy, d, cols=('rouge', 'ambre', 'vert'), n=3):
    w = 0.32 * d; h = 0.9 * d if n == 3 else 0.6 * d
    it = [R(cx, cy, w, h, 'noir', 0.04 * d)]
    ys = [cy + 0.3 * d, cy, cy - 0.3 * d] if n == 3 else [cy + 0.15 * d, cy - 0.15 * d]
    return it + [D(cx, y, 0.1 * d, c) for y, c in zip(ys, cols)]
def sym_animal(cx, cy, d, col='noir'):
    it = [P(rc(cx - 0.03 * d, cy, 0.5 * d, 0.2 * d), col)]
    for dx in (-0.25, -0.15, 0.1, 0.2): it.append(P(rc(cx + dx * d, cy - 0.2 * d, 0.05 * d, 0.3 * d), col))
    it.append(P([(cx + 0.18 * d, cy + 0.05 * d), (cx + 0.3 * d, cy + 0.32 * d), (cx + 0.38 * d, cy + 0.3 * d), (cx + 0.3 * d, cy + 0.0), (cx + 0.24 * d, cy - 0.06 * d)], col))
    it.append(P(stroke([(cx + 0.31 * d, cy + 0.32 * d), (cx + 0.3 * d, cy + 0.5 * d), (cx + 0.38 * d, cy + 0.6 * d)], 0.03 * d), col))
    it.append(P(stroke([(cx + 0.31 * d, cy + 0.32 * d), (cx + 0.22 * d, cy + 0.5 * d), (cx + 0.14 * d, cy + 0.58 * d)], 0.03 * d), col))
    return it
def sym_camera(cx, cy, d, col='noir'):
    return [P(rc(cx, cy, 0.7 * d, 0.38 * d), col), P([(cx + 0.35 * d, cy + 0.12 * d), (cx + 0.55 * d, cy + 0.22 * d), (cx + 0.55 * d, cy - 0.22 * d), (cx + 0.35 * d, cy - 0.12 * d)], col), D(cx - 0.1 * d, cy, 0.1 * d, 'blanc')]
def sym_pump(cx, cy, d, col='noir'):
    return [P(rc(cx - 0.1 * d, cy, 0.4 * d, 0.8 * d), col), P(rc(cx - 0.1 * d, cy + 0.2 * d, 0.26 * d, 0.22 * d), 'blanc'),
            P(stroke([(cx + 0.1 * d, cy + 0.3 * d), (cx + 0.28 * d, cy + 0.2 * d), (cx + 0.28 * d, cy - 0.15 * d)], 0.05 * d), col)]
def sym_plug(cx, cy, d, col='noir'):
    return [P(rc(cx, cy - 0.05 * d, 0.3 * d, 0.4 * d), col), P(rc(cx - 0.07 * d, cy + 0.28 * d, 0.05 * d, 0.2 * d), col), P(rc(cx + 0.07 * d, cy + 0.28 * d, 0.05 * d, 0.2 * d), col),
            P(rc(cx, cy - 0.35 * d, 0.06 * d, 0.2 * d), col)]
def sym_pieton(cx, cy, d, col='noir'):
    return [['sym', 'pieton', cx, cy, d, col]]
def bar(cx, cy, L, w, deg, col): return P(rot(rc(cx, cy, L, w), deg, cx, cy), col)
def cadre(W, H, bg, fg, b=0.02, r=0.04): return [R(0, 0, W, H, fg, r), R(0, 0, W - 2 * b, H - 2 * b, bg, max(r - b, 0.005))]

def spec_tri(code, inner, meta=''):
    it = [P(tri(1.0), 'rouge'), P(tri(1.0, 0.74), 'blanc')] + inner
    return dict(code=code, tpl='dessin', w=1.0, h=0.866, items=it, dos=True, dospts=tri(1.0), meta={'type_objet': 'pictogramme', 'aspect': 'dessin parametrique (hypothese)' + meta})
def spec_disc(code, bg, inner, W=0.65, ring='rouge', listel='blanc'):
    R0 = W / 2
    if bg == 'blanc': it = [D(0, 0, R0, ring), D(0, 0, R0 * 0.8, 'blanc')]
    else: it = [D(0, 0, R0, bg), RG(0, 0, R0 * 0.93, R0 * 0.88, listel)]
    return dict(code=code, tpl='dessin', w=W, h=W, items=it + inner, dos=True, dospts=circ(R0), meta={'type_objet': 'pictogramme', 'aspect': 'dessin parametrique (hypothese)'})
def spec_panel(code, W, H, bg, fg, inner, rad=0.04, b=0.02):
    return dict(code=code, tpl='dessin', w=W, h=H, items=cadre(W, H, bg, fg, b, rad) + inner, dos=True, meta={'type_objet': 'pictogramme', 'aspect': 'dessin parametrique (hypothese)'})

def court(lib, maxc=28):
    import re
    t = re.split(r'[:;(\u2013]', lib or '')[0].strip()
    return t if 3 <= len(t) <= maxc else None
def lignes(txt, n=3, w=16):
    return textwrap.wrap(txt.upper(), w)[:n]

def texte_bloc(lines, W, H, col, cap=None):
    n = len(lines); cap = cap or min(0.09, H * 0.7 / max(n, 1) / 1.5)
    return [T(l, 0, H / 2 - H * (i + 1) / (n + 1), cap, col, W * 0.88) for i, l in enumerate(lines)]
def arrow_sym(cx, cy, s, deg, col):
    base = [(-s / 2, -s * 0.11), (s / 2 - s * 0.4, -s * 0.11), (s / 2 - s * 0.4, -s * 0.3), (s / 2, 0), (s / 2 - s * 0.4, s * 0.3), (s / 2 - s * 0.4, s * 0.11), (-s / 2, s * 0.11)]
    return P([(cx + x, cy + y) for x, y in rot(base, deg)], col)

def build(code, lib, fam):
    c = code
    if c == 'A1':
        return spec_tri(c, PP(arrow_path([(-0.06, -0.22), (-0.06, -0.04)] + arc(0.12, -0.04, 0.18, 180, 90, 18)[1:] + [(0.2, 0.14)], 0.075, 0.08), 'noir'))
    if c == 'A2':
        pth = [(-0.1, -0.22), (-0.1, -0.12), (-0.08, -0.03), (0.0, 0.03), (0.08, 0.08), (0.1, 0.14), (0.1, 0.2)]
        return spec_tri(c, PP(arrow_path(pth, 0.06, 0.06), 'noir'))
    if c == 'A7bis': return spec_tri(c, sym_feu(0, -0.03, 0.4) + [D(-0.2, -0.17, 0.025, 'rouge'), D(0.2, -0.17, 0.025, 'rouge')])
    if c == 'A8bis': return spec_tri(c, sym_feu(0, 0.0, 0.34, ('ambre', 'ambre'), 2) + [T('FEU CLIGNOTANT', 0, -0.2, 0.04, 'noir', 0.5)])
    if c == 'A9a': return spec_tri(c, sym_bus(0, -0.04, 0.42))
    if c == 'A9b': return spec_tri(c, sym_bus(0, -0.04, 0.42, tram=True))
    if c == 'A15': return spec_tri(c, sym_animal(0, -0.06, 0.4))
    barre_r = lambda col: bar(0, 0, 0.5, 0.05, 45, col)
    if c in ('B2', 'B2a'): return spec_disc(c, 'blanc', [arrow_sym(0, -0.02, 0.3, 135, 'noir')] + [bar(0, 0, 0.5, 0.045, 45, 'rouge')])
    if c == 'B6a' or c == 'B6': return spec_disc(c, 'bleu', [RG(0, 0, 0.29, 0.255, 'rouge'), bar(0, 0, 0.58, 0.05, 45, 'rouge')])
    if c == 'B6b': return spec_panel(c, 0.65, 0.65, 'bleu', 'blanc', [RG(0, 0, 0.26, 0.23, 'rouge'), bar(0, 0, 0.5, 0.045, 45, 'rouge')], 0.03)
    if c == 'B21a': return spec_disc(c, 'bleu', [arrow_sym(0, 0, 0.42, -135, 'blanc')])
    if c == 'B25': return spec_disc(c, 'bleu', [T('30', 0, -0.02, 0.2, 'blanc', 0.38), bar(0, -0.12, 0.3, 0.012, 0, 'blanc')])
    if c == 'B43': return spec_disc(c, 'bleu', [T('30', 0, 0, 0.2, 'blanc', 0.38), barre_r('noir')])
    if c == 'B45': return spec_disc(c, 'bleu', sym_bus(0, 0, 0.4, 'blanc', win='bleu') + [barre_r('noir')])
    if c == 'B30': return spec_panel(c, 0.65, 0.9, 'blanc', 'noir', [RG(0, 0.16, 0.26, 0.208, 'rouge'), T('30', 0, 0.16, 0.14, 'noir', 0.3), T('ZONE', 0, -0.25, 0.1, 'noir', 0.5)], 0.03)
    if c == 'B51': return spec_panel(c, 0.65, 0.9, 'blanc', 'noir', [RG(0, 0.16, 0.26, 0.208, 'rouge'), T('30', 0, 0.16, 0.14, 'noir', 0.3), T('ZONE', 0, -0.25, 0.1, 'noir', 0.5), bar(0, 0, 0.78, 0.04, 45, 'noir')], 0.03)
    if c == 'B50': return spec_panel(c, 0.65, 0.9, 'blanc', 'noir', [D(0, 0.1, 0.26, 'bleu'), RG(0, 0.1, 0.2, 0.17, 'rouge'), bar(0, 0.1, 0.4, 0.04, 45, 'rouge'), T('ZONE', 0, -0.28, 0.08, 'noir', 0.5), bar(0, 0, 0.78, 0.04, 45, 'noir')], 0.03)
    if c.startswith('C117-B21'):
        v = c[8:]; deg = {'c1': -135, 'c2': -45, 'd1': 180, 'd2': 0, 'e': -90}.get(v, -90)
        return spec_panel(c, 0.65, 0.65, 'blanc', 'noir', [D(0, 0.1, 0.17, 'bleu'), arrow_sym(0, 0.1, 0.24, deg, 'blanc'), T('TUNNEL', 0, -0.2, 0.08, 'noir', 0.5)], 0.03)
    if c == 'SE2':
        return spec_panel(c, 0.65, 0.65, 'bleu', 'blanc', [P(rc(0, 0, 0.1, 0.5), 'blanc'), P(rc(0, 0, 0.5, 0.1), 'blanc'), P(rot(rc(0, 0, 0.1, 0.5), 45), 'blanc'), T('ÉCHANGEUR', 0, -0.26, 0.05, 'blanc', 0.5)], 0.03)
    if c == 'SC17':
        return spec_panel(c, 0.65, 0.65, 'bleu', 'blanc', [T('A', 0, 0.08, 0.18, 'blanc', 0.3), T('AUTOROUTIER', 0, -0.2, 0.05, 'blanc', 0.55), bar(0, -0.1, 0.4, 0.015, 0, 'blanc')], 0.03)
    if c == 'C4a': return spec_panel(c, 0.65, 0.65, 'bleu', 'blanc', [T('50', 0, 0, 0.2, 'blanc', 0.5)], 0.03)
    if c == 'C4b': return spec_panel(c, 0.65, 0.65, 'bleu', 'blanc', [T('50', 0, 0, 0.2, 'blanc', 0.5), bar(0, 0, 0.9, 0.04, 45, 'noir')], 0.03)
    if c == 'CE15': return spec_panel(c, 0.65, 0.65, 'bleu', 'blanc', sym_pump(0, 0, 0.5, 'blanc'), 0.03)
    if c == 'CE15b': return spec_panel(c, 0.65, 0.65, 'bleu', 'blanc', sym_pump(-0.08, 0, 0.45, 'blanc') + sym_plug(0.18, 0, 0.3, 'blanc'), 0.03)
    if c == 'CE30': return spec_panel(c, 0.65, 0.65, 'vert', 'blanc', [P(rc(0.2, 0, 0.14, 0.4), 'blanc')] + sym_pieton(-0.1, 0, 0.45, 'blanc') + [arrow_sym(0.0, -0.22, 0.3, 0, 'blanc')], 0.03)
    if c in ('C64', 'C64d', 'CE64d'): return spec_panel(c, 0.65, 0.65, 'bleu', 'blanc', [R(0, 0.02, 0.4, 0.26, 'blanc', 0.02), R(0, 0.07, 0.4, 0.05, 'bleu'), T('CB', 0, -0.2, 0.08, 'blanc', 0.3)], 0.03)
    if c == 'ID34': return spec_panel(c, 0.4, 0.4, 'bleu', 'blanc', sym_pieton(0, 0, 0.32, 'blanc'), 0.03)
    if c.startswith('SR2'):
        n = {'SR2a': 1, 'SR2b': 2, 'SR2c': 3}.get(c, 2)
        cars = []
        for i in range(n): cars += sym_car(-0.34 * (n - 1) / 2 + 0.34 * i, 0.07, 0.28, 'blanc')
        return spec_panel(c, 1.0, 0.75, 'bleu', 'blanc', cars + [T('ESPACEMENT', 0, -0.22, 0.07, 'blanc', 0.8)])
    if c.startswith('SR52'): return spec_panel(c, 1.0, 0.75, 'bleu', 'blanc', sym_car(-0.2, 0.1, 0.26, 'blanc') + sym_car(0.2, 0.1, 0.26, 'blanc') + [T('50 m', 0, -0.2, 0.1, 'blanc', 0.6)])
    if c == 'SR3': return spec_panel(c, 1.0, 0.75, 'bleu', 'blanc', sym_camera(0, 0.08, 0.38, 'blanc') + [T('CONTRÔLE AUTOMATISÉ', 0, -0.22, 0.055, 'blanc', 0.85)])
    if c == 'SR4': return spec_panel(c, 1.0, 0.75, 'bleu', 'blanc', sym_camera(0, 0.08, 0.38, 'blanc') + [T('VIDÉOPROTECTION', 0, -0.22, 0.06, 'blanc', 0.85)])
    if fam in ('M', 'KM'):
        bg = 'jaune' if fam == 'KM' else 'blanc'
        W, H = 0.5, 0.35
        txt = {'M9': ['VERGLAS', 'FRÉQUENT'], 'M9z': ['INSCRIPTION', 'LIBRE'], 'KM9': ['TRAVAUX'], 'KM1': ['500 m'], 'KM2': ['2 km'],
               'M4': ['POIDS LOURDS'], 'M6d': ['PAYANT', 'PARCMÈTRE'], 'M6b': ['ALTERNÉ', '1-15 / 16-31'], 'M11d': ['ZFE-m'], 'M11c': ['TUNNEL', 'B C D E'], 'M11b': ['7 h - 19 h'], 'M6': ['ARRÊT', 'INTERDIT'], 'M8': ['SAUF', 'LIVRAISONS'], 'M10': ['A 7'], 'M10c2': ['E 714'], 'M11': ['SAUF', 'RIVERAINS'], 'M6f': ['8 h - 18 h', '2 h MAX']}.get(c)
        if c in ('M3', 'M3a', 'M3b'):
            it = [arrow_sym(-0.1, 0, 0.26, 0 if c != 'M3a' else 180, 'noir')] + ([T('BUS', 0.15, 0, 0.07, 'noir', 0.2)] if c == 'M3b' else [])
        elif c == 'M12':
            return dict(code=c, tpl='dessin', w=0.5, h=0.433, items=[P(tri(0.5), 'noir'), P(tri(0.5, 0.86), 'blanc'), T('STOP', 0, -0.03, 0.06, 'noir', 0.25)], dos=True, dospts=tri(0.5), meta={'type_objet': 'pictogramme', 'aspect': 'dessin parametrique (hypothese)'})
        else:
            it = texte_bloc(txt or lignes(lib or c, 2, 14), W, H, 'noir')
        return spec_panel(c, W, H, bg, 'noir', it)
    if fam == 'H':
        txt = {'H20': ['ROUTE DES', 'VINS'], 'H10': ['ABBAYE', 'DE SÉNANQUE'], 'H11': ['ABBAYE'], 'H12': ['ABBAYE', 'DE SÉNANQUE'], 'H13': ['ABBAYE DE', 'SÉNANQUE', 'XIIe SIÈCLE'], 'H30': ['PATRIMOINE', 'CULTUREL'],
               'H21': ['ROUTE DES VINS'], 'H22': ['ROUTE DES VINS'], 'H23': ['ROUTE DES VINS'], 'H24': ['FIN DE LA', 'ROUTE DES VINS'], 'H31': ['SITE'], 'H32': ['SITE', 'TOURISTIQUE'], 'H33': ['SITE', 'TOURISTIQUE']}.get(c, ['SITE'])
        it = texte_bloc(txt, 1.0, 0.6, 'blanc')
        if c in ('H21', 'H22', 'H23', 'H32', 'H33'): it = [T(txt[0], -0.08, 0.1, 0.09, 'blanc', 0.7)] + ([T(txt[1], -0.08, -0.05, 0.09, 'blanc', 0.7)] if len(txt) > 1 else []) + [arrow_sym(0.3, 0.0, 0.24, {'H21': 0, 'H22': 90, 'H23': 45}.get(c, 90), 'blanc')]
        return spec_panel(c, 1.0, 0.6, 'marron', 'blanc', it)
    if fam in ('X', 'XA', 'XAK', 'XD', 'KX', 'KXC', 'XK', 'KS', 'SAL', 'Sal', 'XM', 'XC', 'XCE', 'XKD'):
        EX = {'X1': ['SORTIE 12', '2 km'], 'X2': ['AIRE', '5 km'], 'X1a': ['70', 'SORTIE'], 'X1b': ['SORTIE', '2 km'], 'X2a': ['AIRE', '2 km'], 'X2b': ['AIRE', '5 km'],
              'X3a': ['CONTRÔLE', 'A 500 m'], 'X3b': ['CONTRÔLE', 'VITESSE'], 'X50': ['MESSAGE'], 'XA1': ['ATTENTION'], 'XAK5': ['TRAVAUX'], 'XAK22': ['ACCIDENT'], 'XAK30': ['BOUCHON', 'RALENTIR'],
              'XAK31': ['BROUILLARD'], 'XAK32': ['BROUILLARD', 'FUMÉES'], 'XD41': ['ITINÉRAIRE', 'BIS'], 'KX2': ['MESSAGE'], 'KX50': ['TEXTE'], 'KXC50': ['MESSAGE', 'LIBRE'], 'XK30': ['BOUCHON'], 'Sal2': ['SALON'], 'Sal4': ['SALON']}
        txt = EX.get(c) or lignes(court(lib) or c, 3, 14)
        if c == 'KS1': txt = ['Dév.']
        return spec_panel(c, 0.9, 0.6, 'noir', 'gris', texte_bloc(txt, 0.9, 0.6, 'ambre' if c != 'KS1' else 'jaune'), 0.04, 0.015)
    if fam == 'KC':
        return spec_panel(c, 0.9, 0.6, 'jaune', 'noir', texte_bloc(lignes(lib or c, 3, 14), 0.9, 0.6, 'noir'))
    return spec_panel(c, 0.5, 0.5, 'blanc', 'noir', texte_bloc(lignes(lib or c, 3, 12), 0.5, 0.5, 'noir'))

if __name__ == '__main__':
    mat = {s['code']: s for s in json.load(open('/home/onyxia/work/_iisr_extract/matrice_v3_normalisee.json'))['signaux']}
    rg = list(csv.DictReader(open('/tmp/chk/docs/registre_catalogue_3d.csv')))
    out = []
    for r in rg:
        if r['lot'].startswith('L6') and r['objet3d_statut'].startswith('silhouette'):
            s = build(r['code'], (mat[r['code']].get('libelle') or ''), r['famille']); s['famille'] = r['famille']; out.append(s)
    json.dump(out, open('/tmp/gab/specs_pic.json', 'w'), ensure_ascii=False)
    print(len(out))
