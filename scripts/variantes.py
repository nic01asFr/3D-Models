"""Differencie les variantes (E33/E34/E36/E37/E52-57, G1*, KD*) d'apres les textes IISR de la matrice. Contenus = exemples."""
import json
S={s['code']:s for s in json.load(open('/tmp/chk/scripts/specs_gabarits.json'))}
out=[]
def put(c,**k):
    s=dict(S[c]); s.update(k); s['meta']=dict(s.get('meta',{}), aspect='variante differenciee d\'apres l\'IISR (contenu exemple)'); out.append(s)
# E : localisation
put('E33a',lines=['Parc national','des Calanques']); put('E33b',lines=['Commune du','Parc national'],h=0.7)
put('E34a',lines=['Aire de la Crau']); put('E34b',lines=['Aire de la Crau','Sortie'],h=0.7)
put('E34c',lines=['Aire de Montélimar']); put('E34d',lines=['Aire de Montélimar','Sortie'],h=0.7)
put('E36a',lines=['BOUCHES-DU-RHÔNE']); put('E36b',lines=['PROVENCE-ALPES','CÔTE D’AZUR'],h=0.7)
put('E37a',lines=['Le Penseur','A. Rodin'],h=0.7); put('E37b',lines=['A. Rodin'])
# E52-57 : a = borne ; b = borne + altitude ; c = plaquette
for base,bg in (('E52','rouge'),('E53','jaune'),('E54','blanc'),('E57','bleu')):
    fg='noir' if bg in('jaune','blanc') else 'blanc'
    put(base+'a',w=0.25,h=0.4,bg=bg,fg=fg,lines=['RN 568','PR 12'])
    put(base+'b',w=0.25,h=0.55,bg=bg,fg=fg,lines=['RN 568','PR 12','Alt. 120 m'])
    put(base+'c',w=0.4,h=0.25,bg=bg,fg=fg,lines=['RN 568','PR 12'])
# G1 : voie unique / plusieurs voies ; bis = signalisation automatique lumineuse
for c,n,bis in (('G1',1,False),('G1b',1,False),('G1bis',1,True),('G1a',2,False),('G1c',2,False),('G1abis',2,True),('G1cbis',2,True)):
    L=1.2*(0.78 if n>1 else 1.0); H=L*(1+1.04*(n-1))+(0.3 if bis else 0)
    put(c,n=n,bis=bis,w=1.3,h=round(H,2))
# KD
V=lambda t:['DÉVIATION' if t=='dev' else '', 'MARSEILLE','TOULON']
def kd(c,sil=False,ville=False,vert=False):
    L0='' if sil and ville else ('DÉVIATION' if not ville else 'MARSEILLE')
    if sil: lines=['', 'MARSEILLE'] if ville else ['', 'DÉVIATION']
    else: lines=[L0,'TOULON'] if ville else ['DÉVIATION']
    kw=dict(lines=[l for l in lines] if lines else ['DÉVIATION'],sil=sil)
    if vert: kw.update(bg='vert',fgc='blanc')
    kw['lines']=[l for l in kw['lines']] 
    kw['h']=0.8 if len(lines)>=2 else 0.5
    put(c,**kw)
for p in ('KD21','KD22','KD42','KD43'):
    kd(p+'a'); kd(p+'b',sil=True); 
    if p in('KD21','KD42','KD43'): pass
for p in ('KD42','KD43'):
    kd(p+'c',ville=True); kd(p+'d',sil=True,ville=True)
kd('KD42e',ville=True,vert=True)
for c in ('KD21a','KD21b','KD22a','KD22b'): pass
codes=[s['code'] for s in out]
fam={'E':'E','G':'G','K':'KD'}
for s in out: s['famille']=S[s['code']]['famille']
json.dump(out,open('/tmp/gab/specs_var.json','w'),ensure_ascii=False); print(len(out),codes)
