// Exemple de scénario qui atteint un objectif, construit par une règle mécanique écrite sur la
// page (CLAUDE.md, exception encadrée à la règle de neutralité) : l'utilisateur coche les mesures
// et fixe la part de l'effort portée par les recettes ; chaque mesure cochée apporte une part
// égale de l'effort de son côté. Aucune mesure n'est choisie, classée ni qualifiée par le site.
import type { ReponsesUnitaires } from "./donnees";
import { LEVIERS_DANS_ONDAM, LEVIER_ONDAM, LEVIERS_RETRAITES } from "./etat.ts";
import { niveau, type Objectif } from "./objectif.ts";
import { calculer, type Fourchette } from "./scenario.ts";

export type Cote = "recettes" | "depenses";

// Côté des comptes publics touché par l'instrument que modifie chaque mesure (SEC 2010 :
// impôts et cotisations en recettes ; rémunérations, prestations, pensions et transferts en
// dépenses). Les allègements généraux sont des cotisations en moins, donc des recettes ;
// la prime d'activité est une prestation et l'âge de départ modifie les pensions, donc des
// dépenses. Classement validé par le responsable du projet (6 novembre 2026).
export const COTES: Record<string, Cote> = {
  tva_taux_normal: "recettes",
  accise_gazole: "recettes",
  accise_essences: "recettes",
  is_taux_normal: "recettes",
  is_surtaxe_grandes_entreprises: "recettes",
  csg_activite: "recettes",
  csg_retraites: "recettes",
  csg_capital: "recettes",
  cotisations_patronales_taux: "recettes",
  allegements_generaux: "recettes",
  ir_seuils_bareme: "recettes",
  ir_plafond_quotient_familial: "recettes",
  chomage_contribution_patronale: "recettes",
  dotations_dgf: "depenses",
  dotations_compensations: "depenses",
  remunerations_point_indice: "depenses",
  remunerations_effectifs: "depenses",
  indexation_pensions_prestations: "depenses",
  prime_activite_pente: "depenses",
  retraites_age_depart: "depenses",
  retraites_age_legal: "depenses",
  chomage_revalorisation: "depenses",
  chomage_duree_indemnisation: "depenses",
  chomage_affiliation_mois: "depenses",
  chomage_degressivite_points: "depenses",
  // Assurance maladie : franchises, indemnités journalières et ticket modérateur changent des
  // prestations (soins remboursés).
  ondam_progression: "depenses",
  franchises_participations: "depenses",
  ij_plafond_smic: "depenses",
  ticket_moderateur_consultations: "depenses",
  ticket_moderateur_dentaire: "depenses",
};

// Combinaisons refusées par le simulateur (double compte, lib/etat.ts) : âge effectif et âge
// légal de départ ; progression de l'ONDAM avec une mesure qu'il contient.
export function incompatibles(leviers: string[]): boolean {
  const avec = (l: string) => leviers.includes(l);
  return (
    LEVIERS_RETRAITES.every(avec) || (avec(LEVIER_ONDAM) && LEVIERS_DANS_ONDAM.some(avec))
  );
}

// Mesure qui ne peut pas être cochée avec celles déjà cochées.
export function exclue(id: string, coches: string[]): boolean {
  return !coches.includes(id) && incompatibles([...coches, id]);
}

export const PAS_PART_RECETTES = 0.1;
export const PART_RECETTES_DEFAUT = 0.5;

export type ChoixExemple = {
  leviers: string[];
  // Part de l'effort portée par les recettes, de 0 à 1 ; le reste par les dépenses.
  partRecettes: number;
  entree: number;
  objectif: Objectif;
  pas: Record<string, number>;
};
export type MesureExemple = {
  levier: string;
  cote: Cote;
  // Part de l'effort attribuée par la règle, en points de l'indicateur (trajectoire centrale).
  part: number;
  // Réglage qui apporte exactement cette part, puis réglage au pas du curseur (ou au cran).
  valeurExacte: number;
  valeur: number;
  // Contribution du réglage au pas, prise seule (trajectoire centrale).
  contribution: number;
  aLaLimite: boolean;
};
export type ProblemeExemple =
  | "double_compte"
  | "cote_vide_recettes"
  | "cote_vide_depenses"
  | "insuffisant_recettes"
  | "insuffisant_depenses"
  | "non_atteint";
export type Exemple = {
  mesures: MesureExemple[];
  // Indicateur l'année de l'objectif avec toutes les mesures (calcul du simulateur) ; null si
  // la règle ne donne pas d'exemple.
  atteint: Fourchette | null;
  sansMesure: number;
  problemes: ProblemeExemple[];
};

const EPS = 1e-9;
const ITERATIONS_MAX = 50;

const auPasVers = (v: number, pas: number, sens: "exterieur" | "interieur") => {
  const n = Math.abs(v) / pas;
  const k = sens === "exterieur" ? Math.ceil(n - EPS) : Math.floor(n + EPS);
  return Number((Math.sign(v) * k * pas).toFixed(6)) + 0;
};

type Capacite = {
  // Réglage qui apporte une contribution donnée (dans le sens utile), et sa contribution.
  reglage: (part: number) => { valeurExacte: number; valeur: number } | null;
  // Réglage extrême dans le sens utile, au pas, et sa contribution.
  extreme: { valeur: number; contribution: number };
};

function capacite(donnees: ReponsesUnitaires, levier: string, choix: ChoixExemple, sens: number): Capacite {
  const contribution = (v: number) =>
    niveau(donnees, levier, v, choix.entree, choix.objectif, "central") -
    niveau(donnees, levier, 0, choix.entree, choix.objectif, "central");
  const l = donnees.leviers[levier];
  if (l.grille) {
    // Levier à crans : le premier cran, en partant de zéro, qui apporte au moins la part.
    const crans = Object.keys(l.grille)
      .map(Number)
      .map((v) => ({ v, c: contribution(v) }))
      .filter(({ c }) => sens * c > EPS)
      .sort((a, b) => Math.abs(a.v) - Math.abs(b.v));
    const dernier = crans.reduce(
      (m, x) => (sens * x.c > sens * m.contribution ? { valeur: x.v, contribution: x.c } : m),
      { valeur: 0, contribution: 0 },
    );
    return {
      reglage: (part) => {
        const cran = crans.find(({ c }) => sens * c >= sens * part - EPS);
        return cran ? { valeurExacte: cran.v, valeur: cran.v } : null;
      },
      extreme: dernier,
    };
  }
  // Levier linéaire (réponses unitaires) : contribution proportionnelle au réglage.
  const pente = contribution(1);
  const pas = choix.pas[levier] ?? 1;
  const [bas, haut] = l.bornes;
  const limites = [auPasVers(bas, pas, "interieur"), auPasVers(haut, pas, "interieur")];
  const utiles = pente === 0 ? [] : limites.filter((v) => sens * pente * v > EPS);
  const v = utiles.sort((a, b) => Math.abs(b) - Math.abs(a))[0] ?? 0;
  return {
    reglage: (part) => {
      if (pente === 0) return null;
      const valeurExacte = part / pente;
      const valeur = auPasVers(valeurExacte, pas, "exterieur");
      return Math.abs(valeur) <= Math.abs(v) + EPS ? { valeurExacte, valeur } : null;
    },
    extreme: { valeur: v, contribution: v === 0 ? 0 : pente * v },
  };
}

// Répartit l'effort d'un côté à parts égales entre ses mesures ; une mesure qui ne peut pas
// porter sa part reste à la limite de son curseur et le reste se répartit entre les autres.
function repartir(
  donnees: ReponsesUnitaires,
  leviers: string[],
  cote: Cote,
  effort: number,
  choix: ChoixExemple,
): MesureExemple[] | null {
  const sens = Math.sign(effort);
  const caps = new Map(leviers.map((l) => [l, capacite(donnees, l, choix, sens)]));
  const resultat: MesureExemple[] = [];
  let actifs = [...leviers];
  let reste = effort;
  for (let i = 0; i < ITERATIONS_MAX && actifs.length > 0; i++) {
    const part = reste / actifs.length;
    const bloques = actifs.filter((l) => sens * (caps.get(l)?.extreme.contribution ?? 0) < sens * part - EPS);
    if (bloques.length === 0) {
      for (const levier of actifs) {
        const r = caps.get(levier)?.reglage(part);
        if (!r) return null;
        resultat.push({ levier, cote, part, ...r, contribution: 0, aLaLimite: false });
      }
      return resultat;
    }
    for (const levier of bloques) {
      const e = caps.get(levier)?.extreme ?? { valeur: 0, contribution: 0 };
      resultat.push({
        levier,
        cote,
        part: e.contribution,
        valeurExacte: e.valeur,
        valeur: e.valeur,
        contribution: 0,
        aLaLimite: true,
      });
      reste -= e.contribution;
    }
    actifs = actifs.filter((l) => !bloques.includes(l));
  }
  return null;
}

export function construireExemple(donnees: ReponsesUnitaires, choix: ChoixExemple): Exemple {
  const o = choix.objectif;
  const reference = choix.leviers[0] ?? Object.keys(donnees.leviers)[0];
  const sansMesure = niveau(donnees, reference, 0, choix.entree, o, "central");
  const vide = (problemes: ProblemeExemple[]): Exemple => ({ mesures: [], atteint: null, sansMesure, problemes });
  if (incompatibles(choix.leviers)) return vide(["double_compte"]);
  const effort = o.cible - sansMesure;
  const parCote: Record<Cote, number> = {
    recettes: effort * choix.partRecettes,
    depenses: effort * (1 - choix.partRecettes),
  };
  const problemes: ProblemeExemple[] = [];
  const mesures: MesureExemple[] = [];
  for (const cote of ["recettes", "depenses"] as const) {
    if (Math.abs(parCote[cote]) < EPS) continue;
    const leviers = choix.leviers.filter((l) => COTES[l] === cote);
    if (leviers.length === 0) {
      problemes.push(`cote_vide_${cote}`);
      continue;
    }
    const r = repartir(donnees, leviers, cote, parCote[cote], choix);
    if (r === null) problemes.push(`insuffisant_${cote}`);
    else mesures.push(...r);
  }
  if (problemes.length > 0) return vide(problemes);
  const avecContribution = mesures
    .filter((m) => m.valeur !== 0)
    .map((m) => ({
      ...m,
      contribution:
        niveau(donnees, m.levier, m.valeur, choix.entree, o, "central") - sansMesure,
    }));
  const lignes = calculer(
    donnees,
    avecContribution.map((m) => ({ levier: m.levier, valeur: m.valeur })),
    choix.entree,
  );
  const ligne = lignes.find((l) => l.annee === o.annee);
  if (!ligne) throw new Error(`année ${o.annee} hors de la projection`);
  const atteint = ligne[o.indicateur];
  const sens = Math.sign(effort);
  if (sens * (atteint.central - o.cible) < -1e-6) return vide(["non_atteint"]);
  return { mesures: avecContribution, atteint, sansMesure, problemes: [] };
}
