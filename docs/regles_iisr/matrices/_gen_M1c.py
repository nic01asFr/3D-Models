"""Genere M1c : verdict par ligne de M1b (phrase a phrase), modalite, condition, article. Lancer depuis matrices/."""
import csv, re, sys
EX = '/home/onyxia/work/_iisr_extract/' if False else None
import os
EXD = os.path.expanduser('~/work/_iisr_extract/')
R = list(csv.DictReader(open('M1b_panonceaux_cites_par_code.csv', encoding='utf-8')))

def nz(s):
    return re.sub(r'\s+', ' ', s.replace('’', "'").replace('\xa0', ' ')).strip()

RAW = {p: open(EXD + 'partie_%d.txt' % p, encoding='utf-8').read() for p in range(1, 10)}

def article_de(partie, page, extrait):
    t = RAW[int(partie)]
    segs = re.split(r'=== PAGE (\d+) ===', t)
    pages = {int(segs[i]): segs[i + 1] for i in range(1, len(segs) - 1, 2)}
    cible = int(page)
    # texte brut cumule jusqu'a la page cible incluse, position de la phrase dans la page cible
    mots = nz(extrait).split(' ')[:7]
    rx = r'\s*'.join(re.escape(m) for m in mots)
    pg = pages[cible].replace('’', "'")
    m = re.search(rx, pg)
    if not m:
        return ''
    avant = ''.join(pages[k].replace('’', "'") for k in sorted(pages) if k < cible) + pg[:m.start()]
    heads = re.findall(r'(?m)^\s*Article\s+(\d+(?:-\d+)*)\s*[\.\-–:]', avant)
    heads = [h for h in heads]
    # exclure les lignes de sommaire (points de conduite) : deja filtre car 'Article N. Titre ....' contient des points ; verifier ci-dessous
    lines = [l for l in avant.split('\n') if re.match(r'\s*Article\s+\d+(?:-\d+)*\s*[\.\-–:]', l) and '....' not in l]
    if not lines:
        return ''
    return re.match(r'\s*Article\s+(\d+(?:-\d+)*)', lines[-1]).group(1)

# ---- verdicts phrase a phrase (indices = ordre de premiere apparition des phrases non univoques dans M1b)
S = {}
for r in R:
    if r['condition'] != 'appariement : univoque':
        S.setdefault((r['partie'], r['page'], r['extrait']), []).append(r)
L = list(S.keys())

A = 'admis'; C = 'admis_conditionnel'; I = 'indetermine'
V = {}   # index phrase -> {(src,cible): (verdict, modalite, condition)}
V[0] = {('A13b', 'M9d'): (A, 'complete par', '')}
V[1] = {('A1c', 'M2'): (A, 'accompagne', 'serie plus longue de courbes'), ('A1d', 'M2'): (A, 'accompagne', 'serie plus longue de courbes')}
cond2 = 'surface de servitude de navigation aerienne a moins de 10 m au-dessus de la chaussee ; mention SAUF AUTORISATION ; un panonceau pour les deux panneaux sur le meme support'
V[2] = {('A23', 'M9'): (A, 'completes par', cond2), ('B12', 'M9'): (A, 'completes par', cond2)}
V[3] = {('A7', 'M9a'): (A, 'doit etre complete', 'signalisation de zone aerienne ; silhouette d\'un avion')}
V[4] = {('A7', 'M9b'): (A, 'complete par', 'symbole de l\'electricite'), ('A8', 'M9b'): (A, 'complete par', 'symbole de l\'electricite')}
for k, a in ((5, 'A9a'), (6, 'A9b')):
    V[k] = {(a, 'M9b'): (A, 'peut etre complete (M9b ou M9z)', 'symbole de l\'electricite'), (a, 'M9z'): (A, 'peut etre complete (M9b ou M9z)', 'symbole de l\'electricite')}
V[7] = {('AB3a', 'M9c'): (A, 'complete par', 'regime Cedez le passage')}
V[8] = {('AB3a', 'M9c'): (A, 'complete par', 'route non prioritaire barre horizontale du T'), ('AB3a', 'M7'): (A, 'panonceau-schema', 'route non prioritaire barre horizontale du T'), ('AB6', 'M7'): (I, 'avec panonceau-schema (code non donne)', '')}
V[9] = {('AB3a', 'M9c'): (A, 'complete par', 'branche qui perd la priorite'), ('AB3a', 'M7'): (A, 'panonceau-schema', 'branche qui perd la priorite')}
V[10] = {('AB3a', 'M9c'): (A, 'complete par', '')}
V[11] = {('AB3a', 'M9c'): (A, 'complete par', 'route qui perd la priorite')}
V[12] = {('AB3a', 'M9c'): (A, 'son panonceau', 'branches perdant leur priorite')}
for k in (13, 14, 15, 16):
    V[k] = {('AB3a', 'M9c'): (A, 'complete par', '')}
V[17] = {('C24a', 'M1'): (A, 'est complete', 'panonceau de distance'), ('B29', 'M3a1'): (A, 'complete par', 'signalisation de position ; panonceau directionnel')}
V[18] = {('B5c', 'M9z'): (C, 'doit etre complete', 'utilisation du panneau CE64d ou du signal XCE64d sur le poste de peage ; inscription SAUF TELEPEAGE')}
V[19] = {('B6a', 'M6a'): (A, 'on distingue les panonceaux', ''), ('B6b', 'M6a'): (A, 'on distingue les panonceaux', ''), ('C1', 'M6a'): (A, 'on distingue les panonceaux', '')}
V[20] = {('B6a', 'M8b'): (C, 'peut etre signalee', 'fin de prescription de stationnement ou d\'arret'), ('B6d', 'M8b'): (C, 'peut etre signalee', 'fin de prescription de stationnement ou d\'arret')}
V[21] = {(b, m): (C, 'il est possible ; par exemple', 'precisions des paragraphes 1 a 5 insuffisantes ; liste non exhaustive') for b in ('B6a1', 'B6a2', 'B6a3') for m in ('M1', 'M2', 'M4', 'M6f')}
V[22] = {('B6a1', 'M6b'): (A, 'complete par', 'regime de stationnement'), ('B6b', 'M6b'): (I, 'phrase non rattachante (B6b cite apres \"ainsi que\")', '')}
V[23] = {('B6a2', 'M6b'): (A, 'peuvent etre completes', 'regime article R.417-2'), ('B6a3', 'M6b'): (A, 'peuvent etre completes', 'regime article R.417-2')}
V[24] = {('CE15e', 'M9z'): (C, 's\'il y a lieu', 'aires de service ; a 800 m ; inscription AUTOMATE'), ('CE15f', 'M9z'): (C, 's\'il y a lieu', 'aires de service ; a 800 m ; inscription AUTOMATE')}
V[25] = {('C26a', 'M3'): (A, 'complete par', 'signalisation de position'), ('C26b', 'M3'): (A, 'complete par', 'signalisation de position'),
         ('C26a', 'M1'): (A, 'complete par', 'presignalisation'), ('C26b', 'M1'): (A, 'complete par', 'presignalisation'),
         ('C26a', 'M9z'): (C, 'le cas echeant', 'presignalisation ; inscription VOIE DE DETRESSE en plusieurs langues'), ('C26b', 'M9z'): (C, 'le cas echeant', 'presignalisation ; inscription VOIE DE DETRESSE en plusieurs langues')}
V[26] = {('CE15e', 'M9z'): (A, 'complete par', 'a 600 m ; prix des carburants ; AUTOMATE le cas echeant'), ('CE15f', 'M9z'): (A, 'complete par', 'a 600 m ; prix des carburants ; AUTOMATE le cas echeant'),
         ('CE15e', 'M1a'): (A, 'doivent etre completes', 'a 300 m ; station suivante'), ('CE15f', 'M1a'): (A, 'doivent etre completes', 'a 300 m ; station suivante')}
NEG = {('B17', 'M2'): (A, 'generalement complete', ''), ('C1a', 'M1'): (C, 'complete par', 'presignalisation seulement'),
       ('C20b', 'M9z'): (C, 'peut etre complete', 'traversee sans signalisation lumineuse ; inscription PRIORITE AU BUS'),
       ('C20c', 'M9z'): (C, 'peut etre complete', 'traversee sans signalisation lumineuse')}
MODRX = re.compile(r'\b(doit|doivent|peut|peuvent|obligatoire|g[ée]n[ée]ralement|il est possible|s\'il y a lieu|le cas [ée]ch[ée]ant|est compl[ée]t[ée]|compl[ée]t[ée]s?|accompagn[ée]s?)\b', re.I)
idx = {k: i for i, k in enumerate(L)}
out = []
for r in R:
    key = (r['partie'], r['page'], r['extrait'])
    pair = (r['source'], r['cible'])
    if r['condition'] != 'appariement : univoque':
        d = V[idx[key]]
        v, mod, cond = d.get(pair, ('non_etabli', 'la phrase rattache ce panonceau a un autre panneau', ''))
        origine = 'phrase_multiple'
    elif 'negation' in r['relation']:
        v, mod, cond = NEG[pair]; origine = 'negation_ou_exception'
    else:
        m = MODRX.search(r['extrait'])
        v, mod, cond = 'admis', (m.group(1) if m else ''), ''
        origine = 'univoque'
    out.append(dict(source=r['source'], cible=r['cible'], verdict=v, modalite=mod, condition_emploi=cond,
                    article=article_de(r['partie'], r['page'], r['extrait']), page=r['page'], partie=r['partie'],
                    origine_m1b=origine, extrait=r['extrait'], statut=r['statut']))
F = list(out[0].keys())
dest = sys.argv[1] if len(sys.argv) > 1 else 'M1c_panonceaux_verdicts.csv'
with open(dest, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, F); w.writeheader(); w.writerows(out)
import collections
print(len(out), collections.Counter(o['verdict'] for o in out), 'articles vides :', sum(1 for o in out if not o['article']))
