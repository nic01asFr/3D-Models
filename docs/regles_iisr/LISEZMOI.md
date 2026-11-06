# Règles IISR pour le configurateur 3D - livraison 2 (6 novembre 2026)

Établi le 2026-11-06 par l'agent audit-iisr, à partir de `~/work/_iisr_extract/partie_1.txt` à `partie_9.txt`
(IISR, version VC_20240315 pour la partie 1). Aucune valeur n'est tirée d'une autre source.

## Méthode
- Chaque règle est choisie à la lecture du texte, puis son extrait est VÉRIFIÉ par programme : il doit figurer mot pour mot
  (espaces et apostrophes normalisés) dans la page indiquée (colonne `verifie`). Les lignes ABSENT_du_texte n'ont pas d'extrait
  (page 0) : leur absence est établie par une recherche sur les 9 parties, décrite dans `note`.
- `page` = numéro de page repéré dans l'extraction (« === PAGE n === »), identique à la pagination imprimée.
- Les tableaux aplatis par l'extraction ont été croisés avec le rendu des pages du PDF (statut `iisr_croise_pdf`) : p.10, 11, 13 (partie 1), p.47 (partie 5).
- Rien n'est déduit.

## Statuts
- `iisr` : cité dans le texte, valeur lue sans ambiguïté.
- `iisr_croise_pdf` : le texte donne l'extrait vérifié, la correspondance ligne/colonne vient du rendu de la page. Contrôle visuel seul, non programmable.
- `iisr_lu_sur_PDF` : lu seulement sur l'image d'une page (annexe I, page 41).
- `iisr_renvoi` : le texte renvoie à une règle dont le contenu n'est pas extrait ici.
- `ABSENT_du_texte` : le texte extrait ne contient pas l'information (voir `note`).
- Aucune ligne n'a le statut `hypothese`.

## Fichiers
- `regles_gammes.csv`, `regles_combinaisons.csv`, `regles_texte_alphabets.csv`, `regles_types_prioritaires.csv`, `regles_marquages.csv` (partie 7 : modulations T1 à T4, largeur unité u, tableau des lignes art. 113-2), `regles_feux.csv` (partie 6 : diamètres, hauteurs d'implantation, partiel), `regles_balises.csv` (J1, J3, J4, J5, J16 : partie 1, partiel), `regles_liseres_couleurs.csv` (formes, couleurs, listels : art. 5-1, 5-2, partie 2 art. 23, partie 4 art. 47), `regles_iisr.json`
- `couverture_catalogue.csv` : pour chacune des 909 lignes de catalogue.csv (et les types absents du catalogue), les règles trouvées et ce qui manque. Les 18 types prioritaires de pilote-cairn sont en tête (colonne `priorite`). Méthode : une règle « concerne » un code si son `objet` cite ce code ou sa famille. Les plages (ex. SR3a-SR3c3) ne sont pas dépliées : la couverture est sous-estimée là.
- `A_SOURCER_HORS_IISR.md` : ce qu'il faudrait sourcer hors IISR.

## Comptes (278 règles)
- ABSENT_du_texte : 10
- a_extraire : 1
- iisr : 243
- iisr_croise_pdf : 19
- iisr_lu_sur_PDF : 2
- iisr_renvoi : 3
(a_extraire = pas encore lu ; ABSENT_du_texte = recherche faite, rien trouvé)
Couverture du catalogue (909 lignes) : règle de gamme, forme, couleur, feux ou balises pour 549, de combinaison pour 92, de texte ou de forme pour 266 ; AUCUNE règle pour 327 lignes.

## Réponses
- Partie 8, « deux, exceptionnellement trois » : la phrase est dans les principes de concentration et de lisibilité de la signalisation temporaire (partie 8, p.16, paragraphe A). Elle ne se limite pas aux panneaux de danger, mais elle ne vaut pas pour la signalisation permanente.
- Hc : Hc = Hb sur fond clair (blanc, jaune) ; Hc = Hb + une gamme sur fond foncé (art. 83). Exceptions : H10, H20, E31, E32 (Hc = Hb) ; Dv : Hc = 40 mm (50 en présignalisation, 30 en position) ; Dc : caractères 80 ou 100 mm au-dessus de 50 km/h, 62,5 mm sinon ; E60 : 40 à 100 mm.
- Panonceaux M1 à M11 (art. 9-2) : rectangulaires ou carrés, sans listel, fond blanc (KM : jaune) ; dimensions par couples longueur x hauteur lues sur le PDF ; M12 triangulaire, côté 150 à 300 mm. La correspondance avec la gamme du panneau complété n'est pas écrite.
- Interlignes, marges, filets : AUCUNE règle dans le texte (0 occurrence de « interlign » et « filet »). Si elles existent, elles sont dans les annexes dessinées.
- Gabarits par type : D, Da, E, EB, H, Dv, Dc, E60 sont dimensionnés à partir de Hc ; leur dimension est choisie dans les tables de l'art. 5-3 (D, Da, E, EB, KD, D29, Dp, Dv, Dc) ou n'est pas prédéfinie (H, E, EB, D, Da). Non extraits : XA, XB, XM (partie 9), gabarits de composition de chaque panneau D (dessins des annexes 8 à 15 de la partie 5).

- Listels, couronnes, bandes : les COULEURS sont écrites (danger, B), AUCUNE LARGEUR n'est donnée dans le texte (ni rayon d'arrondi). Couleurs de fond de AB et C : non écrites dans un article.
- Annexes 8 à 15 de la partie 5 (D20 à D60) : photographies d'exemples sans cote.

## Limites
- Lecture limitée au corpus IISR. Guide Cerema 2017 et NF EN 12899 : non lus.
- Annexes dessinées (partie 5, annexes 8 à 26 ; partie 1, annexe I pages 42 à 47) : non lues, sauf la page 41.
- Parties 6, 7, 8 (hors p.16), 9 : seulement les passages repérés par mot-clé.
