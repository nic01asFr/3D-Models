p='/tmp/chk/scripts/gen_gabarit.py'
s=open(p).read()
def rep(a,b):
    global s
    assert a in s, a[:60]
    s=s.replace(a,b,1)
i=s.index('def tpl_croix'); j=s.index('def tpl_balisePN')
s=s[:i]+'''def tpl_croix(b, W, H, S):
    """Croix de Saint-Andre G1 : n croix superposees (voies multiples), bis = 2 feux rouges au-dessus."""
    n = S.get('n', 1); L = S.get('L', 1.2) * (0.78 if n > 1 else 1.0); w = L * 0.17
    ys = [(-1 + 2 * i / (n - 1)) * L * 0.52 for i in range(n)] if n > 1 else [0.0]
    top = max(ys) + L * 0.36; bot = min(ys) - L * 0.36
    if S.get('bis'): top = max(ys) + L * 0.36 + 0.3
    cy0 = -(top + bot) / 2
    for y in ys:
        for col, wd in (('rouge', w), ('blanc', w * 0.7)):
            for ang in (45, -45):
                a = math.radians(ang); c, sn = math.cos(a), math.sin(a)
                pts = [(-L / 2, -wd / 2), (L / 2, -wd / 2), (L / 2, wd / 2), (-L / 2, wd / 2)]
                b.poly([[(x * c - yy * sn, x * sn + yy * c) for x, yy in pts]], mat(col), 'bras', dx=0, dy=y + cy0)
    if S.get('bis'):
        yf = max(ys) + L * 0.36 + 0.17 + cy0
        b.poly([rrect(0.5, 0.26, 0.04)], mat('noir'), 'boitier', dy=yf)
        for x in (-0.12, 0.12): b.poly([[(x + 0.085 * math.cos(2 * math.pi * k / 20), yf + 0.085 * math.sin(2 * math.pi * k / 20)) for k in range(20)]], mat('rouge'), 'feu')


'''+s[j:]
rep("ls = S['lines'][:2]; n = len(ls)\n    for i, l in enumerate(ls):\n        y = H / 2 - H * (i + 1) / (n + 1)\n        b.text(l, 0, y, min(0.05, H * 0.28), mat(S['fg']), False, maxw=W * 0.88)",
    "ls = S['lines'][:3]; n = len(ls)\n    for i, l in enumerate(ls):\n        y = H / 2 - H * (i + 1) / (n + 1)\n        b.text(l, 0, y, min(0.05, H * 0.8 / max(n, 1) / 1.6), mat(S['fg']), False, maxw=W * 0.88)")
i=s.index('def tpl_deviation'); j=s.index('def tpl_plaque')
s=s[:i]+'''def tpl_deviation(b, W, H, S):
    bg = S.get('bg', 'jaune'); fgc = S.get('fgc', 'noir')
    frame(b, W, H, bg, 'noir', border=0.02, r=0.04)
    rows = S['lines'][:3]; n = len(rows); rh = (H - 0.1) / n
    for i, l in enumerate(rows):
        y = H / 2 - 0.05 - rh * (i + 0.5)
        tx = -W / 2 + 0.15
        if i == 0 and S.get('arrow') is not None:
            b.poly([arrow_pts(min(rh * 0.8, 0.45), S['arrow'])], mat(fgc), 'fl', dx=W / 2 - 0.05 - min(rh * 0.8, 0.45) / 2, dy=y)
        if i == 0 and S.get('sil'):   # silhouette de categorie de vehicule (camion) : HYPOTHESE de dessin
            u = rh * 0.5
            b.poly([rect_pts(-W / 2 + 0.15 + u * 0.6, y, u * 1.2, u * 0.7)], mat(fgc), 'caisse')
            b.poly([[(-W / 2 + 0.15 + u * 1.25, y - u * 0.35), (-W / 2 + 0.15 + u * 1.75, y - u * 0.35), (-W / 2 + 0.15 + u * 1.75, y + u * 0.1), (-W / 2 + 0.15 + u * 1.5, y + u * 0.35), (-W / 2 + 0.15 + u * 1.25, y + u * 0.35)]], mat(fgc), 'cabine')
            for wx in (0.35, 1.5): b.poly([[(-W / 2 + 0.15 + u * wx + u * 0.12 * math.cos(2 * math.pi * k / 16), y - u * 0.38 + u * 0.12 * math.sin(2 * math.pi * k / 16)) for k in range(16)]], mat(bg if False else 'noir'), 'roue')
            tx += u * 2.0
        if l: b.text(l, tx, y, min(0.1, rh * 0.45), mat(fgc), False, align='LEFT', maxw=W - 0.6 - (tx + W / 2 - 0.15))


'''+s[j:]
rep("def rect_pts","def rect_pts") if 'def rect_pts' in s else None
open(p,'w').write(s)
print('ok','rect_pts' in s)
