// Génère les valeurs de référence « Urssaf » des ménages types.
//
// Source : paquet npm `modele-social`, qui contient les règles de calcul utilisées par
// https://mon-entreprise.urssaf.fr (dépôt betagouv/mon-entreprise, licence MIT).
// Le site officiel n'est pas joignable depuis l'environnement de développement : on
// exécute donc le même modèle localement, en version figée.
//
// Les hypothèses que le cas ne fixe pas (effectif, taux AT/MP, mutuelle…) prennent la
// valeur par défaut du modèle Urssaf. Elles sont relues dans le modèle et écrites dans
// le fichier de sortie, pour que le moteur OpenFisca utilise exactement les mêmes.
//
// Usage : npm ci && npm run generer

import { readFileSync, writeFileSync } from 'node:fs'
import rules from 'modele-social'
import Engine from 'publicodes'

const SORTIE = new URL('../../registres/references/menages/urssaf_modele_social.json', import.meta.url)
const versionDe = (paquet) =>
	JSON.parse(readFileSync(new URL(`./node_modules/${paquet}/package.json`, import.meta.url))).version

// Chaque cas : identifiant, date de calcul (premier jour du mois), situation saisie.
const CAS = [
	{
		id: 'celibataire_smic_2026_01_sans_mutuelle',
		mois: '2026-01',
		situation: {
			'salarié . contrat . salaire brut': 'SMIC',
			'salarié . cotisations . prévoyances . santé . montant': '0 €/mois',
		},
	},
	{
		id: 'celibataire_smic_2026_01_mutuelle_par_defaut',
		mois: '2026-01',
		situation: { 'salarié . contrat . salaire brut': 'SMIC' },
	},
	{
		id: 'celibataire_smic_2026_07_sans_mutuelle',
		mois: '2026-07',
		situation: {
			'salarié . contrat . salaire brut': 'SMIC',
			'salarié . cotisations . prévoyances . santé . montant': '0 €/mois',
		},
	},
]

// Hypothèses relues dans le modèle, avec l'unité attendue par le moteur.
const HYPOTHESES = {
	effectif_entreprise: ['entreprise . salariés . effectif', 1],
	taux_accident_travail: ['salarié . cotisations . ATMP . taux', 1 / 100],
	mutuelle_montant_mensuel: ['salarié . cotisations . prévoyances . santé . montant', 1],
	mutuelle_part_employeur: ['salarié . cotisations . prévoyances . santé . taux employeur', 1 / 100],
}

const RESULTATS = {
	salaire_brut: 'salarié . contrat . salaire brut',
	cout_employeur: 'salarié . coût total employeur',
	net_avant_impot: 'salarié . rémunération . net . à payer avant impôt',
	net_imposable: 'salarié . rémunération . net . imposable',
}

const silencieux = { log() {}, warn() {}, error() {} }
const moteur = new Engine(rules, { logger: silencieux })

const valeur = (regle) => {
	const v = moteur.evaluate(regle).nodeValue
	if (typeof v !== 'number') throw new Error(`Règle sans valeur numérique : ${regle}`)
	return v
}

const cas = CAS.map(({ id, mois, situation }) => {
	const [annee, m] = mois.split('-')
	moteur.setSituation({ date: `'01/${m}/${annee}'`, ...situation })
	return {
		id,
		mois,
		situation,
		hypotheses: Object.fromEntries(
			Object.entries(HYPOTHESES).map(([nom, [regle, facteur]]) => [nom, Number((valeur(regle) * facteur).toPrecision(12))]),
		),
		resultats_mensuels: Object.fromEntries(
			Object.entries(RESULTATS).map(([nom, regle]) => [nom, valeur(regle)]),
		),
	}
})

const sortie = {
	source: {
		nom: 'Modèle de calcul de mon-entreprise.urssaf.fr (paquet npm modele-social)',
		editeur: 'Urssaf Caisse nationale (betagouv/mon-entreprise)',
		url: 'https://www.npmjs.com/package/modele-social',
		depot: 'https://github.com/betagouv/mon-entreprise',
		licence: 'MIT',
		version_modele_social: versionDe('modele-social'),
		version_publicodes: versionDe('publicodes'),
		script: 'outils/references_urssaf/generer.mjs',
	},
	cas,
}

writeFileSync(SORTIE, JSON.stringify(sortie, null, 2) + '\n')
console.log(`${cas.length} cas écrits dans ${SORTIE.pathname}`)
