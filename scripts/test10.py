
exec(open('/projects/catalogue_panneaux/gen.py').read())
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for c in list(bpy.data.collections): bpy.data.collections.remove(c)

def txt(body, k=0.28):
    return lambda z,th,s: _text(body, (s if not isinstance(s,tuple) else s[1])*k, z+th/2, th*0.8)
def disc_red_bar(z,th,s): return _bar(s*0.76, s*0.14, z+th/2, th*0.8, "Blanc_Retro")
def diag_bar(z,th,s): return _bar(s*0.80, s*0.07, z+th/2, th*0.8, "Rouge_Panneau", rot=math.radians(-45))
def stop_txt(z,th,s): return _text("STOP", s*0.30, z+th/2, th*0.8, "Blanc_Retro")

S = {
 "B0":      dict(kind="disc", size=0.65, border="Rouge_Panneau", fill="Blanc_Retro", name="Circulation interdite"),
 "B1":      dict(kind="disc", size=0.65, border="Rouge_Panneau", fill="Rouge_Panneau", border_ratio=0.999, picto=[disc_red_bar], name="Sens interdit"),
 "B6a1":    dict(kind="disc", size=0.65, border="Rouge_Panneau", fill="Bleu_Panneau", picto=[diag_bar], name="Stationnement interdit"),
 "B14_30":  dict(kind="disc", size=0.65, border="Rouge_Panneau", fill="Blanc_Retro", picto=[txt("30",0.38)], name="Limitation de vitesse 30"),
 "B14_50":  dict(kind="disc", size=0.65, border="Rouge_Panneau", fill="Blanc_Retro", picto=[txt("50",0.38)], name="Limitation de vitesse 50"),
 "B14_90":  dict(kind="disc", size=0.65, border="Rouge_Panneau", fill="Blanc_Retro", picto=[txt("90",0.38)], name="Limitation de vitesse 90"),
 "AB3a":    dict(kind="tri_inv", size=1.0, border="Rouge_Panneau", fill="Blanc_Retro", name="Cédez le passage"),
 "AB4":     dict(kind="oct", size=0.65, border="Blanc_Retro", fill="Rouge_Panneau", border_ratio=0.93, picto=[stop_txt], name="Stop"),
 "A_tri":   dict(kind="tri", size=1.0, border="Rouge_Panneau", fill="Blanc_Retro", name="Gabarit triangle danger (sans picto)"),
 "M1_100m": dict(kind="rect", size=(0.65,0.25), border="Noir_Pictogramme", fill="Blanc_Retro", border_ratio=0.95, picto=[txt("100 m",0.5)], name="Panonceau distance (démo)"),
}
roots=[]
for i,(code,spec) in enumerate(S.items()):
    root,col = make_sign(code,spec); root.location=((i%5)*1.4,0,1.0+ (i//5)*-1.3 + 1.3); roots.append(root)
bpy.ops.wm.save_as_mainfile(filepath='/projects/catalogue_panneaux/test10.blend')
# export glb individuel
os.makedirs('/projects/catalogue_panneaux/glb',exist_ok=True)
for root in roots:
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for ch in root.children_recursive: ch.select_set(True)
    loc=root.location.copy(); root.location=(0,0,0)
    bpy.ops.export_scene.gltf(filepath=f'/projects/catalogue_panneaux/glb/{root.name}.glb', use_selection=True, export_format='GLB')
    root.location=loc
result={'n':len(roots),'glb':sorted(os.listdir('/projects/catalogue_panneaux/glb'))}
