# web/ — moteur de composition et de rendu des panneaux de direction (JS)

Port JavaScript des règles de `scripts/dir_regles.py` et `scripts/composition.py` (IISR 5e partie, art. 81 C, 81-1, 83), pour l'outil de validation Panoramax : afficher le panneau reconnu, et le recomposer à partir de ce que l'OCR a lu.

| Fichier | Rôle |
|---|---|
| `signrender.js` | module UMD (navigateur et Node) : `composer`, `geometrie`, `renderSVG`, `corriger`, `valider`, `hb`, `hc`, `fmtDistance`, `textWidth` |
| `fontmetrics.json` | avances de glyphes (upm 1000, hauteur de capitale 733) pour la largeur des textes |
| `ref.json` | résultats de référence produits par le code Python (17 cas) |
| `test.js` | parité JS/Python, performance, scénarios « lecture OCR » (`node web/test.js`) |
| `render_test.js` | écrit des SVG et une planche `sheet.html` pour contrôle visuel |
| `demo.tpl.html`, `build_demo.js` | éditeur interactif ; `node web/build_demo.js` produit `demo.html` autonome |

## Usage

```js
const S = require('./signrender.js');
S.setFontMetrics(require('./fontmetrics.json'));
const { comp, errors } = S.composer(spec);   // ne lève pas : errors liste les non-conformités
const { spec: corrigee, log } = S.corriger(spec);  // reclasse blocs et distances
const { svg, warn } = S.renderSVG(comp, S.geometrie(comp));
```

`spec` : `{type, contexte:{reseau, vitesse, support, eloignement_m, presignal}, registres:[{fond, fleche, voies, sortie, mentions:[{texte, pole, distance_km, local}]}]}`.

## État des tests

- Parité avec le Python : 17 cas identiques (hauteurs, casse, distances, largeurs, erreurs).
- Performance : environ 0,03 ms par panneau (composition, géométrie et SVG).
- Lecture OCR : blocs inversés et distances croissantes corrigés automatiquement ; D21b lu avec distance et vitesse hors table signalés, non corrigés.

## Limites et hypothèses

- Seuls Hb et Hc viennent de l'IISR. Hauteur de registre, marges, largeur de flèche et liseré sont des **hypothèses** (`HYP`) : NF P98-532 et Sétra n'ont pas été consultés.
- Police de substitution (Source Sans 3 / Noto Sans) ; les largeurs sont calées sur les métriques de `fontmetrics.json`.
- Périmètre : panneaux de direction composés par règles (famille D). Restent à porter : disques à valeur (B14), panonceaux textuels (M9), schémas (carrefour, giratoire).
- Défaut connu côté pipeline Blender : l'apostrophe typographique ’ a une avance de 1000 dans Noto Sans CJK ; le JS la normalise en `'`.
