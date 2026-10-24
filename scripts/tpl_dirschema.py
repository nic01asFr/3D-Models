

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
