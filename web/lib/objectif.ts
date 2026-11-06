// Mode « atteindre un objectif » : pour un levier choisi par l'utilisateur, la valeur qui amène
// la dette (ou le solde primaire) à une cible une année donnée. Recherche par dichotomie sur le
// calcul du simulateur (lib/scenario.ts) : le résultat redonne exactement le simulateur. Aucun
// levier n'est proposé ni classé : l'utilisateur choisit lequel régler.
import type { ReponsesUnitaires } from "./donnees";
import { calculer, type Fourchette } from "./scenario.ts";

export type Indicateur = "dette" | "solde_primaire";
export type Objectif = { indicateur: Indicateur; annee: number; cible: number };
export type Borne = keyof Fourchette;
export type Solution = {
  // Valeur du levier qui atteint la cible sur la trajectoire de chaque borne ; null si la
  // cible est hors de portée dans les bornes du levier.
  parBorne: Record<Borne, number | null>;
  // Niveau de l'indicateur sans mesure, l'année de l'objectif (trajectoire centrale).
  sansMesure: number;
};

const ITERATIONS = 60;

export function niveau(
  donnees: ReponsesUnitaires,
  levier: string,
  valeur: number,
  entree: number,
  objectif: Objectif,
  borne: Borne,
  croissance = false,
): number {
  const lignes = calculer(donnees, valeur === 0 ? [] : [{ levier, valeur }], entree, croissance);
  const ligne = lignes.find((l) => l.annee === objectif.annee);
  if (!ligne) throw new Error(`année ${objectif.annee} hors de la projection`);
  return ligne[objectif.indicateur][borne];
}

// Valeurs candidates d'un levier non linéaire (réponses exactes par cran) : celles de sa grille.
function crans(donnees: ReponsesUnitaires, levier: string): number[] | null {
  const grille = donnees.leviers[levier].grille;
  return grille ? [0, ...Object.keys(grille).map(Number)].sort((a, b) => a - b) : null;
}

function resoudreBorne(
  donnees: ReponsesUnitaires,
  levier: string,
  entree: number,
  objectif: Objectif,
  borne: Borne,
  croissance: boolean,
): number | null {
  const f = (v: number) => niveau(donnees, levier, v, entree, objectif, borne, croissance) - objectif.cible;
  const valeurs = crans(donnees, levier);
  if (valeurs) {
    // Premier cran, en partant de zéro dans le sens utile, qui atteint ou dépasse la cible.
    const ecarts = valeurs.map((v) => ({ v, e: f(v) }));
    const zero = f(0);
    if (zero === 0) return 0;
    const candidats = ecarts
      .filter(({ e }) => Math.sign(e) !== Math.sign(zero))
      .sort((a, b) => Math.abs(a.v) - Math.abs(b.v));
    return candidats[0]?.v ?? null;
  }
  let [bas, haut] = donnees.leviers[levier].bornes;
  let fb = f(bas);
  const fh = f(haut);
  if (fb === 0) return bas;
  if (fh === 0) return haut;
  if (Math.sign(fb) === Math.sign(fh)) return null;
  for (let i = 0; i < ITERATIONS; i++) {
    const milieu = (bas + haut) / 2;
    const fm = f(milieu);
    if (fm === 0) return milieu;
    if (Math.sign(fm) === Math.sign(fb)) {
      bas = milieu;
      fb = fm;
    } else {
      haut = milieu;
    }
  }
  return (bas + haut) / 2;
}

export function resoudre(
  donnees: ReponsesUnitaires,
  levier: string,
  entree: number,
  objectif: Objectif,
  croissance = false,
): Solution {
  const bornes: Borne[] = ["bas", "central", "haut"];
  return {
    parBorne: Object.fromEntries(
      bornes.map((b) => [b, resoudreBorne(donnees, levier, entree, objectif, b, croissance)]),
    ) as Record<Borne, number | null>,
    sansMesure: niveau(donnees, levier, 0, entree, objectif, "central", croissance),
  };
}

// Fourchette de la valeur qui atteint la cible : extrêmes des valeurs trouvées sur les trajectoires
// basse, centrale et haute ; null si la valeur centrale est hors de portée.
export function fourchetteValeur(s: Solution): Fourchette | null {
  const c = s.parBorne.central;
  if (c === null) return null;
  const autres = [s.parBorne.bas, s.parBorne.haut].filter((v): v is number => v !== null);
  return { bas: Math.min(c, ...autres), central: c, haut: Math.max(c, ...autres) };
}

// Réglage au pas du curseur qui atteint la cible, dans les limites du curseur du simulateur
// (bornes arrondies vers l'intérieur au pas, comme le curseur) ; null s'il n'y en a pas.
export function reglageAuPas(
  donnees: ReponsesUnitaires,
  levier: string,
  pas: number,
  entree: number,
  objectif: Objectif,
  valeur: number,
): number | null {
  const l = donnees.leviers[levier];
  if (l.grille) return valeur;
  const [bas, haut] = l.bornes;
  const min = Math.ceil(bas / pas - 1e-9) * pas;
  const max = Math.floor(haut / pas + 1e-9) * pas;
  const v = auPas(valeur, pas);
  if (v < min - 1e-9 || v > max + 1e-9) return null;
  // L'arrondi vers l'extérieur atteint la cible ou la dépasse, dans le même sens que la valeur.
  const sansMesure = niveau(donnees, levier, 0, entree, objectif, "central");
  const atteint = niveau(donnees, levier, v, entree, objectif, "central");
  const sens = Math.sign(objectif.cible - sansMesure);
  return sens * (atteint - objectif.cible) >= -1e-9 ? v : null;
}

// Valeur au pas du curseur du simulateur, arrondie dans le sens qui atteint la cible (vers
// l'extérieur, en partant de zéro).
export function auPas(valeur: number, pas: number): number {
  const n = Math.abs(valeur) / pas;
  const arrondi = Math.ceil(n - 1e-9) * pas;
  return Number((Math.sign(valeur) * arrondi).toFixed(6)) + 0;
}
