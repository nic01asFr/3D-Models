"""Règles de la signalisation de direction (types D et Da) appliquées PAR CONSTRUCTION.
Entrée : contenu (registres, mentions) + contexte (réseau, vitesse, support, éloignement).
Sortie : composition normalisée (casse, distances, Hb/Hc, ordre) ou ValueError si non conforme.
Sources : IISR 5e partie VC20240315, art. 81 C, 81-1, 83 (p.41-48). Sans dépendance Blender.
Les coefficients de géométrie (HYP) NE sont PAS dans l'IISR (NF P98-532 / Sétra) : hypothèses."""
import re
from composition import valider, arrondi_distance_km

GAMMES = [100, 125, 160, 200, 250, 320]  # gammes de Hb (mm) — art. 83 p.47
# Table art. 83 p.47 (lue par positions dans le PDF) ; None = non défini par l'IISR
HB = {'autoroutier': {70: 160, 90: 200, 110: 250, 130: 320},
      'autre':       {50: 100, 70: 100, 90: 125}}
CLAIR = ('blanc', 'jaune'); FONCE = ('noir', 'bleu', 'vert', 'rouge', 'marron')
# HYPOTHÈSES de géométrie (à remplacer par NF P98-532 / guides Sétra)
HYP = {'hauteur_registre_sur_hc': 2.0, 'marge_h_sur_hc': 1.0, 'fleche_largeur_sur_hc': 2.5,
       'largeur_caractere_sur_hc': 0.72, 'liseré_sur_hc': 0.12, 'interligne_sur_hc': 0.0,
       'statut': 'hypothèse – non issue de l’IISR'}

def gamme_plus(h, n=1):
    i = min(GAMMES.index(h) + n, len(GAMMES) - 1); return GAMMES[i]

def hb(reseau, vitesse, support='sol', type_panneau='', eloignement_m=0, presignal=True):
    tab = HB[reseau]
    v = next((s for s in sorted(tab) if vitesse <= s), None)
    if v is None: raise ValueError('Hb non défini par l’IISR pour %s à %s km/h' % (reseau, vitesse))
    h = tab[v]
    if support in ('portique', 'potence', 'haut-mat'): h = max(h, 250)
    if type_panneau.startswith('D2') and not type_panneau.startswith('D29'):
        if not presignal: h = gamme_plus(h, 1)
        if eloignement_m > 50: h = gamme_plus(h, 2)
        elif eloignement_m >= 15: h = gamme_plus(h, 1)
    return h

def hc(hbase, fond):
    return hbase if fond in CLAIR else gamme_plus(hbase, 1)

def casse(texte, pole):
    return texte.upper() if pole in ('agglo', 'pole_non_agglo', 'secondaire', 'rabattement') else (texte[:1].upper() + texte[1:])

def fmt_distance(d_km, local=False):
    if d_km is None: return None
    if local and d_km < 0.5: return '%d m' % (round(d_km * 1000 / 50) * 50)
    a = arrondi_distance_km(d_km)
    return ('%g' % a).replace('.', ',')

def composer(spec):
    """spec = {'type','contexte':{reseau,vitesse,support,eloignement_m,presignal},'registres':[{fond,fleche,mentions:[{texte,pole,distance_km,local}]}]}"""
    c = spec.get('contexte', {}); t = spec.get('type', 'D21a')
    typ = {'D21a': 'position', 'D21b': 'position', 'D31': 'avancee', 'D41': 'presignalisation', 'D42a': 'D42', 'D42b': 'D42',
           'D61a': 'confirmation', 'D62': 'confirmation'}.get(t[:4] if t[:3] in ('D21', 'D31', 'D41', 'D42', 'D61', 'D62') else t, spec.get('regime', 'position'))
    p = {'type': typ, 'registres': [{'couleur': r['fond'], 'mentions': [{'texte': m['texte'], 'distance_km': m.get('distance_km')} for m in r['mentions']]} for r in spec['registres']]}
    err = valider(p)
    if t == 'D21b' and any(m.get('distance_km') is not None for r in spec['registres'] for m in r['mentions']):
        err.append('D21b ne comporte pas d’indication de distance')
    if t == 'D21a' and not any(m.get('distance_km') is not None for r in spec['registres'] for m in r['mentions']):
        err.append('D21a comporte une indication de distance')
    if err: raise ValueError('; '.join(err))
    h0 = hb(c.get('reseau', 'autre'), c.get('vitesse', 50), c.get('support', 'sol'), t, c.get('eloignement_m', 0), c.get('presignal', True))
    regs = []
    for r in spec['registres']:
        H = hc(h0, r['fond'])
        ms = [{'texte': casse(m['texte'], m.get('pole', 'autre')), 'dist': fmt_distance(m.get('distance_km'), m.get('local', False))} for m in r['mentions']]
        regs.append({'fond': r['fond'], 'fleche': r.get('fleche'), 'hc_mm': H, 'mentions': ms})
    return {'type': t, 'hb_mm': h0, 'registres': regs, 'hyp': HYP}

def geometrie(comp, cap_ratio=1.0):
    """Dimensions (m) dérivées de Hc par les coefficients HYP. Largeur commune (rectangles alignés)."""
    k = HYP; W = 0; rows = []
    for r in comp['registres']:
        H = r['hc_mm'] / 1000.0; h = k['hauteur_registre_sur_hc'] * H * max(1, len(r['mentions']))
        w = 0
        for m in r['mentions']:
            n = len(m['texte']) + (len(m['dist']) + 3 if m['dist'] else 0)
            w = max(w, n * k['largeur_caractere_sur_hc'] * H)
        fl = r['fleche']
        fw = 0 if not fl else (0.8 * h if fl in ('h', 'b', 'hd', 'hg') else 0.5 * h + 0.5 * H)
        w += 2 * k['marge_h_sur_hc'] * H + max(fw, k['fleche_largeur_sur_hc'] * H if fl else 0)
        W = max(W, w); rows.append((r, h, H))
    return {'largeur': W, 'registres': [{'h': h, 'cap': H, 'registre': r} for r, h, H in rows], 'hauteur': sum(h for _, h, _ in rows)}

if __name__ == '__main__':
    s = {'type': 'D21a', 'contexte': {'reseau': 'autre', 'vitesse': 90, 'support': 'sol', 'eloignement_m': 10},
         'registres': [{'fond': 'vert', 'fleche': 'g', 'mentions': [{'texte': 'Marseille', 'pole': 'agglo', 'distance_km': 28}, {'texte': 'Aubagne', 'pole': 'agglo', 'distance_km': 12}]},
                       {'fond': 'blanc', 'fleche': 'g', 'mentions': [{'texte': 'Gémenos', 'pole': 'autre', 'distance_km': 4.3}]}]}
    c = composer(s); print(c['hb_mm'], [(r['fond'], r['hc_mm'], [(m['texte'], m['dist']) for m in r['mentions']]) for r in c['registres']])
    g = geometrie(c); print(round(g['largeur'], 2), round(g['hauteur'], 2))
    for bad in ({**s, 'registres': s['registres'][::-1]}, {**s, 'type': 'D21b'}, {**s, 'contexte': {'reseau': 'autre', 'vitesse': 130}}):
        try: composer(bad); print('ACCEPTÉ ?!')
        except ValueError as e: print('refusé:', e)
