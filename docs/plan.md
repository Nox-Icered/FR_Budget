# Plan de développement

Ce plan découle de `CLAUDE.md` et de `docs/specification.md`. Il découpe le travail en lots livrables un par un. Une phase ne commence que lorsque la porte de la précédente est franchie.

Aucun chiffre n'apparaît dans ce plan : les valeurs viendront des registres, avec leur source.

## 0. État des lieux (7 octobre 2026)

- Le dépôt `Nox-Icered/FR_Budget` est vide. Les seuls documents sont `CLAUDE.md` et la spécification, désormais dans `docs/`.
- Environnement : Python 3.11, 3.12 et 3.13 disponibles, Node 22, `uv`, `pandoc`.
- `openfisca-france` est disponible sur PyPI en version 176.1.2 (dépend de `openfisca-core` ≥ 43, < 45). La résolution des dépendances passe sous Python 3.13 ; l'installation réelle et un premier calcul restent à faire (tâche 0.2).

## 1. Décisions à prendre avant de coder

| # | Question | Proposition par défaut | Pourquoi |
|---|----------|------------------------|----------|
| D1 | Licence du code | AGPL-3.0 | OpenFisca-France est sous AGPL-3.0 (à vérifier dans le paquet installé) ; une API publique qui l'utilise doit rester compatible. |
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
- Indicateur de dépense incompressible pour TVA et accises (budgets de famille INSEE).
- Entreprises : charge par taille et secteur (ESANE, DGFiP), sans effet comportemental.
- Écrans Catalogue, Simulateur, Ménages, Entreprises, « Comment c'est calculé ? ».

## 6. Phase 3 : V1

Porte 3 : mise en ligne avec tests et écarts publics.

1. Module retraites : modèle de cohortes calé sur les projections du COR, démographie INSEE, validation contre les variantes publiées par le COR.
2. Interrupteur de croissance : multiplicateur par instrument et décroissant dans le temps, valeurs et plages sourcées, désactivé par défaut, effet retour par l'élasticité des prélèvements.
3. Scénarios partagés : PostgreSQL, identifiant court, version du modèle et des données enregistrées avec le scénario.
4. Comparaison de 2 à 3 scénarios, export CSV et JSON.
5. Pages Journal et Relectures ; mentions légales.
6. Accessibilité (RGAA visé), mobile, cache des scénarios courants, hébergement.

## 7. Tests et CI

- `tests/unitaires/` : chaque fonction de calcul, sur des cas construits à la main.
- `tests/validation/` : un test par levier et par millésime. Chaque test nomme la référence, son millésime et la tolérance, et écrit l'écart dans un rapport publié par la CI, réussite ou échec.
- Contrôles de registre : toute valeur numérique utilisée par le moteur doit exister dans un registre avec une source.
- Contrôle de neutralité : liste de termes interdits dans les libellés (« effort », « juste », « nécessaire »…), complétée par la relecture humaine.
- Contrôle de confidentialité : aucun champ de profil dans les journaux de l'API.

## 8. Comment je propose d'avancer

1. Tu valides ou modifies les décisions D1 à D7.
2. Je fais la tâche 0.1 (socle sans calcul) sur la branche actuelle.
3. Tâche 0.2 sur une branche dédiée, en te montrant les noms de variables OpenFisca trouvés et les écarts avec les simulateurs officiels.
4. Puis 0.3 à 0.6, une à la fois, en signalant à chaque fois les valeurs de référence saisies et les tests qui bougent.
