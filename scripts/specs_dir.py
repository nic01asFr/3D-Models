import json
from dir_regles import composer, geometrie, hc
S = json.load(open('/tmp/gab/specs.json'))
def M(t, pole='agglo', d=None, local=False): return {'texte': t, 'pole': pole, 'distance_km': d, 'local': local}
VERT_AUTO = {'reseau': 'autoroutier', 'vitesse': 110, 'support': 'portique'}
CTX = {'D2': {'reseau': 'autre', 'vitesse': 50, 'eloignement_m': 10}, 'D3': VERT_AUTO, 'D4': VERT_AUTO, 'D5': VERT_AUTO, 'D6': VERT_AUTO}
def contenu(code, old):
    """Contenu d'exemple (ex. fictif) et contexte par type ; toutes les règles viennent de composer()."""
    ctx = dict(CTX.get(code[:2], {'reseau': 'autre', 'vitesse': 50}))
    if code.startswith('Dp'):  # piéton / local : autres voiries 50 km/h
        return 'D21a', ctx, [{'fond': 'blanc', 'fleche': 'd', 'mentions': [M('Centre-ville', 'autre', 0.3, True)]}]
    if code.startswith('Dv'):
        return code, {'reseau': 'autre', 'vitesse': 50, 'eloignement_m': 10}, [{'fond': 'vert', 'fleche': 'd', 'mentions': [M('Marseille', 'agglo', 12)]}]
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
                'statut_dimension': 'provisoire'}
        out.append({'code': c, 'tpl': 'dircomp', 'w': round(g['largeur'], 3), 'h': round(g['hauteur'], 3), 'bg': regs[0]['fond'], 'fg': 'blanc',
                    'famille': s['famille'], 'geo': g, 'dos': False, 'meta': meta})
    return out, ko
if __name__ == '__main__':
    import sys
    codes = sys.argv[1].split(',') if len(sys.argv) > 1 else [s['code'] for s in S if s['code'][0] == 'D' and s['tpl'] in ('position','dirfleche','presign') and not s['code'].startswith(('D7','D69','Dv44','D70'))]
    out, ko = build(set(codes)); json.dump(out, open('/tmp/gab/specs_dir.json', 'w'), ensure_ascii=False)
    print(len(out), 'specs ; refusés:', ko)
