"""Règles de composition de la signalisation de direction (IISR 5e partie, art. 81 C et 81-1, VC20240315).
Chaque règle porte sa source (id matrice, article, page). Validateur sans dépendance Blender."""
import json, re

REGLES = {
  "ordre_blocs_couleur": {"valeur": ["bleu", "vert", "blanc", "jaune"], "src": "art. 81 C p.43 (IISR 5e partie)",
      "texte": "Les blocs sont répartis de haut en bas dans l'ordre : bleu, vert, blanc, jaune."},
  "ordre_dans_bloc": {"valeur": "distances_decroissantes_de_haut_en_bas", "src": "C290 art. 81-1 p.43",
      "texte": "Pour chaque couleur, les mentions sont inscrites de haut en bas par ordre de distances décroissantes."},
  "max_mentions_par_direction_et_couleur": {"valeur": 4, "src": "C285 art. 81-1 p.42-43",
      "texte": "Position, avancée, confirmation : 4 mentions au plus pour une même couleur par direction."},
  "max_mentions_par_direction_multicolore": {"valeur": 6, "src": "C285 art. 81-1 p.43",
      "texte": "...et au plus 6 si l'ensemble comporte plusieurs couleurs."},
  "max_mentions_presignalisation": {"valeur": 6, "src": "C286 art. 81-1 p.43", "derogation": {"D42": 9},
      "texte": "Présignalisation : 6 mentions ; sur les D42 jusqu'à 9 si cela évite le dédoublement."},
  "max_mentions_bifurcation": {"valeur": 4, "src": "C287 art. 81-1 p.43", "texte": "Panneau d'avertissement de bifurcation : 4 mentions au maximum."},
  "max_mentions_portique_affectation": {"valeur": 12, "src": "C288 art. 81-1 p.43", "texte": "Affectation de voies sur portique : 12 mentions pour l'ensemble des directions."},
  "max_mentions_filante_hors_urbain_autoroutier": {"valeur": 4, "src": "C289 art. 81-1 p.43", "texte": "Voiries autoroutières hors zone urbaine : 4 mentions en filante."},
  "max_mentions_D71": {"valeur": 3, "src": "art. 81 C p.43", "texte": "Panneau D71 : 3 mentions."},
  "max_idéogrammes": {"par_mention": 2, "par_panneau": 3, "src": "C306 art. 82-1 p.46"},
  "registre": {"src": "C269 art. 81-1 p.41", "texte": "Un registre = une seule couleur de fond, une ou plusieurs mentions."},
  "distance_sans_unite_km": {"src": "C291 art. 81-1 p.43", "texte": "Distances en km, jamais complétées d'un symbole d'unité."},
  "distance_arrondi": {"src": "art. 81 C p.43", "texte": ">5 km : km voisin ; 1 à 5 km : 1/2 km ou km voisin ; <1 km : hectomètre voisin."},
  "distance_locale_metres": {"src": "C292 art. 81-1 p.43", "texte": "Mentions d'intérêt local : <500 m exprimées en mètres avec le symbole m."},
  "casse": {"src": "art. 81-1 c) p.42 (C274-C276)",
      "texte": "Majuscules L1/L2 : pôle qui est une agglomération. Majuscules L4 : pôle classé non agglomération, mention secondaire, rabattement autoroute. Minuscules L4 (initiale majuscule pour les noms propres) : autres mentions."},
  "couleur_fond": {"src": "C277-C282 art. 81-1 p.42", "texte": "Liaison verte : fond vert ; liaison blanche : fond blanc ; exploitation (S, Bis) : jaune ; rabattement autoroute : bleu ; autres voiries : blanc."},
}

def arrondi_distance_km(d):
    if d > 5: return round(d)
    if d >= 1: return round(d * 2) / 2
    return round(d * 10) / 10  # hectomètre voisin

def valider(panneau):
    """panneau = {'type': 'position|avancee|confirmation|presignalisation|bifurcation|portique|D71|D42|filante_autoroutiere',
    'registres': [{'couleur': 'vert', 'mentions': [{'texte': 'MARSEILLE', 'distance_km': 12, 'direction': 'g'}]}]}"""
    err = []
    R = REGLES; t = panneau.get('type', 'position')
    ordre = R['ordre_blocs_couleur']['valeur']
    cols = [r['couleur'] for r in panneau['registres']]
    idx = [ordre.index(c) for c in cols if c in ordre]
    if idx != sorted(idx): err.append('ordre des blocs de couleur (bleu, vert, blanc, jaune)')
    tot = 0; multic = len(set(cols)) > 1
    for r in panneau['registres']:
        ds = [m.get('distance_km') for m in r['mentions'] if m.get('distance_km') is not None]
        if ds != sorted(ds, reverse=True): err.append('distances non décroissantes dans le bloc ' + r['couleur'])
        n = len(r['mentions']); tot += n
        if t in ('position', 'avancee', 'confirmation') and n > R['max_mentions_par_direction_et_couleur']['valeur']:
            err.append('plus de 4 mentions pour la couleur ' + r['couleur'])
    lim = {'presignalisation': 6, 'D42': 9, 'bifurcation': 4, 'portique': 12, 'D71': 3, 'filante_autoroutiere': 4}.get(t)
    if t in ('position', 'avancee', 'confirmation') and multic: lim = 6
    if lim and tot > lim: err.append('%d mentions > limite %d (%s)' % (tot, lim, t))
    return err

if __name__ == '__main__':
    json.dump(REGLES, open('regles_composition_directionnelle.json', 'w'), ensure_ascii=False, indent=1)
    ok = {'type': 'presignalisation', 'registres': [{'couleur': 'vert', 'mentions': [{'texte': 'MARSEILLE', 'distance_km': 12}, {'texte': 'TOULON', 'distance_km': 8}]}]}
    ko = {'type': 'D71', 'registres': [{'couleur': 'vert', 'mentions': [{'distance_km': 3}, {'distance_km': 8}, {'distance_km': 1}, {'distance_km': 2}]}, {'couleur': 'bleu', 'mentions': []}]}
    print(valider(ok), valider(ko))
