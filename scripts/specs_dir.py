import json
from dir_regles import composer, geometrie, hc
S = json.load(open('/tmp/gab/specs.json'))
def M(t, pole='agglo', d=None, local=False): return {'texte': t, 'pole': pole, 'distance_km': d, 'local': local}
VERT_AUTO = {'reseau': 'autoroutier', 'vitesse': 110, 'support': 'portique'}
CTX = {'D2': {'reseau': 'autre', 'vitesse': 50, 'eloignement_m': 10}, 'D3': VERT_AUTO, 'D4': VERT_AUTO, 'D5': VERT_AUTO, 'D6': VERT_AUTO}
def contenu(code, old):
    """Contenu d'exemple (ex. fictif) et contexte par type ; toutes les règles viennent de composer()."""
    ctx = dict(CTX.get(code[:2], {'reseau': 'autre', 'vitesse': 50}))
    if code.startswith('Da'):
        aire = code[:4] in ('Da32','Da51') or code in ('Da52a','Da52b') 
        fond = 'bleu' if aire else 'vert'
        ms = [M('Aire de la Crau', 'autre', 2)] if aire else [M('Toulon', 'agglo', 65)]
        return code, VERT_AUTO, [{'fond': fond, 'fleche': None, 'mentions': ms, 'voies': 2, 'sortie': True}]
    if code.startswith('Dp'):  # piéton / local : autres voiries 50 km/h
        if code[:3] in ('Dp1', 'Dp2'):   # Dp1a/b postes d'appel d'urgence, Dp2a/b issues de secours (a/b = sens : HYPOTHESE)
            lib = "Poste d'appel d'urgence" if code[:3] == 'Dp1' else 'Issue de secours'
            return 'D21a', ctx, [{'fond': 'blanc', 'fleche': 'g' if code.endswith('a') else 'd', 'mentions': [M(lib, 'autre', 0.1, True)]}]
        return 'D21a', ctx, [{'fond': 'blanc', 'fleche': 'd', 'mentions': [M('Centre-ville', 'autre', 0.3, True)]}]
    if code.startswith('Dv'):
        cx = {'reseau': 'autre', 'vitesse': 50, 'eloignement_m': 10}
        if code in ('Dv21b', 'Dv43b'):   # sans indication de distance
            return code, cx, [{'fond': 'vert', 'fleche': 'd', 'mentions': [M('Marseille', 'agglo')]}]
        if code in ('Dv21c', 'Dv43c'):   # continuites evidentes d'itineraires
            return code, cx, [{'fond': 'vert', 'fleche': 'h', 'mentions': [M('Marseille', 'agglo')]}]
        if code == 'Dv43d':
            return code, cx, [{'fond': 'vert', 'fleche': 'h', 'mentions': [M('Marseille', 'agglo'), M('Aix-en-Provence', 'agglo')]}]
        return code, cx, [{'fond': 'vert', 'fleche': 'd', 'mentions': [M('Marseille', 'agglo', 12)]}]
    if code.startswith('Dc'):
        return code, {'reseau': 'autre', 'vitesse': 50, 'eloignement_m': 10}, [{'fond': 'bleu', 'fleche': 'd', 'mentions': [M("Zone d'activités", 'autre', 0.4, True)]}]
    if code in ('D44','D45','D46','D46b','D47a','D47b','D48','D48a','D48b','D48c'):
        return code, {'reseau': 'autoroutier', 'vitesse': 110, 'support': 'portique'}, [{'fond': 'bleu', 'fleche': 'd', 'mentions': [M('Aire de la Crau', 'autre', 2)]}]
    if code in ('D42','D43','D42a','D42b','D40','D41','D41a','D41b','D41c'):
        return code, ctx if code[1]!='4' else VERT_AUTO, [{'fond': 'vert', 'fleche': 'h', 'mentions': [M('Toulon', 'agglo', 65), M('Aix-en-Provence', 'agglo', 35), M('Marseille', 'agglo', 28)]}]
    if code[:3] in ('D30','D31','D32') or code.startswith('D5'):
        return code, VERT_AUTO, [{'fond': 'vert', 'fleche': 'hd', 'mentions': [M('Toulon', 'agglo', 65), M('Marseille', 'agglo', 28)]},
                                  {'fond': 'blanc', 'fleche': None, 'mentions': [M('Sortie 12', 'autre', None)]}]
    if code.startswith('D6'):
        return code, VERT_AUTO, [{'fond': 'vert', 'fleche': None, 'mentions': [M('Marseille', 'agglo', 12)]}]
    if code in ('D21b','D29b'):
        return 'D21b', ctx, [{'fond': 'vert', 'fleche': 'g', 'mentions': [M('Marseille', 'agglo')]}]
    # D20, D21, D21a, D29, D29a
    return 'D21a', ctx, [{'fond': 'vert', 'fleche': 'g', 'mentions': [M('Marseille', 'agglo', 28), M('Aubagne', 'agglo', 12)]},
                          {'fond': 'blanc', 'fleche': 'g', 'mentions': [M('Gémenos', 'autre', 4.3)]}]
def cartouche(c):
    if c[:3] == 'D21': return 'E42, E43, E44 ou E47 (+ E41 éventuel) au-dessus de l’ensemble'
    if c[:3] in ('D61', 'D62') or c in ('Da31b','Da31c','Da31e','Da31f','Da41b','Da41c','Da41e','Da41f'): return 'E42, E43, E44, E46 ou E47 obligatoire (+ E41 éventuel)'
    if c in ('Da31a','Da31d'): return 'E42, E43, E44, E46 ou E47 facultatif (+ E41 éventuel)'
    if c == 'D31d': return 'E42, E43, E44, E46 ou E47 possible (+ E41)'
    if c[:3] in ('D31','D41','Da4','D40'): return 'E41 éventuel'
    return ''
def build(codes):
    out = []; ko = []
    for s in S:
        c = s['code']
        if c not in codes: continue
        typ, ctx, regs = contenu(c, s)
        try:
            comp = composer({'type': typ, 'contexte': ctx, 'registres': regs})
        except ValueError as e:
            ko.append((c, str(e))); continue
        g = geometrie(comp)
        meta = {'hb_mm': comp['hb_mm'], 'hc_mm': ';'.join(str(r['hc_mm']) for r in comp['registres']),
                'hauteur_caractere_mm': ';'.join(str(r['hc_mm']) for r in comp['registres']),
                'contexte': json.dumps(ctx, ensure_ascii=False),
                'regles_appliquees': 'IISR 5e partie art.81 C, 81-1 (casse, distances, ordre des blocs, limites de mentions), art.83 (Hb/Hc, alignement)',
                'dimension_source': 'Hb/Hc: IISR art.83 ; autres dimensions: hypothese (NF P98-532 / Setra non consultes)',
                'statut_dimension': 'provisoire', 'cartouche_requis': cartouche(c)}
        out.append({'code': c, 'tpl': 'dircomp', 'w': round(g['largeur'], 3), 'h': round(g['hauteur'], 3), 'bg': regs[0]['fond'], 'fg': 'blanc',
                    'famille': s['famille'], 'geo': g, 'dos': False, 'meta': meta})
    return out, ko
if __name__ == '__main__':
    import sys
    codes = sys.argv[1].split(',') if len(sys.argv) > 1 else [s['code'] for s in S if s['code'][0] == 'D' and s['tpl'] in ('position','dirfleche','presign','affectation') and not s['code'].startswith('KD') and not s['code'].startswith(('D7','D69','Dv44','D70'))]
    out, ko = build(set(codes)); json.dump(out, open('/tmp/gab/specs_dir.json', 'w'), ensure_ascii=False)
    print(len(out), 'specs ; refusés:', ko)

# ---- schémas D42a / D42b / D52 (Hc par construction, libellés en capitales d'agglomération)
def build_schemas():
    from dir_regles import hb, hc, casse
    spec = {'D42': ('carrefour', 'autre', 90, 'sol', {'haut': 'Aix-en-Provence', 'gauche': 'Marseille', 'droite': 'Toulon'}, '150 m'),
            'D42a': ('carrefour', 'autre', 90, 'sol', {'haut': 'Aix-en-Provence', 'gauche': 'Marseille', 'droite': 'Toulon'}, '150 m'),
            'D42b': ('giratoire', 'autre', 90, 'sol', {'haut': 'Aix-en-Provence', 'gauche': 'Marseille', 'droite': 'Toulon'}, '150 m'),
            'Dv42a': ('carrefour', 'autre', 50, 'sol', {'haut': 'Aix-en-Provence', 'gauche': 'Marseille', 'droite': 'Toulon'}, None),
            'Dv42b': ('giratoire', 'autre', 50, 'sol', {'haut': 'Aix-en-Provence', 'gauche': 'Marseille', 'droite': 'Toulon'}, None),
            'D52': ('echangeur', 'autoroutier', 90, 'portique', {'haut': 'Marseille', 'droite': 'Toulon'}, None),
            'D52b': ('echangeur', 'autoroutier', 90, 'portique', {'haut': 'Marseille', 'droite': 'Toulon'}, None),
            'D52c': ('echangeur', 'autoroutier', 90, 'portique', {'haut': 'Marseille', 'droite': 'Toulon'}, None)}
    out = []
    for s in S:
        c = s['code']
        if c not in spec: continue
        kind, res, v, sup, labs, enc = spec[c]
        h0 = hb(res, v, sup, c); u = hc(h0, 'blanc') / 1000.0
        Wp, Hp = 26 * u, 19 * u
        labs = {k: casse(t, 'agglo') for k, t in labs.items()}
        out.append({'code': c, 'tpl': 'dirschema', 'w': round(Wp, 3), 'h': round(Hp, 3), 'bg': 'blanc', 'fg': 'noir', 'famille': s['famille'],
                    'sch': {'kind': kind, 'u': u, 'labels': labs, 'encart': enc}, 'dos': True,
                    'meta': {'hb_mm': h0, 'hc_mm': int(u * 1000), 'hauteur_caractere_mm': int(u * 1000),
                             'contexte': '%s %s km/h %s' % (res, v, sup),
                             'regles_appliquees': 'IISR art.83 (Hb/Hc), art.81-1 (casse) ; encart 150 m : art.83-4 / 42-6 (D42) ; schéma = hypothèse de dessin',
                             'dimension_source': 'Hb/Hc: IISR art.83 ; schéma et dimensions: hypothèse (NF P98-532 / Setra non consultés)', 'statut_dimension': 'provisoire'}})
    return out
