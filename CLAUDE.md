# CLAUDE.md — Simulateur public du budget des administrations publiques françaises

Ce fichier donne à Claude Code le contexte et les règles du projet. Il prime sur les habitudes par défaut. La spécification complète est dans `docs/specification.md`.

## Objectif

Un site web public, open source, où n'importe quel Français choisit une réforme (paramétrique ou structurelle) et voit son effet chiffré sur :

- le budget de toutes les administrations publiques (État, Sécurité sociale, collectivités) ;
- la dette et le solde de N à N+20 ;
- le salaire (coût employeur, brut, net avant impôt, net après impôt) de ménages types ;
- la charge fiscale et sociale des entreprises, par taille et secteur.

Chaque chiffre, source, hypothèse et calcul doit être visible et vérifiable. Le projet est sérieux ou il n'existe pas : un levier non validé n'est pas publié.

## Règles non négociables

1. **Aucune valeur reprise de mémoire.** Tout chiffre (taux, barème, montant, chiffrage officiel, multiplicateur) vient d'une source citée dans le registre de données ou d'hypothèses. Si tu ne trouves pas la source, tu t'arrêtes et tu me le dis, tu n'inventes pas.
2. **Aucun nom de variable OpenFisca supposé.** Vérifie-le dans le paquet installé ou dans le référentiel avant de l'utiliser.
3. **Neutralité.** Aucun score, aucun classement, aucune « meilleure réforme ». Les intitulés sont descriptifs (« hausse de 1 point du taux normal de TVA », pas « effort fiscal »). Pas de formulation qui oriente.
4. **Fourchettes, jamais un chiffre unique.** Tout résultat est donné en valeur basse, centrale et haute, dérivées de plages d'hypothèses sourcées.
5. **Aucun stockage de données personnelles.** Les profils de ménage saisis par un utilisateur ne sont ni enregistrés ni journalisés.
6. **Pas de levier publié sans validation.** Voir la règle de publication ci-dessous.
7. **Les tests ne sont jamais modifiés pour faire passer le code.** Si un test de validation échoue, c'est le modèle ou la donnée de référence qu'on examine, et l'écart est rapporté tel quel.

## Règle de publication d'un levier ou d'un module

Un levier passe en production seulement si :

- il reproduit le chiffrage officiel de référence à ±10 % sur le rendement à 1 an, sur au moins deux millésimes quand deux existent ;
- il est confronté à une source indépendante (IPP, OFCE, Cour des comptes, Commission européenne) et l'écart est publié ;
- son jeu de tests automatisés tourne à chaque modification du code et des données.

Sinon il est marqué « bêta, non validé » avec un bandeau explicite, ou reste hors du site. L'écart avec la référence est toujours affiché sur la page Validation, y compris quand le modèle est moins bon.

## Périmètre et phases

- **V1** : tableau de bord des APU, baseline N à N+20, dynamique de la dette, 12 leviers paramétriques, ménages types, entreprises, interrupteur de multiplicateur budgétaire (désactivé par défaut), module structurel retraites, pages de transparence, partage par lien, export CSV/JSON, comparaison de 2 à 3 scénarios.
- **V2** : assurance chômage, assurance maladie, impôt sur le revenu (structure), agrégats par décile issus de publications officielles, combinaison de réformes sans double compte, API publique.
- **V3** : cotisations, minima sociaux, fiscalité du capital, collectivités, élasticités comportementales sourcées, version anglaise.
- **Hors scope** : recommander des réformes, modèle macro complet, comptes utilisateurs.

Phases : 0 cadrage (prototype TVA validé), 1 socle (dashboard, baseline, dette), 2 leviers (12 leviers, ménages, entreprises), 3 V1 (retraites, croissance, partage). Ne pas commencer une phase avant que la porte de la précédente soit franchie.

## Architecture

- **Moteur socio-fiscal** : Python, OpenFisca-France, utilisé comme bibliothèque (pas via `openfisca serve`). Le système socio-fiscal est chargé une seule fois au démarrage du serveur.
- **Modèle agrégé APU et modules structurels** : Python (pandas, NumPy), testés avec pytest.
- **API** : FastAPI, sans état.
- **Données** : fichiers CSV versionnés (lisibles en revue de code ; décision du 30 octobre 2026), scripts d'extraction et de transformation rejouables ; PostgreSQL pour les scénarios partagés.
- **Front** : TypeScript, React (Next.js), mobile first, textes externalisés pour préparer l'anglais.
- **CI** : GitHub Actions, les tests de validation tournent à chaque modification.

Chaîne de calcul : sources publiques → registre de données et registre d'hypothèses → moteurs (OpenFisca pour les ménages, modèle agrégé pour les leviers, modules structurels) → agrégation de l'écart de solde primaire → dynamique de la dette (avec baseline) → résultats en fourchette → tests de validation.

## Dynamique de la dette

En ratio de PIB : `d(t+1) = d(t) * (1 + r) / (1 + g) - pb + sfa`. Le solde primaire du scénario est celui de la baseline plus l'effet de la réforme. Le taux apparent r dépend du profil de maturité de la dette existante, pas d'un taux de marché unique. L'effet de croissance (multiplicateur) est un interrupteur désactivé par défaut, avec des valeurs sourcées dans le registre d'hypothèses.

## Moteur salaire

Pour chaque ménage type, afficher avant et après réforme : coût total employeur, salaire brut, salaire net avant impôt, salaire net après impôt (prestations et crédits d'impôt inclus), avec l'écart ligne par ligne. L'incidence des cotisations patronales est un réglage visible (par défaut : incidence comptable), et le résultat est montré dans les deux lectures.

## Données et hypothèses

- Chaque donnée a : source, URL, éditeur, date de publication, millésime, licence, méthode de transformation, empreinte du fichier.
- Chaque hypothèse a : identifiant, libellé, valeur centrale, plage, source, justification, instruments concernés.
- Les données brutes sont conservées telles que téléchargées. Seules des transformations scriptées et versionnées produisent les tables du modèle.
- Les micro-données d'enquête (par exemple ERFS) ne sont pas publiables : n'en jamais committer.
- Chaque scénario enregistre la version du modèle et des données, pour qu'un lien partagé reproduise toujours le même résultat.

## Conventions de code

- Python : typage, fonctions pures pour les calculs, docstring qui cite la source de chaque paramètre. Formatage et lint automatiques.
- Un calcul = une fonction testée. Pas de nombre magique : toute constante vient du registre.
- Tests : écrire le test avant le code pour tout levier. Un test de validation nomme la référence officielle, son millésime et la tolérance.
- Messages de commit courts et factuels. Un levier ou un module par branche.
- Tout texte affiché à l'utilisateur est en français, court, sans jargon, avec un renvoi au glossaire.

## Comment travailler avec moi

- Avance phase par phase, un levier à la fois. Propose un plan court avant tout changement qui touche au calcul.
- Quand un calcul change, dis-moi quels tests ont bougé et de combien.
- Quand tu hésites entre deux sources ou deux méthodes, présente les deux avec leurs écarts, ne choisis pas en silence.
- Je relis moi-même chaque modification du modèle de calcul et chaque valeur de référence saisie. Signale-les explicitement dans ta réponse.
- Si une donnée ou un accès réseau manque, dis-le et demande-moi de déposer le fichier plutôt que d'improviser.

## Premières tâches (phase 0)

1. Créer le dépôt public, choisir la licence, poser la structure du projet.
2. Installer OpenFisca-France et reproduire un ménage type contre les simulateurs officiels.
3. Rassembler, pour les 12 leviers, les chiffrages officiels des trois derniers millésimes du PLF (Voies et Moyens).
4. Construire le prototype TVA : assiette, rendement, comparaison avec le chiffrage officiel.
5. Rédiger le modèle de fiche d'un levier et le premier registre d'hypothèses.
6. Dresser la liste de 5 à 10 relecteurs potentiels (communauté OpenFisca, IPP, économistes des finances publiques).
