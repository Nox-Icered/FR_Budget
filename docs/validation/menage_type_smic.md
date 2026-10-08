# Ménage type « célibataire au SMIC » : OpenFisca contre le modèle Urssaf

Tâche 0.2 du plan. Rapport du 7 octobre 2026.

## Méthode

- **Moteur** : OpenFisca-France 176.1.2, adaptateur `moteur/src/fr_budget/menages/openfisca.py`, avec les corrections de `registres/corrections_openfisca.yaml` (voir plus bas).
- **Référence** : modèle de calcul de mon-entreprise.urssaf.fr, paquet npm `modele-social` 11.1.0 (publicodes 1.10.3, licence MIT), exécuté localement par `outils/references_urssaf/generer.mjs`. Le site de l'Urssaf et celui des impôts ne sont pas joignables depuis l'environnement de développement.
- **Cas** : salarié célibataire non cadre, CDI à temps plein, payé au SMIC, en janvier et juillet 2026.
- **Hypothèses non fixées par la loi** : valeurs par défaut du modèle Urssaf, relues dans le modèle et écrites dans `registres/references/menages/urssaf_modele_social.json`. Effectif de 4 salariés, taux AT/MP de 2,08 % (taux moyen du modèle Urssaf), mutuelle de 40 €/mois payée à 50 % par l'employeur, ou pas de mutuelle.
- **Entrée commune** : OpenFisca reçoit le salaire brut calculé par le modèle Urssaf.
- **Tolérance** : 0,50 € par mois et par ligne (validée le 7 octobre 2026).

## Résultats

| Cas | Ligne | OpenFisca publié (€) | OpenFisca corrigé (€) | Urssaf (€) | Écart corrigé (€) | Statut |
|-----|-------|------|------|------|------|------|
| Janvier 2026, sans mutuelle | Brut | 1823,03 | 1823,03 | 1823,03 | 0,00 | OK |
|  | Coût employeur | 1878,39 | 1879,30 | 1879,29 | +0,01 | OK |
|  | Net avant impôt | 1443,10 | 1443,10 | 1443,11 | −0,01 | OK |
|  | Net imposable | 1495,05 | 1495,05 | 1495,05 | −0,01 | OK |
| Janvier 2026, mutuelle 40 € | Brut | 1823,03 | 1823,03 | 1823,03 | 0,00 | OK |
|  | Coût employeur | 1898,39 | 1899,30 | 1899,29 | +0,01 | OK |
|  | Net avant impôt | 1421,16 | 1421,16 | 1421,17 | −0,01 | OK |
|  | Net imposable | 1473,69 | 1493,69 | 1493,69 | −0,01 | OK |
| Juillet 2026, sans mutuelle (référence corrigée) | Brut | 1867,02 | 1867,02 | 1867,02 | 0,00 | OK |
|  | Coût employeur | 1966,82 | 1967,76 | 1967,76 | 0,00 | OK |
|  | Net avant impôt | 1477,93 | 1477,93 | 1477,93 | 0,00 | OK |
|  | Net imposable | 1531,12 | 1531,12 | 1531,12 | 0,00 | OK |

Bilan : 12 comparaisons sur 12 dans la tolérance avec les corrections ; 4 sur 12 avec OpenFisca tel que publié.

## Écarts trouvés et décisions

Les sources primaires (Légifrance, BOFiP, urssaf.fr, site de l'AGS) n'étaient pas joignables. Les décisions s'appuient sur des sources secondaires trouvées par recherche web, recoupées avec les journaux de modifications d'OpenFisca et du modèle Urssaf. Elles sont à confirmer sur les textes primaires.

### 1. Taux de la cotisation AGS : OpenFisca corrigé

- Constat : −0,90 € sur le coût employeur au SMIC. OpenFisca retient 0,20 % depuis le 1er janvier 2024 (dernière vérification notée dans le paramètre : 14 mars 2024) ; le modèle Urssaf 0,25 % depuis juillet 2024.
- Sources : communiqué de l'AGS du 18 juin 2024 annonçant le passage de 0,20 % à 0,25 % au 1er juillet 2024 (cité par Legisocial, Previssima, éditions Tissot) ; règle du modèle Urssaf.
- Décision : le paramètre d'OpenFisca est périmé. Correction `taux_ags_2024_07` du registre.

### 2. Part patronale de la mutuelle dans le net imposable : OpenFisca corrigé

- Constat : −20,01 € sur le net imposable, soit la part patronale de la mutuelle. OpenFisca déduit la part salariale du salaire imposable mais n'y ajoute pas la part patronale.
- Sources : depuis l'imposition des revenus 2013 (loi de finances pour 2014), la part patronale finançant une complémentaire santé collective et obligatoire est imposable pour le salarié (article 83 du CGI, BOFiP) ; règle du modèle Urssaf.
- Décision : correction `mutuelle_part_patronale_imposable` du registre. OpenFisca calcule le salaire net à partir du salaire imposable : la correction ajoute la part patronale au salaire imposable et la retire du salaire net, pour que le net avant impôt ne change pas.

### 3. SMIC de référence de la réduction générale en juillet 2026 : référence Urssaf corrigée

- Constat : +42,19 € sur le coût employeur en juillet 2026. Le SMIC horaire passe de 12,02 € à 12,31 € au 1er juin 2026.
- Sources : le décret n° 2026-509 du 12 juin 2026 (JO du 14 juin) maintient, pour la réduction générale dégressive unique de 2026, le SMIC du 1er janvier 2026, soit 12,02 € (cité par GHR, FFB, Legisocial, FHF, service-public.gouv.fr). OpenFisca 176.1.2 applique ce décret. Le modèle Urssaf 11.1.0 ne l'applique pas, mais sa version suivante le corrige (journal des modifications de `modele-social`, section « next » : « Utilisation du Smic au 1er janvier 2026 dans les calculs de la RGDU et de la Lodeom »).
- Décision : OpenFisca est juste ; c'est la référence qui est en retard. Le générateur applique au cas de juillet la correction annoncée par l'Urssaf (SMIC du début d'année pour ce calcul) et l'indique dans le champ `correction_appliquee` du fichier de référence. À retirer quand une version de `modele-social` qui l'intègre sera publiée.

### Convention d'heures (sans effet sur les tests)

Le SMIC mensuel diffère de 0,04 € : OpenFisca compte 151,67 heures, le modèle Urssaf 35 × 52 / 12 heures. Les tests neutralisent cet écart en donnant à OpenFisca le brut de l'Urssaf. Pour nos ménages types, il faudra choisir une convention.

## Signalements à faire en amont

- OpenFisca-France : taux AGS (écart 1) et part patronale de la mutuelle dans `salaire_imposable` (écart 2).
- Rien à signaler à l'Urssaf : l'écart 3 est déjà corrigé dans leur dépôt.

## Pas encore fait

- **Net après impôt** (impôt sur le revenu, prime d'activité) : la référence officielle est le simulateur d'impots.gouv.fr et celui de la CAF, injoignables d'ici. Il faut soit des cas saisis à la main dans ces simulateurs, soit une autre référence publiée.
- **Autres ménages types** : le salaire médian et ses multiples demandent une source INSEE à déposer dans le registre.
