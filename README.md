# 3D-Models : catalogue paramétrique des panneaux routiers français

Objets 3D (GLB) de la signalisation routière française, générés avec Blender à partir des pictogrammes officiels
(Wikimedia Commons) et mis à l'échelle selon l'IISR (instruction interministérielle sur la signalisation routière).
Ils servent de référentiel pour « mapper » la matrice réglementaire IISR (signal → vignette → objet 3D → paramètres → supports → règles).

## Contenu

| Dossier / fichier | Rôle |
|---|---|
| `panneaux/<famille>/<code>.glb` | **440 panneaux** (face −Y, mètres, repère Blender→glTF), par famille |
| `catalogue.csv`, `manifeste.json` | une ligne par panneau : dimensions, gamme, statut de la dimension, licence, auteur, source |
| `supports/` | compositions de test : poteau, potence, portique, haut-mât, mât de feu (valeurs par défaut) |
| `sources/svg/` | SVG officiels d'origine (Commons), nécessaires à la régénération |
| `scripts/` | générateurs Blender (`gen_svg.py` panneaux, `gen_support*.py` supports, `defauts_supports.json`) |
| `docs/` | registre des lots de production et mapping avec la matrice |
| `tests/`, `divers/` | essais de forme paramétrique, objets sans lien avec le catalogue |

## Familles

| Dossier | Famille | Panneaux |
|---|---|---|
| `01_A_danger` | Panneaux de danger | 29 |
| `02_AB_intersection_priorite` | Panneaux d'intersection et de priorité | 9 |
| `03_B_prescription` | Panneaux de prescription (interdiction, obligation, fin de prescription) | 104 |
| `04_C_indication` | signalisation d'indication, panneaux de type C | 51 |
| `05_CE_services` | panneaux de signalisation des services | 47 |
| `06_D_direction` | signalisation de direction, panneaux de type D | 8 |
| `07_E_identification_voirie` | Panneaux et dispositifs d'identification de voirie | 1 |
| `08_EB_entree_sortie_agglomeration` | panneaux de localisation d'entrée et de sortie d'agglomération | 2 |
| `09_J_balises` | Balises | 1 |
| `10_AK_signalisation_temporaire` | Panneaux de signalisation temporaire (AK, K, KC, KD) | 10 |
| `11_M_panonceaux` | — | 48 |
| `12_ID_ideogrammes` | idéogramme (signal de type ID) associé à une mention | 85 |
| `13_symboles/SC` | Symbole de signalisation de direction (liaison conseillée / itinéraire de contournement) | 5 |
| `13_symboles/SE` | symboles d'identification d'un échangeur ou d'une bifurcation | 3 |
| `13_symboles/SI` | symboles catégoriels d'interdiction d'une direction (catégories de véhicules) | 3 |
| `13_symboles/SU` | symboles de caractérisation d'itinéraire | 5 |
| `14_SR_information_securite` | Signalisation d'information de sécurité (panneaux de type SR) | 7 |
| `15_XA` | — | 22 |

## Structure d'un GLB

Racine = empty pivotant de 90° autour de X ; une pièce par couleur (matériaux nommés `Rouge_Panneau`, `Blanc_Retro`,
`Bleu_Panneau`, `Noir_Pictogramme`, …), plaque dorsale `Aluminium_Dos`. Propriétés personnalisées : `licence`, `auteur`, `source`,
`gamme`, `dimension_source`, `statut_dimension`, `code_iisr`.

## Statut des dimensions

- `iisr` (226) : dimension tirée des tableaux de l'IISR (partie 1, art. 14 et tableaux spécifiques).
- `provisoire` (214) : dimension par défaut en attendant l'accès aux normes ; à confirmer (champ `dimension_source`).

## Supports

Valeurs par défaut (`scripts/defauts_supports.json`) : gabarit 4,30 m avec revanches 0,10 et 0,50 m, bord inférieur 1,0 m (2,30 m en agglomération),
tubes Ø 48,3 / 60,3 / 76 mm, retrait 2,0 m (0,70 m en agglomération), massifs et platines d'après le guide Sétra (1999).
Les portées de potence/portique et sections de haut-mât sont des **hypothèses** à remplacer par les normes (NF EN 12899-1, NF P98-531, NF P98-532).

## Limites connues

- Les panneaux de direction et de texte (famille D, lot L4) ne sont pas encore générés.
- Les panneaux à valeur variable (vitesse, tonnage, distance…) ont un SVG par valeur : leurs variantes restent à produire.
- Le rendu n'est pas validé visuellement panneau par panneau.

## Régénérer

Nécessite un Blender 4.x avec le service MCP `blender-remote-mcp` : `BLENDER_MCP_URL` et `BLENDER_MCP_KEY` en variables d'environnement, puis
`python scripts/produire_lot.py items.json`.

## Licences

Voir [LICENCES.md](LICENCES.md). Le code est sous MIT ; chaque objet suit la licence de son pictogramme d'origine.
