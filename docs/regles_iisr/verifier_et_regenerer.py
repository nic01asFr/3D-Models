#!/usr/bin/env python3
"""Vérifie les règles IISR et régénère les fichiers CSV à partir de regles_iisr.json.

Source de vérité : regles_iisr.json (les règles sont des données, choisies à la lecture du texte).
Ce script ne choisit aucune règle. Il fait deux choses reproductibles :
  1. VÉRIFIE que chaque extrait figure mot pour mot (espaces et apostrophes normalisés) dans la page indiquée
     du texte extrait (partie_N.txt, marqueurs « === PAGE n === ») ; une règle ABSENT_du_texte sans extrait
     (page 0) est acceptée telle quelle.
  2. RÉGÉNÈRE regles_<lot>.csv et couverture_catalogue.csv dans un dossier de sortie séparé (jamais par-dessus).

Usage :
    python3 verifier_et_regenerer.py [--regles regles_iisr.json] [--texte ~/work/_iisr_extract]
                                     [--catalogue ~/work/catalogue-3d/catalogue.csv] [--sortie ./regenere]
Code de sortie : 0 si tous les extraits sont retrouvés, 1 sinon.

Limite : ce script ne relit pas les statuts « iisr_croise_pdf » et « iisr_lu_sur_PDF » : leur valeur vient d'une
lecture visuelle de la page du PDF (voir preuves_pdf/). Seul l'extrait de texte qui les accompagne est vérifié.
"""
import argparse
import collections
import csv
import json
import os
import re
import sys

COLONNES = ['id', 'lot', 'objet', 'parametre', 'valeur', 'condition', 'partie', 'article', 'page',
            'extrait', 'statut', 'note', 'verifie']
COLONNES_COUVERTURE = ['code', 'famille', 'dans_catalogue', 'priorite', 'regles_gamme', 'regles_combinaison',
                       'regles_texte_et_forme', 'absent_explicite', 'manquant', 'statut_catalogue']
LOTS = ('gammes', 'combinaisons', 'texte_alphabets', 'types_prioritaires', 'liseres_couleurs', 'marquages',
        'feux', 'balises', 'formes_par_code', 'feux_par_code')
# types signalés en priorité par pilote-cairn, dans cet ordre
PRIORITAIRES = ['M9v', 'M4c', 'H', 'H10', 'H20', 'A9b', 'M8', 'B45', 'M9z', 'M6a', 'M8f', 'AB3a', 'Dv61', 'M6i',
                'M4d1', 'B14-30', 'M9z-AB3a', 'C-PARK']
LOTS_GAMME = ('gammes', 'liseres_couleurs', 'feux', 'balises', 'feux_par_code')
LOTS_TEXTE = ('texte_alphabets', 'types_prioritaires')
STATUTS_NON_COMPTES = ('ABSENT_du_texte', 'iisr_renvoi', 'a_extraire')


def normaliser(texte):
    texte = texte.replace('’', "'").replace(' ', ' ').replace('‑', '-')
    return re.sub(r'\s+', ' ', texte).strip()


def charger_pages(dossier):
    pages = {}
    for n in range(1, 10):
        chemin = os.path.join(dossier, 'partie_%d.txt' % n)
        brut = open(chemin, encoding='utf-8').read()
        morceaux = re.split(r'=== PAGE (\d+) ===', brut)
        for i in range(1, len(morceaux), 2):
            pages[(n, int(morceaux[i]))] = normaliser(morceaux[i + 1])
    return pages


def verifier(regles, pages):
    ecarts = []
    for r in regles:
        if r['page'] == 0 and r['extrait'] == '':
            r['verifie'] = True
            continue
        r['verifie'] = normaliser(r['extrait']) in pages.get((r['partie'], r['page']), '')
        if not r['verifie']:
            ecarts.append((r['id'], r['partie'], r['page'], r['extrait'][:70]))
    return ecarts


def concerne(regle, code, famille):
    objet = regle['objet']
    if objet.strip().lower().startswith('tous'):
        return False
    for t in [t for t in re.split(r'[,\s/()]+', objet) if t]:
        if t.lower() == code.lower() or t.lower() == famille.lower():
            return True
        if re.fullmatch(r'M\d+[a-z]?\d?', t) and code.lower().startswith(t.lower()) \
                and not code[len(t):len(t) + 1].isdigit():
            return True
    return 'panonceaux' in objet.lower() and famille.upper() == 'M'


def ligne_couverture(regles, code, ligne_catalogue):
    famille = ligne_catalogue['famille'] if ligne_catalogue else ''

    def compte(r):
        return r['statut'] not in STATUTS_NON_COMPTES and concerne(r, code, famille)
    g = [r['id'] for r in regles if r['lot'] in LOTS_GAMME and compte(r)]
    k = [r['id'] for r in regles if r['lot'] == 'combinaisons' and compte(r)]
    t = [r['id'] for r in regles if r['lot'] in LOTS_TEXTE and compte(r)]
    absent = [r['id'] for r in regles if r['statut'] == 'ABSENT_du_texte' and r['objet'] == code]
    manquant = [n for n, v in (('gamme', g), ('combinaison', k), ('texte_forme', t)) if not v]
    return dict(code=code, famille=famille, dans_catalogue='oui' if ligne_catalogue else 'non',
                priorite=(PRIORITAIRES.index(code) + 1 if code in PRIORITAIRES else ''),
                regles_gamme=' '.join(g), regles_combinaison=' '.join(k), regles_texte_et_forme=' '.join(t),
                absent_explicite=' '.join(absent), manquant=' '.join(manquant),
                statut_catalogue=(ligne_catalogue['statut_dimension'] if ligne_catalogue else ''))


def ecrire(regles, catalogue, sortie):
    os.makedirs(sortie, exist_ok=True)
    for lot in LOTS:
        with open(os.path.join(sortie, 'regles_%s.csv' % lot), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=COLONNES)
            w.writeheader()
            for r in regles:
                if r['lot'] == lot:
                    w.writerow({k: r[k] for k in COLONNES})
    par_code = {c['code']: c for c in catalogue}
    lignes = [ligne_couverture(regles, c, par_code.get(c)) for c in PRIORITAIRES]
    lignes += [ligne_couverture(regles, c, v) for c, v in par_code.items() if c not in PRIORITAIRES]
    with open(os.path.join(sortie, 'couverture_catalogue.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLONNES_COUVERTURE)
        w.writeheader()
        w.writerows(lignes)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    base = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument('--regles', default=os.path.join(base, 'regles_iisr.json'))
    ap.add_argument('--texte', default=os.path.expanduser('~/work/_iisr_extract'))
    ap.add_argument('--catalogue', default=os.path.expanduser('~/work/catalogue-3d/catalogue.csv'))
    ap.add_argument('--sortie', default=os.path.join(base, 'regenere'))
    a = ap.parse_args()
    regles = json.load(open(a.regles, encoding='utf-8'))
    pages = charger_pages(a.texte)
    ecarts = verifier(regles, pages)
    catalogue = list(csv.DictReader(open(a.catalogue, encoding='utf-8')))
    ecrire(regles, catalogue, a.sortie)
    par_statut = collections.Counter(r['statut'] for r in regles)
    print('%d règles ; %d extraits non retrouvés' % (len(regles), len(ecarts)))
    for e in ecarts:
        print('  ECART', e)
    print('statuts :', dict(par_statut))
    print('sortie :', a.sortie)
    return 1 if ecarts else 0


if __name__ == '__main__':
    sys.exit(main())
