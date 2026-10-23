
exec(open('/projects/catalogue_panneaux/gen_support.py').read())
D=json.load(open('/projects/catalogue_panneaux/defauts_supports.json'))
def dv(k): return D[k]['valeur']

def _box(name,dx,dy,dz,loc,mat,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.scale=(dx,dy,dz); o.name=name
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if parent: o.parent=parent
    return o

def _foot(root,name,x,y,mat,conc,sect,massif):
    pc=dv('platine_cote_m'); pe=dv('platine_epaisseur_m'); sur=dv('platine_surplomb_sol_m')
    _box(name+'_platine',pc,pc,pe,(x,y,sur+pe/2),mat,root)
    mx,my,mz=massif
    _box(name+'_massif',mx,my,mz,(x,y,-mz/2),conc,root)

def assemble_support(cfg):
    """cfg: name, type in potence|portique|haut_mat|mat_feu ; elements:[{code,dx}] ; paramètres optionnels."""
    t=cfg['type']; root=bpy.data.objects.new(cfg['name'],None); bpy.context.scene.collection.objects.link(root)
    steel=_mat('Acier_Galvanise',(0.55,0.57,0.6,1),0.9,0.4); alu=_mat('Aluminium_Structure',(0.72,0.73,0.75,1),0.85,0.35)
    conc=_mat('Beton_Massif',(0.5,0.5,0.48,1),0.0,0.9)
    gab=dv('gabarit_route_m'); zbas=cfg.get('bord_inferieur',gab+dv('revanche_entretien_m')+dv('revanche_protection_m'))
    ecart=cfg.get('ecart',dv('ecart_entre_panneaux_m'))
    parts=[]; sources=['IISR E077 (bord inférieur = gabarit + 0,10 + 0,50)']
    # panneaux : placement en x selon dx (centre) ; z_bas commun
    items=[]
    for el in cfg['elements']:
        r,(w,h,th),new=load_sign(el['code']); items.append((el,r,w,h))
    hmax=max(h for _,_,_,h in items)
    if t=='potence':
        ms=cfg.get('montant_section',dv('potence_montant_section_m')); bs=cfg.get('bras_section',dv('potence_bras_section_m')); av=cfg.get('avancee',dv('potence_avancee_m'))
        hm=zbas+hmax+0.25
        _box(cfg['name']+'_montant',ms,ms,hm,(0,0,0.13+hm/2),alu,root)
        _foot(root,cfg['name'],0,0,steel,conc,ms,cfg.get('massif',dv('massif_lourd_m')))
        zb=0.13+hm-bs/2-0.05
        _box(cfg['name']+'_bras',av,bs,bs,(ms/2+av/2,0,zb),alu,root)
        x0=ms/2; ymont=ms/2+0.02
        for el,r,w,h in items:
            x=x0+el.get('dx',av/2)
            r.location=(x,-bs/2-0.02,zbas+h/2); r.parent=root
            parts.append(dict(code=el['code'],x=round(x,3),z_bas=round(zbas,3),largeur=w,hauteur=h))
        sources.append('hypothèses : section montant/bras, avancée (voir defauts_supports.json)')
    elif t=='portique':
        L=cfg.get('portee',dv('portique_portee_m')); ms=cfg.get('montant_section',dv('portique_montant_section_m')); bs=cfg.get('traverse_section',dv('portique_traverse_section_m'))
        hm=zbas+hmax+0.35
        for sgn,nm in ((-1,'G'),(1,'D')):
            x=sgn*(L/2+ms/2)
            _box(f"{cfg['name']}_montant{nm}",ms,ms,hm,(x,0,0.13+hm/2),alu,root)
            _foot(root,f"{cfg['name']}_{nm}",x,0,steel,conc,ms,cfg.get('massif',dv('massif_lourd_m')))
        zt=0.13+hm-bs/2
        _box(cfg['name']+'_traverse',L+2*ms,bs,bs,(0,0,zt),alu,root)
        for el,r,w,h in items:
            x=el.get('dx',0.0)
            r.location=(x,-bs/2-0.02,zbas+h/2); r.parent=root
            parts.append(dict(code=el['code'],x=round(x,3),z_bas=round(zbas,3),largeur=w,hauteur=h))
        sources.append('hypothèses : portée, sections (voir defauts_supports.json)')
    elif t=='haut_mat':
        hh=cfg.get('hauteur',dv('hautmat_hauteur_m')); ms=cfg.get('montant_section',dv('hautmat_section_m'))
        _box(cfg['name']+'_montant',ms,ms,hh,(0,0,0.13+hh/2),alu,root)
        _foot(root,cfg['name'],0,0,steel,conc,ms,cfg.get('massif',dv('massif_lourd_m')))
        zb=cfg.get('bord_inferieur',3.5)
        for el,r,w,h in items:
            r.location=(el.get('dx',0.0),-ms/2-0.02,zb+h/2); r.parent=root
            parts.append(dict(code=el['code'],z_bas=round(zb,3),largeur=w,hauteur=h))
        sources.append('IISR : PMV sur haut-mât entre 3,50 et 6,50 m ; autres cotes = hypothèses')
    elif t=='mat_feu':
        dia=cfg.get('diametre',dv('mat_feu_diametre_m')); hh=cfg.get('hauteur',dv('mat_feu_hauteur_m'))
        _cyl(cfg['name']+'_mat',dia/2,0,hh,0,steel).parent=root
        zb=cfg.get('bord_inferieur',2.3)
        z=zb
        for el,r,w,h in items:
            r.location=(el.get('dx',0.0),-dia/2-0.02,z+h/2); r.parent=root; z+=h+ecart
            parts.append(dict(code=el['code'],z_bas=round(zb,3),largeur=w,hauteur=h))
        sources.append('hypothèses : diamètre et hauteur du mât de feu')
    root['type_support']=t; root['configuration']=json.dumps(cfg,ensure_ascii=False)
    root['elements_calcules']=json.dumps(parts,ensure_ascii=False); root['sources_regles']=' ; '.join(sources)
    root['statut']='valeurs par défaut : voir defauts_supports.json (statut iisr / guide / hypothese)'
    return root,parts
