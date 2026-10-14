# Plan de développement

Ce plan découle de `CLAUDE.md` et de `docs/specification.md`. Il découpe le travail en lots livrables un par un. Une phase ne commence que lorsque la porte de la précédente est franchie.

Aucun chiffre n'apparaît dans ce plan : les valeurs viendront des registres, avec leur source.

## 0. État des lieux (7 octobre 2026)

- Le dépôt `Nox-Icered/FR_Budget` est vide. Les seuls documents sont `CLAUDE.md` et la spécification, désormais dans `docs/`.
- Environnement : Python 3.11, 3.12 et 3.13 disponibles, Node 22, `uv`, `pandoc`.
- `openfisca-france` est disponible sur PyPI en version 176.1.2 (dépend de `openfisca-core` ≥ 43, < 45). La résolution des dépendances passe sous Python 3.13 ; l'installation réelle et un premier calcul restent à faire (tâche 0.2).

## 1. Décisions

Validées le 7 octobre 2026, sauf D7 (en attente).

| # | Question | Choix | Pourquoi |
|---|----------|------------------------|----------|
| D1 | Licence du code | AGPL-3.0 | OpenFisca-France est sous AGPL-3.0 (vérifié dans les métadonnées du paquet 176.1.2) ; une API publique qui l'utilise doit rester compatible. |
| D2 | Licence des données et registres produits | Licence Ouverte Etalab 2.0 | Même licence que la plupart des sources publiques françaises ; chaque source garde sa propre licence dans le registre. |
| D3 | Version de Python | 3.12 | Plus éprouvée avec l'écosystème scientifique ; passage en 3.13 quand la CI le confirme. |
| D4 | Gestionnaire de paquets Python | `uv` avec `pyproject.toml` et fichier de verrouillage | Rapide, reproductible, un seul outil. |
| D5 | Gestionnaire de paquets front | `pnpm` | Monorepo léger, verrouillage strict. |
| D6 | Format des registres | YAML relu à la main, compilé en Parquet par script | Lisible dans une revue de code, validé par schéma (pydantic). |
| D7 | Nom du projet et domaine | à choisir | Point ouvert de la spécification. |

## 2. Structure du dépôt

```
FR_Budget/
├── CLAUDE.md
├── LICENSE
├── README.md
├── docs/
│   ├── specification.md
│   ├── plan.md
│   ├── fiches/                  # une fiche par levier ou module
│   │   └── _modele.md
│   ├── methodologie.md
│   └── relecteurs.md
├── registres/
│   ├── sources.yaml             # entité source
│   ├── datasets.yaml            # entité dataset (hash, méthode)
│   ├── hypotheses.yaml          # entité assumption
│   ├── leviers.yaml             # entité lever (statut de validation)
│   └── references/              # chiffrages officiels saisis, par levier et millésime
├── data/
│   ├── raw/                     # fichiers tels que téléchargés (gitignorés si lourds, hash au registre)
│   └── processed/               # Parquet produits par les scripts
├── pipelines/                   # extraction et transformation rejouables
├── moteur/                      # paquet Python `fr_budget`
│   ├── pyproject.toml
│   ├── src/fr_budget/
│   │   ├── registres/           # chargement et validation des registres (pydantic)
│   │   ├── fourchette.py        # type Fourchette(bas, central, haut)
│   │   ├── menages/             # adaptateur OpenFisca, ménages types, cascade salaire
│   │   ├── agrege/              # un fichier par levier paramétrique
│   │   ├── structurels/         # retraites, puis lot 1 V2
│   │   ├── entreprises/
│   │   ├── agregation.py        # ΔPB par année et par sous-secteur APU
│   │   ├── baseline.py
│   │   ├── dette.py
│   │   └── croissance.py        # multiplicateur, désactivé par défaut
│   └── tests/
│       ├── unitaires/
│       └── validation/          # un test par levier et par millésime de référence
├── api/                         # FastAPI, sans état
├── web/                         # Next.js, TypeScript
│   └── messages/fr.json         # tous les textes affichés
└── .github/workflows/
```

Choix structurants :

- Le moteur est un paquet Python indépendant de l'API : on peut le tester, l'auditer et le réutiliser sans serveur.
- Les calculs sont des fonctions pures qui reçoivent les registres en paramètre. Pas de constante dans le code.
- Le type `Fourchette` est imposé dans toutes les signatures de résultat : un résultat à valeur unique ne compile pas au contrôle de types.
- `data/raw/` garde les fichiers d'origine. S'ils sont trop lourds ou si leur licence l'interdit, seul le hash et l'URL sont committés, et le script de téléchargement les récupère.
- Les micro-données d'enquête sont bloquées par `.gitignore` et par un contrôle en CI.

## 3. Phase 0 : cadrage

Porte 0 : prototype TVA reproduisant le chiffrage officiel à ±10 % sur deux millésimes, présenté à un premier relecteur.

Décision du 8 octobre 2026 : le prototype TVA est clos au statut bêta sans avoir franchi la porte au niveau de chaque taux (10 comparaisons sur 17 dans la tolérance, détail dans `docs/validation/levier_tva.md`). Le passage à la phase 1 est décidé par le mainteneur malgré ces écarts, qui restent publiés. La présentation à un premier relecteur reste à faire.

| Tâche | Contenu | Terminé quand |
|-------|---------|---------------|
| 0.1 Socle du dépôt | Licence, README, structure ci-dessus, `pyproject.toml`, ruff, mypy strict, pytest, pre-commit, CI qui lance lint et tests. | La CI passe sur une branche vide de calcul. |
| 0.2 OpenFisca | Installer OpenFisca-France, charger le système une fois, écrire l'adaptateur. Lister depuis le paquet installé les noms exacts des variables utiles (salaire de base, cotisations, CSG, IR, prime d'activité…) dans `docs/variables_openfisca.md`. | Un célibataire au SMIC est calculé ; les résultats sont comparés au simulateur Urssaf et au simulateur impots.gouv.fr ; les cas de test sont publiés avec la date de consultation. |
| 0.3 Registres | Schémas pydantic des entités `source`, `dataset`, `assumption`, `lever`, `validation_test`. Script qui valide les YAML et refuse toute valeur sans source. | Un registre invalide fait échouer la CI. |
| 0.4 Chiffrages de référence | Pour les 12 leviers, saisir les chiffrages officiels des trois derniers PLF (Voies et Moyens et annexes), avec page et tableau cités. | `registres/references/` complet ou, pour chaque trou, la raison écrite. Liste soumise à ta relecture. |
| 0.5 Prototype TVA | Pipeline : données de consommation par taux (comptes nationaux), assiette, rendement d'une variation de taux. Test de validation écrit avant le code. | Écart publié pour chaque millésime ; statut validé ou bêta selon la règle. |
| 0.6 Fiche de levier | Modèle de fiche (questions, formule, données, hypothèses, validation, limites) ; fiche TVA remplie ; premier registre d'hypothèses. | Fiche TVA relisible par un tiers sans lire le code. |
| 0.7 Relecteurs | Liste de 5 à 10 personnes (communauté OpenFisca, IPP, OFCE, économistes des finances publiques) avec le contact public. | `docs/relecteurs.md` écrit ; premier envoi fait par toi. |

Ordre : 0.1, puis 0.2 et 0.3 en parallèle, puis 0.4, 0.5, 0.6. La tâche 0.7 ne dépend de rien.

Ce que je ne peux pas faire seul :

- Les téléchargements depuis budget.gouv.fr, l'INSEE ou l'AFT peuvent être bloqués par le réseau de cet environnement. Si c'est le cas, je te demanderai de déposer les fichiers.
- Les chiffrages de référence (0.4) sont des valeurs saisies : tu les relis une par une.

## 4. Phase 1 : socle

Porte 1 : baseline et dynamique de la dette relues par deux relecteurs indépendants.

1. Données APU : comptes des APU de l'INSEE (recettes, dépenses COFOG, solde, dette, intérêts) par sous-secteur, en pipeline rejouable.
2. Baseline N à N+20 : croissance réelle, inflation, taux, démographie, retraites COR, santé. Chaque entrée est une hypothèse avec plage. Scénarios bas, central, haut.
3. Dette : `d(t+1) = d(t)·(1+r)/(1+g) − pb + sfa`, avec un taux apparent calculé à partir du profil de maturité (part refinancée chaque année au taux de marché). Tests sur des cas analytiques (r = g, pb = 0…) puis reproduction de la trajectoire officielle de référence.
4. API minimale : `GET /baseline`, `POST /scenario` (sans levier pour l'instant), `GET /registres/*`.
5. Front : squelette Next.js, textes dans `messages/fr.json`, page d'accueil APU, pages Méthodologie, Sources, Hypothèses, Validation générées depuis les registres.
6. CI : tests de validation à chaque modification de `moteur/`, `registres/` ou `data/`, avec publication du tableau d'écarts.

## 5. Phase 2 : leviers

Décision du 9 octobre 2026 : la phase 2 commence avant le franchissement de la porte 1. La relecture de la baseline et de la dynamique de la dette par deux relecteurs indépendants est reportée ; la baseline reste affichée « bêta, non validé » et les valeurs saisies restent « à relire » jusque-là.

Porte 2 : 12 leviers validés ou affichés en bêta avec écart publié.

Un levier par branche, dans cet ordre indicatif (des références les plus solides aux plus délicates) :

1. TVA (déjà fait en phase 0, intégré à l'agrégation)
2. Accises et taxes énergie
3. Impôt sur les sociétés
4. Niches fiscales (catalogue Voies et Moyens, tome 2)
5. Crédits par mission
6. Dotations aux collectivités
7. Rémunérations publiques
8. Indexation des pensions et prestations
9. CSG
10. Cotisations patronales
11. Impôt sur le revenu
12. Minima et prime d'activité

Pour chaque levier, la même suite : test de validation écrit d'abord, calcul, comparaison avec une source indépendante, fiche, libellé neutre relu, statut dans `leviers.yaml`.

En parallèle :

- Ménages types : les 8 profils de la spécification, cascade coût employeur, brut, net avant impôt, net après impôt, avant et après. Réglage d'incidence des cotisations patronales, les deux lectures affichées. Profil saisi par l'utilisateur calculé sans stockage ni journalisation (contrôle de la configuration des logs en test).
  - Première partie faite le 13 octobre 2026 (`docs/fiches/menages_types.md`, choix à relire) : 5 profils salariés (SMIC, médiane et 95e centile de l'Insee, couple avec deux enfants, parent seul), cascade jusqu'au net après impôt et prestations, sans réforme ; impôt validé contre le simulateur officiel d'impots.gouv.fr (5 sur 5, à 1 € près).
  - Prestations validées contre les barèmes publiés le 13 octobre 2026 ; cas du simulateur officiel de la prime d'activité en attente (service des communes indisponible).
  - Apprenti ajouté le 13 octobre 2026, avec trois corrections d'OpenFisca (exonérations de 2025).
  - Retraité ajouté le 13 octobre 2026 (pension moyenne de la DREES, la médiane n'étant pas publiée).
  - Artisan ajouté le 13 octobre 2026 (assiette réformée de 2025, décret n° 2024-688 et pages de l'Urssaf déposés par le mainteneur) : les huit profils de la spécification sont couverts.
  - Profil saisi par l'utilisateur ajouté le 13 octobre 2026 : page « Mon ménage », calcul par `POST /mon-menage`, sans stockage ni journal (test du journal de l'API). La page attend l'hébergement de l'API.
  - Effet des leviers sur les ménages types ajouté le 13 octobre 2026 : 7 leviers traduits en réformes d'OpenFisca, hausse et baisse d'une unité publiées sur la page Ménages types ; pension du retraité non chiffrée pour l'indexation (source manquante).
  - Réglage d'incidence ajouté le 13 octobre 2026 : lectures comptable (par défaut) et répercutée sur le salaire, qui bornent l'effet des cotisations patronales et des allègements.
  - Scénario de plusieurs leviers calculé le 13 octobre 2026 (moteur et API) pour les ménages types et le ménage saisi.
  - Effet du scénario affiché le 13 octobre 2026 : panneau du simulateur (approximation sur grille, écart au calcul complet publié : 61 € pour une mesure seule, 291 € pour toutes les mesures à leurs bornes) et page « Mon ménage » (calcul complet, quand l'API sera hébergée).
- Indicateur de dépense incompressible pour TVA et accises (budgets de famille INSEE).
  - Fait le 14 octobre 2026 (`docs/fiches/depense_menages.md`, choix à relire) : dépense supplémentaire à consommation inchangée pour les mesures de TVA (taux normal) et d'accises, par décile de niveau de vie et par type de ménage (enquête Budget de famille 2017, prix des carburants du SDES), dans le panneau du simulateur. Part de la consommation au taux normal confrontée aux comptes nationaux (écarts de −1,4 % et −0,1 %).
- Entreprises : charge par taille et secteur (ESANE, DGFiP), sans effet comportemental.
  - Fait le 14 octobre 2026 (`docs/fiches/entreprises.md`, choix à relire) : quatre leviers (taux de cotisation patronale, allègements, taux normal et surtaxe de l'impôt sur les sociétés) répartis selon les données de l'Urssaf (open data, ODbL) et de la DGFiP, plutôt qu'ESANE, qui ne publie ni cotisations ni impôt par classe ; page Entreprises et panneau du simulateur. Données de l'Urssaf confrontées à la CCSS (écarts de +0,3 % et −4,1 %).
- Écrans Catalogue, Simulateur, Ménages, Entreprises, « Comment c'est calculé ? ».

## 6. Phase 3 : V1

Porte 3 : mise en ligne avec tests et écarts publics.

Décision du 12 octobre 2026 : la phase 3 commence avant le franchissement de la porte 2. Les 12 leviers sont affichés en bêta avec leurs écarts publiés, mais aucun n'a encore été confronté à une source indépendante ; les ménages types, les entreprises et l'indicateur de dépense incompressible restent à faire. La phase 3 est conduite en autonomie (instruction du mainteneur), lot par lot, avec les choix et leurs conséquences consignés ci-dessous et dans chaque PR.

1. Module retraites : modèle de cohortes calé sur les projections du COR, démographie INSEE, validation contre les variantes publiées par le COR.
   - Première étape faite au lot 3.1 (choix à relire, `docs/fiches/retraites.md`) : pas de modèle de cohortes. Un levier « âge effectif moyen de départ » (de −1 à +3 ans), dont l'effet annuel vient de l'abaque du COR (rapport de juin 2026, figure 2.24) ; montée en charge en 4 ans.
   - Conséquences : effet mécanique, sans effets sur l'emploi ni autres dépenses sociales. Confronté au tableau 2.10 du COR (simulations de la DG Trésor, d'I-MIP et de l'OFCE pour un an d'âge légal), le modèle est au-dessus de la fourchette publiée à 2, 10 et 20 ans, de +20 % à +860 % selon l'horizon et la borne ; il reste en bêta.
   - Reste à faire : modèle de cohortes (âge légal, durée de cotisation, taux de remplacement), lien entre âge légal et âge effectif, Cour des comptes.
2. Interrupteur de croissance : multiplicateur par instrument et décroissant dans le temps, valeurs et plages sourcées, désactivé par défaut, effet retour par l'élasticité des prélèvements.
   - Fait au lot 3.2 (choix à relire, `docs/fiches/croissance.md`) : modèle simple de l'OFCE (Policy brief n° 146) ; multiplicateur central tiré de Mésange 2017 (Insee et DG Trésor), plage jusqu'aux valeurs de l'OFCE ; persistance 0,7 et effet sur le solde 0,5, sans plage (une seule source).
   - Conséquences : effet transitoire, sans effets d'offre de long terme ; résultat central plutôt bas dans la plage des multiplicateurs ; données du site environ 2,7 fois plus lourdes.
3. Scénarios partagés : PostgreSQL, identifiant court, version du modèle et des données enregistrées avec le scénario.
   - Choix fait en autonomie (lot 3.3, à relire) : **pas de PostgreSQL**. Le scénario tient entièrement dans l'adresse de la page (paramètres `a`, `v`, `l`, `i`, `d`, `m`, `web/lib/etat.ts`) et le calcul se refait dans le navigateur.
   - Conséquences : aucun scénario n'est stocké sur un serveur, le site reste statique et sans état (pas de base à héberger ni à sauvegarder) ; en contrepartie le lien est long et n'a pas d'identifiant court.
   - Limite : le lien porte l'empreinte de la version (moteur, registres, données) mais pas les données elles-mêmes. Après une mise à jour du site, il est recalculé avec la nouvelle version et un avertissement le signale ; il ne reproduit donc le même résultat que tant que la version déployée est la même. Garder chaque version en ligne (archives par version) reste à faire au lot 3.6.
   - Un lien illisible, hors bornes ou qui combine des mesures refusées par le moteur (double compte) n'est pas chargé ; un message le dit.
4. Comparaison de 2 à 3 scénarios, export CSV et JSON.
   - Choix (lot 3.4) : la page Comparer reçoit 2 à 3 liens du simulateur et affiche côte à côte l'écart de solde primaire, l'écart de dette et la dette, en fourchette ; son adresse porte les scénarios (`s1` à `s3`).
   - Exports : toutes les années, en points de PIB, valeurs basse, centrale et haute ; le JSON ajoute les réglages, le lien et la version complète. Séparateur `;` et point décimal dans le CSV.
5. Pages Journal et Relectures ; mentions légales.
   - Fait au lot 3.5 (choix à relire) :
     - le journal est tiré des sections « Journal » des fiches (une seule source, rien à recopier) ;
     - les relectures externes ont leur registre (`registres/relectures.yaml`, vide à ce jour), publié tel quel ; la page montre aussi combien de valeurs saisies restent « à relire » ;
     - les mentions légales laissent l'éditeur et l'hébergeur « à compléter ». Ces informations ne peuvent pas être inventées : **à fournir par le mainteneur** avant la mise en ligne.
6. Accessibilité (RGAA visé), mobile, cache des scénarios courants, hébergement.
   - Fait au lot 3.6 (première partie) :
     - contrôle automatique axe-core (WCAG 2.0 A et AA, WCAG 2.1 AA) de chaque page en largeur mobile, à chaque modification (CI, `pnpm accessibilite`) ;
     - seule anomalie trouvée et corrigée : les tableaux défilants n'étaient pas atteignables au clavier.
   - Limite : un contrôle automatique couvre une partie seulement des critères du RGAA ; un audit manuel (lecteur d'écran, contrastes du graphique, navigation clavier complète) reste à faire.
   - Reste à faire, et **à décider par le mainteneur** :
     - hébergement (choix de l'hébergeur, du nom de domaine, archives par version pour que les anciens liens restent reproductibles) ;
   - Fait au lot 3.6 (deuxième partie) : les réponses unitaires du simulateur ne sont plus incluses dans le HTML. Elles sont copiées en fichier statique nommé d'après l'empreinte de la version (`/donnees/scenario-unitaire.<empreinte>.json`, aucun cache ne peut servir une version précédente) et chargées une fois par visite, partagées entre le simulateur et la comparaison, reliés par une navigation interne. La page du simulateur passe de 5,7 Mo à 123 ko (27 ko compressés) ; le fichier de données fait environ 600 ko compressés, mis en cache par le navigateur selon l'hébergement.
     - Conséquence : sans JavaScript, le simulateur affiche seulement un message de chargement (c'était déjà le cas pour le calcul).

## 7. Tests et CI

- `tests/unitaires/` : chaque fonction de calcul, sur des cas construits à la main.
- `tests/validation/` : un test par levier et par millésime. Chaque test nomme la référence, son millésime et la tolérance, et écrit l'écart dans un rapport publié par la CI, réussite ou échec. Décision du 8 octobre 2026 : le job de validation est non bloquant ; la CI publie le tableau des écarts dans le résumé de chaque exécution et un avertissement quand un écart dépasse la tolérance.
- Contrôles de registre : toute valeur numérique utilisée par le moteur doit exister dans un registre avec une source.
- Contrôle de neutralité : liste de termes interdits dans les libellés (« effort », « juste », « nécessaire »…), complétée par la relecture humaine.
- Contrôle de confidentialité : aucun champ de profil dans les journaux de l'API.

## 8. Comment je propose d'avancer

1. Tu valides ou modifies les décisions D1 à D7.
2. Je fais la tâche 0.1 (socle sans calcul) sur la branche actuelle.
3. Tâche 0.2 sur une branche dédiée, en te montrant les noms de variables OpenFisca trouvés et les écarts avec les simulateurs officiels.
4. Puis 0.3 à 0.6, une à la fois, en signalant à chaque fois les valeurs de référence saisies et les tests qui bougent.
