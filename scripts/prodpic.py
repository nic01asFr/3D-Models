import json, os, base64, glob, bl, sys
from PIL import Image
sp=json.load(open('specs_pic.json')); res=[]
codes_only=sys.argv[1:] 
if codes_only: sp=[s for s in sp if s['code'] in codes_only]
DEF={'A':'01_A_danger','B':'03_B_prescription','C':'04_C_indication','CE':'05_CE_services','ID':'12_ID_ideogrammes','M':'11_M_panonceaux','KM':'11_M_panonceaux','H':'20_H_tourisme_culture','SR':'14_SR_information_securite','SC':'04_C_indication','SE':'04_C_indication','X':'19_X_dynamiques','XA':'15_XA','XAK':'10_AK_signalisation_temporaire','XD':'19_X_dynamiques','XK':'10_AK_signalisation_temporaire','KX':'19_X_dynamiques','KXC':'19_X_dynamiques','KS':'10_AK_signalisation_temporaire','SAL':'23_autres','KC':'10_AK_signalisation_temporaire'}
for i in range(0,len(sp),6):
    ch=sp[i:i+6]
    r=bl.run("exec(open('/projects/catalogue_panneaux/gen_gabarit.py').read())\nexec(open('/projects/catalogue_panneaux/gen_objets.py').read().split('exec(open',1)[1].split('\\n',1)[1])\nresult=run_gabarits(%r)"%(ch,))
    res+= r if isinstance(r,list) else [{'code':c['code'],'erreur':str(r)[:150]} for c in ch]
    open('progpic.txt','w').write('%d/%d'%(len(res),len(sp)))
    ok=[x['code'] for x in res if 'glb' in x]
    codes=[c['code'] for c in ch if c['code'] in ok]
    if not codes: continue
    r2=bl.run("import base64,os\nresult={}\nfor c in %r:\n    for sub,ext in (('glb_gab','.glb'),('vig_gab','.png')):\n        p='/projects/catalogue_panneaux/%%s/'%%sub+c+ext\n        result[c+ext]=base64.b64encode(open(p,'rb').read()).decode() if os.path.exists(p) else None"%(codes,))
    fam={s['code']:s['famille'] for s in ch}
    for k,v in r2.items():
        if not v: continue
        c,ext=os.path.splitext(k)
        if ext=='.glb':
            ex=glob.glob('/tmp/chk/panneaux/*/%s.glb'%c)
            d=ex[0] if ex else '/tmp/chk/panneaux/%s/%s.glb'%(DEF.get(fam[c],'23_autres'),c)
        else: d='/tmp/chk/vignettes/%s.png'%c
        open(d,'wb').write(base64.b64decode(v))
        if ext=='.png':
            im=Image.open(d).convert('RGBA'); im.thumbnail((256,256)); im.quantize(64,method=Image.Quantize.FASTOCTREE).save(d,optimize=True)
json.dump(res,open('res_pic.json','w'),ensure_ascii=False); open('progpic.txt','w').write('FIN')
