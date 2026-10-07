# Registres

Toute valeur utilisée par le moteur remonte à une ligne de ces registres, avec sa source, son millésime et sa licence. Schémas et contrôles : tâche 0.3 du [plan](../docs/plan.md).

- `sources.yaml` : sources publiques (nom, URL, éditeur, date de publication, millésime, licence)
- `datasets.yaml` : séries extraites d'une source (méthode de transformation, empreinte du fichier)
- `hypotheses.yaml` : hypothèses (identifiant, libellé, valeur centrale, plage, source, justification, instruments concernés)
- `leviers.yaml` : leviers (paramètres réglables, moteur, statut de validation)
- `references/` : chiffrages officiels et académiques saisis, par levier et millésime
