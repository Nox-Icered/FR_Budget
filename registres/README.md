# Registres

Toute valeur utilisée par le moteur remonte à une ligne de ces registres. Les schémas sont dans `moteur/src/fr_budget/registres/schemas.py` ; la vérification tourne en intégration continue et avant chaque commit :

```sh
cd moteur && uv run python -m fr_budget.registres.verification
```

| Fichier | Entité | Contenu |
|---------|--------|---------|
| `sources.yaml` | source | Nom, éditeur, URL, licence, date de publication, millésime, mode d'accès, date de consultation |
| `datasets.yaml` | dataset | Fichier de `data/raw/`, source, empreinte SHA-256, script de transformation, date de téléchargement |
| `hypotheses.yaml` | assumption | Libellé, unité, valeur centrale, plage (basse ≤ centrale ≤ haute), sources, justification, instruments |
| `leviers.yaml` | lever | Libellé neutre, paramètres réglables, moteur, références visées, statut (`valide`, `beta`, `non_publie`) |
| `references/chiffrages.yaml` | chiffrage | Chiffrage officiel saisi : levier, source, millésime, mesure, valeur, unité, localisation, statut de relecture |
| `references/menages/` | — | Valeurs de référence des ménages types, générées par script (`outils/references_urssaf/`) |
| `corrections_openfisca.yaml` | correction | Corrections apportées à OpenFisca-France, avec leurs sources |
| `libelles_interdits.yaml` | — | Termes refusés dans les libellés des leviers (règle de neutralité) |

## Ce que la vérification contrôle

- Chaque entrée respecte son schéma ; un champ inconnu (faute de frappe) est refusé.
- Les identifiants sont uniques dans chaque registre.
- Chaque renvoi (source d'une hypothèse, d'un chiffrage, d'une correction ; levier d'un chiffrage) existe.
- L'empreinte de chaque fichier de `data/raw/` correspond au registre (un fichier absent donne un avertissement : il peut être trop lourd pour le dépôt et téléchargé par script).
- La plage d'une hypothèse encadre sa valeur centrale.
- Aucun libellé de levier ne contient un terme de `libelles_interdits.yaml`.

## Mode d'accès d'une source

- `direct` : document primaire consulté.
- `recherche_web` : cité d'après des résultats de recherche, à confirmer sur le document primaire.
- `paquet` : logiciel installé (OpenFisca, modèle Urssaf).
