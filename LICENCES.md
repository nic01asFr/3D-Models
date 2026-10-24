# Licences

- **Code** (`scripts/`) : MIT.
- **Objets 3D et SVG** : dérivés des pictogrammes publiés sur Wikimedia Commons, chacun sous sa licence d'origine.
  Les licences CC BY-SA imposent l'attribution et le partage à l'identique : les GLB correspondants restent sous la même licence.

| Licence | Nombre de panneaux |
|---|---|
| CC BY-SA 3.0 | 108 |
| CC BY-SA 4.0 | 104 |
| Public domain | 103 |
| Licence Ouverte | 95 |
| CC0 | 24 |
| CC BY 4.0 | 6 |

L'auteur, la licence et la source de **chaque** panneau figurent dans `catalogue.csv`, dans `manifeste.json` et dans les propriétés personnalisées du GLB.
Toute réutilisation doit conserver cette attribution.

## Gabarits, silhouettes et modèles paramétriques

Les objets générés par `scripts/gen_gabarit.py` et `scripts/gen_objets.py` (gabarits direction/texte, cartouches, dynamiques, feux, balises, dispositifs, silhouettes, messages) sont des géométries produites par le code du dépôt : **CC0** pour la géométrie, **MIT** pour le code. Les lettres sont tracées avec la police Noto Sans CJK Regular distribuée avec Blender (glyphes latins issus de Source Sans, SIL Open Font License 1.1), qui autorise l'usage des glyphes dans des œuvres dérivées ; elle remplace provisoirement les alphabets L1, L2, L4 et L5 de l'IISR. Correction : une version précédente de ce dépôt indiquait à tort « police intégrée de Blender (Inter) » ; la police réellement employée était la police interne de Blender, remplacée depuis par la police ci-dessus (fichier de police non redistribué ici : seuls les contours des glyphes figurent dans les GLB). Les vignettes (`vignettes/`) et planches (`planches/`) sont des rendus de ces objets (CC0) ou de pictogrammes Commons (licence et auteur indiqués dans `catalogue.csv`).
