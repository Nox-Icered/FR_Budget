# Données

- `raw/` : fichiers tels que téléchargés, jamais modifiés à la main. Quand un fichier est trop lourd ou que sa licence interdit de le redistribuer, seuls son URL et son empreinte sont dans `registres/datasets.yaml`, et le script de `pipelines/` le télécharge.
- `processed/` : tables Parquet produites uniquement par les scripts de `pipelines/`.

Les micro-données d'enquête (ERFS, par exemple) ne sont jamais committées. `outils/verifier_donnees_interdites.py` le vérifie en pré-commit et en intégration continue.
