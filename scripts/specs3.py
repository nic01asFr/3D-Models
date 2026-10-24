import json, re, csv, textwrap
rg=list(csv.DictReader(open('/tmp/chk/docs/registre_catalogue_3d.csv')))
na=[r['code'] for r in rg if r['objet3d_statut']=='n.a.']
out=[]
def dyn(code,lines,couleur='ambre',W=1.5,H=0.8,kind='message'):
    out.append(dict(code=code,tpl='dynamique',w=W,h=H,lines=lines,couleur=couleur,famille='MSG',meta={'type_objet':kind,'aspect':'message dynamique d exemple (a valider)'}))
for c in na:
    if c.startswith('MSG:'):
        t=c[4:].replace('xxxx','1000').replace('yyyy','500').replace('XXX','300').replace(' / ','/')
        t=t.split('/')[0]
        ls=textwrap.wrap(t,14)[:3]; dyn(c,ls)
    elif c.startswith('ALERTE_'): dyn(c,['ALERTE',c[7:].replace('_',' ')],'rouge')
    elif c=='décompteur': dyn(c,['10:00'],'ambre',1.0,0.5,'dispositif')
    elif c=='CAR_EGAL': dyn(c,['='],W=0.5,H=0.5,kind='pictogramme')
    elif c=='CAR_EN_DIRECTION_DE': dyn(c,['=>'],W=0.5,H=0.5,kind='pictogramme')
    elif c=='CAR_SORTIE': dyn(c,['SORTIE'],W=0.8,H=0.4,kind='pictogramme')
    elif c=='triangle de présignalisation':
        out.append(dict(code=c,tpl='forme',forme='triangle',w=0.7,h=0.606,lines=['K'],dos=False,famille='TRIANGLE',meta={'type_objet':'dispositif','aspect':'silhouette'}))
print(len(out),[o['code'] for o in out])
json.dump(out,open('specs3.json','w'),ensure_ascii=False)
