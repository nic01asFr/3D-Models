import csv, json, re
rows=list(csv.DictReader(open('docs/registre_catalogue_3d.csv')))
m=json.load(open('matrice_v3_normalisee.json'))
lib={x['code']:(x.get('libelle') or '') for x in m['signaux']}
VILLES=['Marseille','Aix-en-Provence','Toulon','Avignon','Nîmes','Arles']
def S(code,tpl,w,h,**k): d=dict(code=code,tpl=tpl,w=w,h=h); d.update(k); return d
def spec(code,fam):
    L=lib.get(code,'').lower(); N=re.sub(r'^[A-Za-z]+','',code); n=int(re.match(r'\d+',N).group()) if re.match(r'\d+',N) else 0
    auto=any(t in L for t in ('autorout','échangeur','péage','sortie','bifurcation'))
    bg,fg=('bleu','blanc') if auto else ('vert','blanc')
    v=VILLES
    if fam=='G':
        if code=='G2': return S(code,'balisePN',0.35,1.0,barres=1)
        if code=='G3': return S(code,'plaque',1.5,0.4,bg='jaune',fg='noir',lines=['GABARIT','4,30 m'])
        return S(code,'croix',1.2,1.2,bis=code.endswith('bis'))
    if fam=='XKD': return S(code,'dynamique',1.0,1.0,lines=['DEVIATION',code],couleur='jaune')
    if fam in('XB','XC','XCE','XM'):
        ov={'XB14':['50'],'XB26':['CHAINES'],'XCE15g':['1,89 €/L'],'XCE15h':['1,95 €/L'],'XCE15a':['STATION','FERMEE'],'XCE45':['PARKING','120 places'],'XCE22':['RADIO','107.7'],'XC50':['TEXTE','LIBRE'],'XM9z':['VERGLAS']}
        sz=(1.0,0.4) if fam=='XM' else ((1.2,0.8) if fam in('XCE','XC') else (1.0,1.0))
        return S(code,'dynamique',*sz,lines=ov.get(code,[code]))
    if fam=='KD':
        if code in('KD8','KD9','KD10','KD10a','KD10b'): return S(code,'affectation',2.0,1.4,bg='jaune',fg='noir',lines=['DEVIATION'],voies=3)
        if n in(69,): return S(code,'deviation',1.8,0.7,lines=['FIN DE','DEVIATION'])
        ar=0 if n in(21,22,62,79) else 90
        return S(code,'deviation',1.8,1.0,lines=['DEVIATION',v[0],v[2]],arrow=ar)
    if fam=='DA': return S(code,'affectation',2.4,1.6,bg=bg,fg=fg,lines=[v[2]],voies=3)
    if fam=='DC':
        if n==43: return S(code,'dirfleche',1.4,0.7,bg='bleu',fg='blanc',lines=['Zone d’activités','500 m'],arrow=90,alphabet='L4')
        return S(code,'position',1.2,0.5,bg='bleu',fg='blanc',lines=['Zone d’activités'],alphabet='L4',italic=True)
    if fam=='DP':
        if n==29: return S(code,'position',1.0,0.45,bg='vert',fg='blanc',lines=['Centre-ville'],alphabet='L5')
        return S(code,'dirfleche',1.0,0.5,bg='vert',fg='blanc',lines=['Centre-ville','300 m'],arrow=90 if n!=43 else 0)
    if fam=='DV':
        if n in(10,12,20,21): return S(code,'position',1.2,0.5,bg='vert',fg='blanc',lines=['Véloroute V63'] if n in(10,12) else [v[0],'12 km'])
        if n==42: return S(code,'presign',1.6,1.1,bg='vert',fg='blanc',lines=[v[0],v[1]])
        if n==44: return S(code,'plaque',0.5,0.25,bg='vert',fg='blanc',lines=['VÉLO'])
        return S(code,'dirfleche',1.4,0.7,bg='vert',fg='blanc',lines=[v[0],'12 km'],arrow=0)
    if fam=='E':
        if 40<=n<=47 and n not in(45,):
            c={41:('E 15','vert','blanc'),42:('N 568','rouge','blanc'),43:('D 7','jaune','noir'),44:('C 12','blanc','noir'),46:('RN 8','rouge','blanc'),47:('A 55','bleu','blanc'),40:('N 7','rouge','blanc')}.get(n,('N 7','rouge','blanc'))
            return S(code,'cartouche',0.5,0.3,bg=c[1],fg=c[2],lines=[c[0]])
        if n==45: return S(code,'cartouche',0.5,0.3,bg='rouge',fg='blanc',lines=['N 7'])
        if n==60: return S(code,'plaque',0.6,0.2,bg='bleu',fg='blanc',lines=['Rue de la République'])
        if 50<=n<=57:
            c={52:('rouge','blanc'),53:('jaune','noir'),54:('blanc','noir'),57:('bleu','blanc')}.get(n,('blanc','noir'))
            return S(code,'plaque',0.4,0.25,bg=c[0],fg=c[1],lines=['RN 568','PR 12'])
        t={30:('blanc','noir',['Marseille']),31:('blanc','noir',['Rocade L2']),32:('bleu','blanc',['La Durance']),33:('vert','blanc',['Parc national']),34:('bleu','blanc',['Aire de repos']),36:('blanc','noir',['BOUCHES-DU-RHÔNE']),37:('blanc','noir',['Œuvre d’art']),38:('bleu','blanc',['Domaine autoroutier'])}.get(n,('blanc','noir',['Localisation']))
        return S(code,'position',1.4,0.5,bg=t[0],fg=t[1],lines=t[2],alphabet='L5' if n==36 else 'L1')
    # D
    if n in(20,21,29): return S(code,'position',1.6,0.7,bg=bg,fg=fg,lines=[v[0],'12 km'] if code.endswith('a') else [v[0]])
    if n in(30,31,32,50,51,52): return S(code,'dirfleche',2.0,1.3,bg=bg,fg=fg,lines=[v[0],v[2],'Sortie 12'],arrow=45 if n<40 else 90)
    if n in(40,41,42,43): return S(code,'presign',2.0,1.4,bg=bg,fg=fg,lines=[v[1],v[0],v[2]])
    if n in(44,46,47,48): return S(code,'dirfleche',1.6,0.9,bg='bleu',fg='blanc',lines=['AIRE DE LA CRAU','2 km'],arrow=90)
    if n in(60,61,62,63): return S(code,'position',1.6,0.7,bg=bg,fg=fg,lines=[v[0],'12 km'])
    if n==69: return S(code,'position',1.2,0.6,bg=bg,fg=fg,lines=['FIN','ITINÉRAIRE '+('BIS' if code.endswith('b') else 'S')])
    if n>=70: return S(code,'position',1.0,0.5,bg=bg,fg=fg,lines=['Itinéraire','S 12'])
    return S(code,'dirfleche',1.8,0.9,bg=bg,fg=fg,lines=[v[0],'12 km'],arrow=0)
g=[r for r in rows if r['objet3d_statut'].startswith('gabarit')]
specs=[]
for r in g:
    s=spec(r['code'],r['famille'].upper() if r['famille'] in('Da','Dc') else r['famille']); s['famille']=r['famille']; specs.append(s)
# dedupe codes
seen=set(); out=[]
for s in specs:
    if s['code'] in seen: continue
    seen.add(s['code']); out.append(s)
json.dump(out,open('specs.json','w'),ensure_ascii=False)
import collections; print(len(out),collections.Counter(s['tpl'] for s in out))
