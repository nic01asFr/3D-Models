"""M1c_panonceaux_distance_sans_code.csv : phrases ou le panonceau de distance est cite sans code M, rapproche de M1
par l'equivalence nommee du texte (« panonceau de distance M1 », partie 4 p.28 notamment). Lancer depuis matrices/."""
import csv, os, re, sys
EXD = os.path.expanduser('~/work/_iisr_extract/')
def nz(s): return re.sub(r'\s+', ' ', s.replace('’', "'").replace('\xa0', ' ')).strip()
rows, seen = [], set()
for p in (3,):
    t = open(EXD + 'partie_%d.txt' % p, encoding='utf-8').read()
    segs = re.split(r'=== PAGE (\d+) ===', t)
    for i in range(1, len(segs) - 1, 2):
        pg = int(segs[i]); tx = nz(segs[i + 1])
        tx = re.sub(r'DSR/BSC.{0,120}?VP\d+ \d+ ', '', tx)
        phr = re.split(r'(?<=[\.;:])\s+(?=[A-ZÉ•\-−])', tx)
        for j, s in enumerate(phr):
            if 'panonceau de distance' not in s: continue
            s = s.replace('', '-').strip()
            if (pg, s[:80]) in seen: continue
            seen.add((pg, s[:80]))
            prec = phr[j - 1].replace('', '-').strip() if j else ''
            neg = bool(re.search(r"sans panonceau de distance|ne comportent (?:g[ée]n[ée]ralement )?pas|pas de panonceau de distance", s))
            if re.search(r'AB1 et AB2', s): src = 'AB1;AB2'
            elif pg == 7: src = 'indetermine (panneaux designes par la phrase precedente)'
            else: src = 'AB7'
            rows.append(dict(source=src, cible='M1', polarite='sans' if neg else 'avec',
                             modalite=('generalement' if 'g' in s and re.search(r'g[ée]n[ée]ralement', s) else ('exceptionnellement' if 'exceptionnellement' in s else '')),
                             page=pg, partie=3, extrait=s[:420], phrase_precedente=prec[:260],
                             statut='iisr', rapprochement='panonceau de distance = M1 (equivalence nommee dans le texte, partie 4 p.7 et p.28 : « panonceau de distance M1 »)'))
F = list(rows[0].keys())
with open(sys.argv[1] if len(sys.argv) > 1 else 'M1c_panonceaux_distance_sans_code.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, F); w.writeheader(); w.writerows(rows)
print(len(rows))
for r in rows: print(r['page'], r['source'], r['polarite'], r['modalite'], '|', r['extrait'][:110], '| PREC:', r['phrase_precedente'][:60])
