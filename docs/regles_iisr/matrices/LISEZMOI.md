# Matrices du configurateur (format long : une ligne = une relation)

Colonnes : source, relation, cible, condition, valeur_unite, article, page, partie, extrait, statut, id_regle (renvoi à ../regles_iisr.json).
Statuts : iisr, iisr_croise_pdf, iisr_lu_sur_PDF, iisr_renvoi, ABSENT_du_texte. Une ligne ABSENT_du_texte = choix non encadré par l'IISR
(à proposer, jamais refusé ni validé). Les extraits de ces matrices sont vérifiés mot pour mot dans la page citée.

- M4_panneau_gammes.csv (58 lignes) : {'iisr_croise_pdf': 38, 'iisr': 20}
- M1_panneau_panonceaux.csv (64 lignes) : {'iisr': 61, 'iisr_renvoi': 2, 'ABSENT_du_texte': 1}
- M2_supports.csv (20 lignes) : {'iisr': 17, 'ABSENT_du_texte': 3}
- M3_panneau_meme_support.csv (25 lignes) : {'iisr': 24, 'ABSENT_du_texte': 1}
- matrices.json : les quatre ensembles.

## Limites
- M1 : liste les panonceaux dont le texte limite l'emploi (M1, M2, M4, M6, M8, M10, M11, KM1, KM2) et les cas nommés (M3a, M3b, M3d, M12, M9b/M9z sur A9b, M9c sur AB3a, M6a, M4d1). M9 n'est pas restreint par le texte. M5 et M7 : renvois non extraits (art. 35 C, 42-2 F, 42-5). Les panonceaux admis par les articles des parties 2 à 5 pour chaque panneau ne sont pas tous lus : M1 est incomplète par construction.
- M2 : seules les sections de supports d'accotement, hauteurs et retraits sont dans l'IISR ; portée des potences et portiques, section des hauts-mâts, table panneau-support : ABSENT du texte. E030, E066, E073, E077 cités dans la demande n'ont pas été lus.
- M3 : ordre vertical et même support du texte ; l'exclusivité de AB3a et AB4 (art. 8) y figure ; aucun nombre maximal de panneaux par support en signalisation permanente ; « deux, exceptionnellement trois » = signalisation temporaire seulement (partie 8 p.16).
- M4 : voir regles_gammes.csv ; pour les panonceaux M1 à M11, la correspondance avec la gamme du panneau complété n'est pas écrite.

## M1c - verdicts phrase a phrase (complement de M1b, M1b inchange)

- `M1c_panonceaux_verdicts.csv` : les 190 lignes de M1b, chacune avec `verdict`, `modalite`, `condition_emploi`, `article`.
  - `admis` : la phrase rattache ce panonceau a ce panneau (130). `admis_conditionnel` : idem, sous la condition de `condition_emploi` (22).
  - `non_etabli` : la phrase cite le panonceau mais le rattache a un autre panneau (36). `indetermine` : la phrase ne permet pas de trancher (2 : AB6-M7 sans code du panonceau-schema ; B6b-M6b cite apres « ainsi que »).
  - Les 97 lignes `phrase_multiple` et les 4 lignes `negation_ou_exception` ont ete lues une a une (colonne `origine_m1b`). Les 93 lignes `univoque` sont `admis`, `modalite` = mot repere dans la phrase par expression reguliere (peut vide).
  - `article` : dernier titre « Article N » qui precede la phrase dans le texte extrait (deduction mecanique, pas lue sur la page : a controler si une decision en depend).
  - Une liste introduite par « par exemple » (B6a1/2/3) est notee non exhaustive. Generateur : `_gen_M1c.py` (lance depuis matrices/, verdicts ecrits a la main dans le script).
- `M1c_panonceaux_distance_sans_code.csv` : phrases des parties 3 ou le « panonceau de distance » est cite sans code M, rapproche de M1 par l'equivalence que le texte nomme (« panonceau de distance M1 », partie 4 p.7 et p.28). 17 lignes (AB7 avec ; AB1/AB2 sans en regle generale ; AB7 sans dans le cas ou le texte l'ecarte). Colonne `source` = `indetermine` quand la phrase designe les panneaux par « ces panneaux ». Generateur : `_gen_M1c_sans_code.py`.
- Non traite : panonceaux d'etendue/categorie/directionnel sans code M dans une phrase avec un panneau A/AB/B/C : le balayage n'en trouve aucun hors « panonceaux complementaires » de B6a1/2/3 (deja dans M1c). Panonceaux de parties 6 a 9 non couverts.
