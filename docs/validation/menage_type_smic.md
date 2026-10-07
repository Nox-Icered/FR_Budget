# Ménage type « célibataire au SMIC » : OpenFisca contre le modèle Urssaf

Tâche 0.2 du plan. Rapport du 7 octobre 2026.

## Méthode

- **Moteur** : OpenFisca-France 176.1.2, adaptateur `moteur/src/fr_budget/menages/openfisca.py`.
- **Référence** : modèle de calcul de mon-entreprise.urssaf.fr, paquet npm `modele-social` 11.1.0 (publicodes 1.10.3, licence MIT), exécuté localement par `outils/references_urssaf/generer.mjs`. Le site de l'Urssaf et celui des impôts ne sont pas joignables depuis l'environnement de développement.
- **Cas** : salarié célibataire non cadre, CDI à temps plein, payé au SMIC, en janvier et juillet 2026.
- **Hypothèses non fixées par la loi** : valeurs par défaut du modèle Urssaf, relues dans le modèle et écrites dans `registres/references/menages/urssaf_modele_social.json`. Effectif de 4 salariés, taux AT/MP de 2,08 % (taux moyen du modèle Urssaf), mutuelle de 40 €/mois payée à 50 % par l'employeur, ou pas de mutuelle.
- **Entrée commune** : OpenFisca reçoit le salaire brut calculé par le modèle Urssaf.
- **Tolérance** : 0,50 € par mois et par ligne (proposée, à valider).

## Résultats

| Cas | Ligne | OpenFisca (€) | Urssaf (€) | Écart (€) | Statut |
|-----|-------|---------------|------------|-----------|--------|
| Janvier 2026, sans mutuelle | Brut | 1 823,03 | 1 823,03 | 0,00 | OK |
| | Coût employeur | 1 878,39 | 1 879,29 | −0,90 | Échec |
| | Net avant impôt | 1 443,10 | 1 443,11 | −0,01 | OK |
| | Net imposable | 1 495,05 | 1 495,05 | −0,01 | OK |
| Janvier 2026, mutuelle 40 € | Brut | 1 823,03 | 1 823,03 | 0,00 | OK |
| | Coût employeur | 1 898,39 | 1 899,29 | −0,90 | Échec |
| | Net avant impôt | 1 421,16 | 1 421,17 | −0,01 | OK |
| | Net imposable | 1 473,69 | 1 493,69 | −20,01 | Échec |
| Juillet 2026, sans mutuelle | Brut | 1 867,02 | 1 867,02 | 0,00 | OK |
| | Coût employeur | 1 966,82 | 1 924,63 | +42,19 | Échec |
| | Net avant impôt | 1 477,93 | 1 477,93 | 0,00 | OK |
| | Net imposable | 1 531,12 | 1 531,12 | 0,00 | OK |

Bilan : 8 comparaisons sur 12 dans la tolérance, 4 hors tolérance.

Le détail exact de chaque écart est imprimé par `uv run pytest -m validation` dans `moteur/`.

## Écarts expliqués

### 1. Taux de la cotisation AGS (−0,90 € sur le coût employeur)

- OpenFisca : 0,20 % depuis le 1er janvier 2024. Le paramètre indique une dernière vérification au 14 mars 2024.
- Modèle Urssaf : 0,25 % depuis juillet 2024.
- Lecture probable : le paramètre OpenFisca n'a pas été mis à jour. À confirmer sur la fiche Urssaf de la cotisation AGS ; si c'est confirmé, signaler l'écart au projet OpenFisca-France.

### 2. Part patronale de la mutuelle dans le net imposable (−20,01 €)

- L'écart est égal à la part employeur de la mutuelle (20 €).
- Modèle Urssaf : la part patronale de la complémentaire santé collective est ajoutée au net imposable.
- OpenFisca : elle ne l'est pas.
- À trancher sur le texte fiscal applicable (code général des impôts) avant de choisir. Aucune des deux lectures n'est retenue pour l'instant.

### 3. SMIC de référence de la réduction générale en juillet 2026 (+42,19 € sur le coût employeur)

- Le SMIC horaire passe de 12,02 € à 12,31 € au 1er juin 2026 (paramètre OpenFisca, arrêté du 22 mai 2026).
- OpenFisca calcule la réduction générale de 2026 avec un SMIC de référence figé à 12,02 €, en citant le décret n° 2026-509 du 12 juin 2026. Au SMIC de juillet, le salaire dépasse ce SMIC de référence et la réduction baisse.
- Modèle Urssaf (paquet publié le 16 juillet 2026) : la réduction utilise le SMIC en vigueur à la date du calcul.
- L'écart restant (42,19 € au lieu d'environ 43 €) inclut l'écart AGS.
- À trancher sur le texte du décret du 12 juin 2026. C'est l'écart le plus important pour le ménage type au SMIC.

### Convention d'heures (sans effet sur les tests)

Le SMIC mensuel diffère de 0,04 € : OpenFisca compte 151,67 heures, le modèle Urssaf 35 × 52 / 12 heures. Les tests neutralisent cet écart en donnant à OpenFisca le brut de l'Urssaf. Pour nos ménages types, il faudra choisir une convention.

## Pas encore fait

- **Net après impôt** (impôt sur le revenu, prime d'activité) : la référence officielle est le simulateur d'impots.gouv.fr et celui de la CAF, injoignables d'ici. Il faut soit des cas saisis à la main dans ces simulateurs, soit une autre référence publiée.
- **Autres ménages types** : le salaire médian et ses multiples demandent une source INSEE à déposer dans le registre.
