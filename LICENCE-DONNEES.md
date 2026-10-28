Licence des données et registres
================================

Ce fichier s'applique aux registres (`registres/`) et aux tables produites par les scripts du projet (`data/processed/`).

Chaque source publique d'origine garde sa propre licence, indiquée dans `registres/sources.yaml`. Les fichiers bruts de `data/raw/` restent sous la licence de leur éditeur.

Le code du projet est sous AGPL-3.0 (voir `LICENSE`).

**Exception : tables dérivées de données sous licence ODbL.** Les tables suivantes sont dérivées des jeux open data de l'Urssaf, publiés sous Open Database License (ODbL) 1.0. Elles sont distribuées sous cette même licence, et non sous la Licence Ouverte 2.0 ci-dessous ; le texte de l'ODbL est dans `LICENCE-ODBL.txt` (repris sans modification de https://opendatacommons.org/licenses/odbl/odbl-10.txt). Mention de la source : Urssaf, open.urssaf.fr, avec la date de mise à jour de chaque jeu indiquée dans `registres/sources.yaml` (identifiants `urssaf_open_data_*`).

- `data/processed/entreprises/taille.csv`
- `data/processed/entreprises/secteur.csv`
- `data/processed/entreprises/masse_salariale_annuelle.csv`
- le fichier `entreprises.json` produit par l'export de l'API (`api/src/fr_budget_api/export.py`) et publié par le site, ainsi que la réponse de la route `GET /entreprises`

Les tables `data/processed/entreprises/is_taille.csv` et `is_secteur.csv`, dérivées de données de la DGFiP (Licence Etalab 2.0), restent sous la Licence Ouverte 2.0.

**Exception : documents de la DG Trésor, réutilisation non commerciale** (décision du mainteneur du 28 octobre 2026). Les mentions légales du site de la DG Trésor n'autorisent que la « réutilisation non commerciale », en respectant l'intégrité des informations et en citant la source (`registres/sources.yaml`, identifiants `plf2027_resf`, `dgtresor_tresor_eco_371` et `dgtresor_cahier_2016_02`). Les fichiers et données suivants restent donc sous ces conditions, et non sous la Licence Ouverte 2.0 :

- les fichiers bruts `data/raw/baseline/tresor/PLF_2027_RESF.pdf` et `Tableaux_RESF_2027.xlsx` (rapport économique, social et financier du PLF 2027), `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf` et `data/raw/tva/dgtresor_cahier_2016-02_tva_theorique.pdf` ;
- la table dérivée `data/processed/baseline/resf_2027.csv`, et la trajectoire 2025-2030 de la baseline qui en reprend les valeurs (fichiers de l'export de l'API publiés par le site, route `GET /baseline`) ;
- les valeurs tirées de ces documents dans `registres/references/chiffrages.yaml` (chiffrages dont la `source` est l'un des identifiants ci-dessus), reprises comme citations avec leur source.

Le rapport économique, social et financier est une annexe du projet de loi de finances ; si la DG Trésor confirme qu'il relève de la libre réutilisation, cette exception sera levée.

**Exception : conditions non vérifiées.** La documentation « PCI et masse volumique » de la Base Carbone de l'ADEME (`data/raw/accises/ademe/base_carbone_pci_et_masse_volumique.htm`, identifiant `ademe_base_carbone_pci_masse_volumique`) est publiée sous la Licence Ouverte selon la documentation de l'ADEME, ce qui n'a pas pu être vérifié sur la page officielle de la Base Empreinte (inaccessible depuis l'environnement de travail le 28 octobre 2026). D'ici là, ce fichier et les masses volumiques qui en sont tirées sont repris comme citations, avec leur source.

Le texte de la licence ci-dessous est repris sans modification de https://github.com/etalab/licence-ouverte (fichier `LO.md`).

---

# LICENCE OUVERTE 2.0/OPEN LICENCE 2.0

## Réutilisation de l’« Information » sous  cette licence

Le « Concédant » concède au « Réutilisateur » un droit non exclusif et gratuit de libre  « Réutilisation » de l’« Information » objet de la présente licence, à des fins commerciales ou non, dans le monde entier et pour une durée illimitée, dans les conditions exprimées ci-dessous.

**Le « Réutilisateur » est libre de réutiliser l’« Information » :**

-   de la communiquer, la reproduire, la copier ;
-   de l’adapter, la modifier, l’extraire et la transformer, notamment pour créer des « Informations dérivées » ;
-   de la diffuser, la redistribuer, la publier et la transmettre, de l’exploiter à titre commercial, par exemple en la combinant avec d’autres informations, ou en l’incluant dans votre propre produit ou application.

**Sous réserve de :**

-   mentionner la paternité de l’«Information» : sa source (a minima le nom du  « Concédant ») et la date de la dernière mise à jour de l’« Information » réutilisée.

Le « Réutilisateur » peut notamment s’ acquitter de cette condition en indiquant l’adresse (URL) renvoyant vers « l’Information » et assurant une mention effective de sa paternité.

**Par exemple :**

Dans le cas d’une réutilisation de la base SIRENE de l’INSEE, mentionner l’URL du « Concédant » : www.insee.fr + la date de dernière mise à jour de l’Information réutilisée.

Cette mention de paternité ne doit ni conférer un caractère officiel à la « Réutilisation » de l’« Information », ni suggérer une quelconque reconnaissance ou caution par le « Concédant », ou par toute autre entité publique, du « Réutilisateur » ou de sa « Réutilisation ».

## Données à caractère personnel

L’« Information » mise à disposition peut contenir des « Données à caractère personnel » pouvant faire l’objet d’une « Réutilisation ». Alors, le « Concédant » informe le « Réutilisateur » (par tous moyens) de leur présence, l’ « Information » peut être librement réutilisée, sans faire obstacle aux libertés accordées par la présente licence, à condition de respecter le cadre légal relatif à la protection des données à caractère personnel.

## Droits de propriété intellectuelle

Il est garanti au « Réutilisateur » que l’ « Information » ne contient pas de « Droits de propriété intellectuelle »  appartenant à des tiers qui pourraient faire obstacle aux libertés qui lui sont accordées par la présente licence.

Les éventuels « Droits de propriété intellectuelle » détenus par le « Concédant » sur l’ « Information » ne font pas obstacle aux libertés qui sont accordées par la présente licence. Lorsque le « Concédant » détient des « Droits de propriété intellectuelle » » sur l’ « Information », il les cède au « Réutilisateur » de façon non exclusive, à titre gracieux, pour le monde entier, pour toute la durée des « Droits de propriété intellectuelle », et le « Réutilisateur »  peut en faire tout usage conformément aux libertés et aux conditions définies par la présente licence.

## Responsabilité

L’ «Information» est mise à disposition telle que produite ou reçue, sans autre garantie expresse ou tacite qui n’est pas prévue par la présente licence. L’absence de défauts ou d’erreurs éventuellement contenues dans l’ «Information», comme la fourniture continue de l’ « Information » n’est pas garantie par le «Concédant». Il ne peut être tenu pour responsable de toute perte, préjudice ou dommage de quelque sorte causé à des tiers du fait de la « Réutilisation ».

Le « Réutilisateur » est seul responsable de la « Réutilisation » de l’« Information ».

La « Réutilisation » ne doit pas induire en erreur des tiers quant au contenu de l’« Information », sa source et sa date de mise à jour.

## Droit applicable

La présente licence est régie par le droit français.

### Compatibilité de la présente licence

Elle a été conçue pour être compatible avec toute licence libre qui exige _a minima_ la mention de paternité. Elle est notamment compatible avec la version antérieure de la présente licence ainsi qu’avec les licences « Open Government Licence » (OGL) du Royaume-Uni, « Creative Commons Attribution » (CC-BY) de Creative Commons et « Open Data Commons Attribution » (ODC-BY) de l’Open Knowledge Foundation.

## Définitions

Sont considérés, au sens de la présente licence comme :

-   Le « **Concédant** » : toute personne concédant un droit de « Réutilisation » sur l’« Information » dans les libertés et les conditions prévues par la présente licence.
-   L’« **Information** » :
    -   toute information publique figurant dans des documents communiqués ou publiés par une administration mentionnée au premier alinéa de l’article L.300-2 du CRPA ;
    -   toute information mise à disposition par toute personne selon les termes et conditions de la présente licence.
-   La « **Réutilisation** » : l’utilisation de l’« Information » à d’autres fins que celles pour lesquelles elle a été produite ou reçue.
-   Le « **Réutilisateur** » : toute personne qui réutilise les « Informations »  conformément aux conditions de la présente licence.
-   Des « **Données à caractère personnel** » : toute information se rapportant à une personne physique identifiée ou identifiable, pouvant être identifiée directement ou indirectement. Leur « Réutilisation » est subordonnée au respect du cadre juridique en vigueur.
-   Une « **Information dérivée** » : toute nouvelle donnée ou information créées directement à partir de l’« Information » ou à partir d’une combinaison  de l’ « Information » et d’autres données ou informations non  soumises à cette licence.
-   Les « **Droits de propriété intellectuelle** » : tous droits identifiés comme tels par le Code de la propriété intellectuelle (droit d’auteur, droits voisins au droit d’auteur, droit sui generis des producteurs de bases de données).

## À propos de cette licence

La présente licence a vocation à être utilisée par les administrations pour la réutilisation de leurs informations publiques. Elle peut également être utilisée par toute personne souhaitant mettre à disposition de l’« Information » dans les conditions définies par la présente licence.

La France est dotée d’un cadre juridique global visant à une diffusion spontanée par les administrations de leurs informations publiques afin d’en permettre la plus large réutilisation.

Le droit de la « Réutilisation » de l’« Information » des administrations est régi par le code des relations entre le public et l’administration (CRPA) et, le cas échéant, le code du patrimoine (livre II relatif aux archives).

Cette licence facilite la réutilisation libre et gratuite des informations publiques et figure parmi les licences qui peuvent être utilisées par l’administration en vertu du décret pris en application de l’article L.323-2 du CRPA.

Etalab est la mission chargée, sous l’autorité du Premier ministre, d’ouvrir le plus grand nombre de données publiques des administrations de l’État et de ses établissements publics. Elle a réalisé la Licence Ouverte pour faciliter la réutilisation libre et gratuite de ces informations publiques, telles que définies par l’article L321-1 du CRPA.

Cette licence est une version 2.0 de la Licence Ouverte.

Etalab se réserve la faculté de proposer de nouvelles versions de la Licence Ouverte. Cependant, les « Réutilisateurs » pourront continuer à réutiliser les informations disponibles sous cette licence s’ils le souhaitent.
