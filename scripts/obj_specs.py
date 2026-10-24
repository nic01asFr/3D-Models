import csv, json, re
rg = list(csv.DictReader(open('/tmp/chk/docs/registre_catalogue_3d.csv')))
m = json.load(open('/home/onyxia/work/_iisr_extract/matrice_v3_normalisee.json'))
lib = {x['code']: (x.get('libelle') or '') for x in m['signaux']}


def D(code, W, H, items, kind, **k):
    d = dict(code=code, tpl='dessin', w=W, h=H, items=items, dos=False, meta={'type_objet': kind, 'aspect': 'modele schematique (a valider)'}); d.update(k); return d


# ------------------------------------------------------------- feux
T3 = [('rouge', None), ('jaune', None), ('vert', None)]


def feu(code, lamps, d=0.2, horiz=False):
    n = len(lamps); pad = d * 0.3
    if horiz: W, H = n * (d + pad) + pad, d + 2 * pad
    else: W, H = d + 2 * pad, n * (d + pad) + pad
    it = [('rect', 0, 0, W, H, 'noir', 0.1, 0.03)]
    for i, (c, s) in enumerate(lamps):
        x = -W / 2 + pad + d / 2 + i * (d + pad) if horiz else 0
        y = 0 if horiz else H / 2 - pad - d / 2 - i * (d + pad)
        it.append(('disc', x, y, d / 2, c, 0.01))
        if s: it.append(('sym', s, x, y, d, 'noir'))
    return D(code, round(W, 3), round(H, 3), it, 'feu')


def feu_spec(code):
    c = code.lower(); suf = lambda p: c[len(p):]
    if c == 'r25': return feu(code, [('rouge', 'pieton')])
    if c.startswith('r12'): return feu(code, [('rouge', 'velo' if c == 'r12m' else 'pieton'), ('vert', 'velo' if c == 'r12m' else 'pieton')])
    for pre, d in (('r13', 0.2), ('r15', 0.1)):
        if c.startswith(pre):
            s = suf(pre); sym = 'velo' if s.startswith('c') else 'bus' if s.startswith('b') else 'tram'
            return feu(code, [('jaune', sym)] if s.endswith('j') else [('rouge', sym), ('jaune', sym), ('vert', sym)], d)
    for pre, d in (('r14', 0.2), ('r16', 0.1)):
        if c.startswith(pre):
            s = suf(pre); sym = {'tg': 'fleche_g', 'td': 'fleche_d', 'd': 'fleche_h', 'dtg': 'fleche_hg', 'dtd': 'fleche_hd'}.get(s, 'fleche_h')
            return feu(code, [('rouge', sym), ('jaune', sym), ('vert', sym)], d)
    if c == 'r18td': return feu(code, [('blanc', 'barre_d')])
    if c.startswith('r17') or c.startswith('r18'): return feu(code, [('blanc', 'barre_g')])
    if c == 'r19': return feu(code, [('jaune', 'fleche_d')])
    if c == 'r21a': return feu(code, [('rouge', 'croix')])
    if c == 'r21b': return feu(code, [('vert', 'fleche_b')])
    if c in ('r21c',): return feu(code, [('jaune', 'fleche_b')])
    if c == 'r21cd': return feu(code, [('jaune', 'fleche_d')])
    if c == 'r21cg': return feu(code, [('jaune', 'fleche_g')])
    if c in ('r22j',): return feu(code, [('jaune', None)])
    if c in ('r22v', 'r23v'): return feu(code, [('vert', None)])
    if c == 'r23j': return feu(code, [('jaune', None)])
    if re.match(r'^(r1|r1j|r1n|r1jn|r2|r2d|r24|kr1|kr2|kr2d|r21)$', c): return feu(code, [('rouge', None), ('rouge', None)], 0.2, True)
    if c == 'kr41': return feu(code, [('ambre', None)] * 6, 0.12, True)
    if c in ('kr42', 'kr43', 'kr44'):
        sym = {'kr42': 'fleche_d', 'kr43': 'fleche_hd', 'kr44': 'fleche_d'}[c]
        it = [('rect', 0, 0, 1.2, 0.6, 'noir', 0.1, 0.03), ('sym', sym, 0, 0, 0.55, 'ambre')]
        if c == 'kr44': it.append(('sym', sym, 0.35, 0, 0.55, 'ambre'))
        return D(code, 1.2, 0.6, it, 'dispositif')
    return feu(code, T3)


# ------------------------------------------------------------- balises / dispositifs
def chev(cy, col='blanc'):
    return ('poly', [(-0.14, cy - 0.08), (0, cy + 0.04), (0.14, cy - 0.08), (0.14, cy - 0.16), (0, cy - 0.04), (-0.14, cy - 0.16)], col, 0.004)


def poteau(h=1.0, w=0.15, extra=None, bande=None):
    it = [('rect', 0, 0, w, h, 'blanc', w)]
    if bande: it.append(('rect', 0, h / 2 - 0.15, w * 1.02, 0.2, bande, 0.005))
    return it + (extra or [])


def balise_spec(code):
    c = code.lower()
    P = lambda W, H, it, kind='balise': D(code, W, H, it, kind)
    if c in ('j1', 'j1bis'): return P(0.15, 1.0, poteau(bande='noir', extra=[('rect', 0, -0.25, 0.08, 0.06, 'rouge', 0.006)]))
    if c == 'j3': return P(0.15, 1.0, poteau(bande='rouge', extra=[('rect', 0, -0.25, 0.08, 0.06, 'blanc', 0.006)]))
    if c == 'j6': return P(0.15, 1.0, poteau(bande='noir', extra=[('rect', 0, -0.2, 0.08, 0.06, 'blanc', 0.006), ('rect', 0, -0.35, 0.08, 0.06, 'blanc', 0.006)]))
    if c in ('j4', 'j12', 'j14b', 'j11'): return P(0.4, 0.8, [('rect', 0, 0.2, 0.4, 0.6, 'noir', 0.03), chev(0.35), chev(0.2), chev(0.05), ('rect', 0, -0.3, 0.06, 0.4, 'blanc', 0.06)])
    if c == 'j14a': return P(0.4, 0.8, [('rect', 0, 0.2, 0.4, 0.6, 'noir', 0.03), chev(0.2), ('rect', 0, -0.3, 0.06, 0.4, 'blanc', 0.06)])
    if c in ('j10', 'j13'): return P(0.4, 1.0, [('bands', 0, 0.2, 0.4, 0.6, 6, 'rouge', 'blanc', 0.03), ('rect', 0, -0.3, 0.06, 0.4, 'blanc', 0.06)])
    if c == 'j7': return P(0.7, 2.0, [('rect', -0.25, 0, 0.05, 2.0, 'gris', 0.05), ('solid', 0.0, 0.7, 0.12, 0.04, 0.45, 'orange'), ('solid', 0.0, 0.7, 0.123, 0.123, 0.08, 'blanc'), ('solid', 0.0, 0.9, 0.095, 0.095, 0.08, 'blanc')])
    if c in ('j15a', 'j15b'): return P(0.2, 0.1, [('solid', 0, -0.04, 0.09, 0.07, 0.07, 'blanc'), ('disc', 0, -0.0, 0.025, 'rouge', 0.006)])
    if c == 'j16': return P(0.05, 0.6, [('rect', 0, 0, 0.05, 0.6, 'blanc', 0.05), ('rect', 0, 0.2, 0.052, 0.08, 'noir', 0.005)])
    if c == 'j17': return P(0.2, 0.1, [('solid', 0, -0.04, 0.09, 0.07, 0.07, 'gris'), ('disc', 0, 0.0, 0.03, 'ambre', 0.008)])
    if c == 'k1': return P(0.5, 1.2, [('rect', -0.2, 0, 0.02, 1.2, 'noir', 0.02), ('poly', [(-0.19, 0.55), (0.25, 0.4), (-0.19, 0.25)], 'rouge', 0.004)])
    if c == 'k2': return P(1.2, 1.0, [('bands', 0, 0.2, 1.2, 0.25, 6, 'rouge', 'blanc', 0.03), ('rect', -0.5, -0.25, 0.05, 0.6, 'gris', 0.05), ('rect', 0.5, -0.25, 0.05, 0.6, 'gris', 0.05)], 'dispositif')
    if c == 'k5a': return P(0.4, 0.75, [('solid', 0, -0.37, 0.19, 0.04, 0.75, 'orange'), ('solid', 0, 0.0, 0.114, 0.095, 0.14, 'blanc')], 'dispositif')
    if c in ('k5', 'k5b', 'k10'): return P(0.06, 1.0, [('bands', 0, 0, 0.06, 1.0, 6, 'rouge', 'blanc', 0.06)], 'dispositif')
    if c in ('k5c', 'k5d'): return P(0.4, 1.0, [('rect', 0, -0.2, 0.06, 0.6, 'blanc', 0.06), ('rect', 0, 0.3, 0.4, 0.4, 'noir', 0.03), chev(0.35), chev(0.2)], 'dispositif')
    if c == 'k8': return P(0.8, 0.6, [('rect', 0, 0, 0.8, 0.6, 'jaune', 0.02, 0.03), ('sym', 'fleche_d', 0, 0, 0.55, 'noir')], 'dispositif')
    if c == 'k14': return P(1.0, 0.08, [('bands', 0, 0, 1.0, 0.08, 10, 'rouge', 'blanc', 0.003)], 'dispositif')
    if c == 'k15': return P(3.0, 1.6, [('rect', -1.4, 0, 0.1, 1.6, 'gris', 0.1), ('rect', 1.4, 0, 0.1, 1.6, 'gris', 0.1), ('rect', 0, 0.55, 3.0, 0.5, 'jaune', 0.05), ('text', 'K15', 0, 0.55, 0.2, 'noir')], 'dispositif')
    if c == 'k16': return P(0.8, 0.6, [('bands', 0, 0, 0.8, 0.6, 4, 'rouge', 'blanc', 0.4)], 'dispositif')
    if c == 'xk3': return P(2.5, 0.5, [('rect', -1.2, -0.05, 0.1, 0.4, 'gris', 0.1), ('bands', 0.05, 0.1, 2.4, 0.1, 12, 'rouge', 'blanc', 0.03)], 'dispositif')
    if c in ('xk4', 'xk4a', 'xk4b'):
        L = {'xk4': 2.0, 'xk4a': 3.0, 'xk4b': 1.5}[c]
        return P(L, 0.4, [('bands', 0, 0, L, 0.4, 8, 'rouge', 'blanc', 0.4)], 'dispositif')
    if c == 't3': return P(1.0, 0.3, [('rect', 0, 0, 1.0, 0.3, 'gris', 0.002)] + [('rect', -0.33 + 0.33 * i, 0, 0.2, 0.05, 'blanc', 0.001) for i in range(3)], 'marquage')
    return None


# ------------------------------------------------------------- formes-types
def forme(code, fam, L):
    c = code
    def F(**k):
        d = dict(code=code, tpl='forme', lines=[code], dos=False, meta={'type_objet': 'forme-type', 'aspect': 'silhouette : forme et couleur du type, pictogramme a dessiner'}); d.update(k); return d
    if fam == 'A': return F(forme='triangle', w=1.0, h=0.866)
    if c == 'B30': return F(forme='disque_rouge', w=0.65, h=0.65, valeur='30', haut='ZONE')
    if c == 'B51': return F(forme='disque_rouge', w=0.65, h=0.65, valeur='30', haut='ZONE', barre=True)
    if c == 'B25': return F(forme='disque_bleu', w=0.65, h=0.65, valeur='30', haut='MINI')
    if c == 'B43': return F(forme='disque_bleu', w=0.65, h=0.65, valeur='30', barre=True)
    if c == 'B45': return F(forme='disque_bleu', w=0.65, h=0.65, barre=True)
    if c == 'B2': return F(forme='disque_rouge', w=0.65, h=0.65)
    if fam == 'B': return F(forme='disque_bleu', w=0.65, h=0.65)
    if c in ('C4a', 'C4b'): return F(forme='rect', w=0.65, h=0.65, bg='bleu', fg='blanc', lines=['50'], barre=(c == 'C4b'))
    if fam in ('C', 'CE'): return F(forme='rect', w=0.65, h=0.65, bg='bleu', fg='blanc')
    if fam == 'H': return F(forme='rect', w=1.0, h=0.6, bg='marron', fg='blanc')
    if fam == 'SR': return F(forme='rect', w=1.0, h=0.75, bg='bleu', fg='blanc')
    if fam in ('M', 'KM'): return F(forme='rect', w=0.5, h=0.35, bg='blanc', fg='noir')
    if fam in ('X', 'XA', 'XAK', 'XD', 'KX', 'KXC', 'XM'): return dict(code=code, tpl='dynamique', w=1.0, h=1.0, lines=[code], meta={'type_objet': 'forme-type', 'aspect': 'silhouette dynamique'})
    return F(forme='rect', w=0.5, h=0.5, bg='blanc', fg='noir')


todo = [r for r in rg if r['objet3d_statut'] in ('à dessiner (pas de source)', 'feu/balise/dispositif : modèle dédié')]
out = []; seen = set()
for r in todo:
    code, fam = r['code'], r['famille']
    if code in seen: continue
    seen.add(code)
    s = None
    if fam in ('R', 'KR'): s = feu_spec(code)
    if s is None and fam in ('J', 'K', 'XK', 'T'): s = balise_spec(code)
    if s is None: s = forme(code, fam, lib.get(code, ''))
    s['famille'] = fam; s['statut_orig'] = r['objet3d_statut']
    out.append(s)
json.dump(out, open('/tmp/gab/specs2.json', 'w'), ensure_ascii=False)
import collections
print(len(out), collections.Counter(s['meta']['type_objet'] for s in out))
