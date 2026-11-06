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
