#!/usr/bin/env python3
"""Génère docs/referentiel.json : référentiel unifié des 955 entrées IISR pour l'outil de validation Panoramax.

Un enregistrement par code : libellé, famille, forme et couleurs (IISR), vignette, GLB, variantes, valeurs
paramétrables, supports, statut de l'objet 3D, dimensions du modèle, références d'articles, moteur de rendu.

Usage : python3 scripts/referentiel.py [matrice_v3_normalisee.json]
Entrées : docs/registre_catalogue_3d.csv, catalogue.csv, manifeste.json, matrice IISR normalisée (hors dépôt).
"""
import csv, json, os, sys, re, datetime

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATRICE = sys.argv[1] if len(sys.argv) > 1 else '/home/onyxia/work/_iisr_extract/matrice_v3_normalisee.json'


def lire_csv(p):
    return list(csv.DictReader(open(os.path.join(RACINE, p), encoding='utf-8')))


reg = lire_csv('docs/registre_catalogue_3d.csv')
cat = {r['code']: r for r in lire_csv('catalogue.csv')}
man = {x['code']: x for x in json.load(open(os.path.join(RACINE, 'manifeste.json'), encoding='utf-8'))}
mat = {x['code']: x for x in json.load(open(MATRICE, encoding='utf-8'))['signaux']}


def nature_objet(statut):
    s = statut or ''
    if s.startswith('produit (pictogramme officiel)'): return 'officiel'
    if 'hypothèse de dessin' in s: return 'dessin_hypothese'
    if s.startswith('composé par règles'): return 'compose_regles'
    if s.startswith('gabarit'): return 'gabarit'
    if s.startswith('produit (variantes par valeur)'): return 'variantes_valeur'
    if s.startswith('modèle schématique'): return 'schematique'
    if s.startswith('version dynamique'): return 'dynamique'
    if s.startswith('représentation'): return 'representation'
    if s.startswith('fiche'): return 'fiche_sans_objet'
    return 'autre'


def valeurs_possibles(code, params):
    """Valeurs numériques citées par l'IISR pour les panneaux à valeur (ex. 30, 50, 70 pour B14)."""
    m = re.search(r':\s*([\d, ]+)\s+selon', params or '')
    return [int(x) for x in re.findall(r'\d+', m.group(1))] if m else []


out = []
for r in reg:
    c = r['code']; x = mat.get(c, {}); mn = man.get(c, {}); ct = cat.get(c, {})
    glb = r['glb'] or None
    vglb = [v for v in (r['variantes_glb'] or '').split(';') if v]
    nat = nature_objet(r['objet3d_statut'])
    e = {
        'code': c, 'libelle': x.get('libelle') or None, 'type': r['type'], 'famille': r['famille'], 'niveau': r['niveau'],
        'statut_iisr': r['statut_iisr'],
        'forme': x.get('forme'), 'couleurs': x.get('couleurs'),
        'variantes': x.get('variantes') or [],
        'parametres': {'type': r['params_type'], 'description': [p.strip() for p in (r['params'] or '').split('|') if p.strip()],
                       'valeurs_variantes_glb': sorted({int(re.search(r'-(\d+)\.glb$', v).group(1)) for v in vglb if re.search(r'-(\d+)\.glb$', v)})},
        'supports': [s.strip() for s in (r['supports'] or '').split(';') if s.strip()],
        'vignette': r['vignette'] if r['vignette'] and r['vignette'] != 'a_dessiner' else None,
        'glb': glb, 'glb_variantes': vglb,
        'objet3d': {'nature': nat, 'statut': r['objet3d_statut'], 'lot': r['lot'],
                    'fidele_au_dessin_officiel': nat == 'officiel',
                    'dimensions_m': mn.get('dims_m'), 'statut_dimension': mn.get('statut_dimension'), 'licence': mn.get('licence')},
        'sources_iisr': sorted({(str(s.get('partie', '')), str(s.get('article', ''))) for s in x.get('sources', [])}),
        'moteur_rendu': 'web/signrender.js' if nat == 'compose_regles' else None,
    }
    if c == 'B14': e['moteur_rendu'] = 'web/signrender.js#renderDisqueValeur'
    elif c in ('D42', 'D42a', 'D42b', 'Dv42a', 'Dv42b', 'D52', 'D52b', 'D52c'): e['moteur_rendu'] = 'web/signrender.js#renderSchema'
    elif re.match(r'^M9[a-z]?$', c): e['moteur_rendu'] = 'web/signrender.js#renderPanonceauTexte'
    e['sources_iisr'] = [{'partie': p, 'article': a} for p, a in e['sources_iisr']]
    out.append(e)

# libellé dérivé : jamais inventé ; repris du code parent (variante lettrée ou version dynamique X...) et marqué comme tel
LIB = {e['code']: e['libelle'] for e in out if e['libelle']}


def parent_de(code):
    b = code
    while b and b[-1].islower():
        b = b[:-1]
        if b in LIB: return b, 'variante', code[len(b):]
    m = re.match(r'^(X[A-Z]*?)([A-Z]{1,3}\d.*)$', code)
    if m:
        for t in (m.group(2), re.sub(r'[a-z]+$', '', m.group(2))):
            if t in LIB: return t, 'dynamique', m.group(1)
    return None, None, None


for e in out:
    e['libelle_origine'] = 'matrice' if e['libelle'] else None
    e['parent'] = None
    if not e['libelle']:
        par, kind, suf = parent_de(e['code'])
        if par:
            e['parent'] = par
            e['libelle'] = LIB[par] + (' (variante ' + suf + ')' if kind == 'variante' else ' (version dynamique ' + suf + ')')
            e['libelle_origine'] = 'derive_du_parent'

doc = {
    'version': 1, 'genere_le': datetime.date.today().isoformat(), 'nb_entrees': len(out),
    'avertissements': [
        'Les dessins marqués dessin_hypothese sont des reconstructions paramétriques, pas des vecteurs IISR : à utiliser comme repère de catégorie, pas comme référence graphique.',
        'Les dimensions du modèle sont provisoires hors Hb/Hc (règles IISR) ; NF P98-532 et Sétra non consultés.',
        'Chemins relatifs à la racine du dépôt nic01asFr/3D-Models.'],
    'signes': out,
}
dest = os.path.join(RACINE, 'docs', 'referentiel.json')
json.dump(doc, open(dest, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
import collections
print(len(out), 'entrées ->', dest, os.path.getsize(dest), 'octets')
print('libellés :', dict(collections.Counter(e['libelle_origine'] for e in out)))
print('nature objet 3D :', dict(collections.Counter(e['objet3d']['nature'] for e in out)))
print('sans libellé :', sum(not e['libelle'] for e in out), '| sans vignette :', sum(not e['vignette'] for e in out), '| sans glb :', sum(not e['glb'] for e in out))
