// Effet d'un scénario du simulateur sur les ménages types, approché à partir des cascades
// exactes exportées sur une grille de valeurs de chaque levier (menages-effets.json) : chaque
// ligne est interpolée entre les deux valeurs de la grille qui encadrent la mesure, les écarts
// des mesures sont additionnés ligne par ligne, et aucune prestation ne devient négative.
// Même calcul que le moteur (fr_budget.menages.leviers.approximation), qui en publie l'écart au
// calcul complet sur des scénarios de contrôle.
import type { LignesCascade } from "./cascade.ts";

export type Incidence = "comptable" | "salaire";
export type Grille = Record<
  string,
  Partial<Record<Incidence, Record<string, Record<string, LignesCascade | null>>>>
>;

const CHAMPS = [
  "cout_employeur",
  "salaire_brut",
  "net_avant_impot",
  "pension_brute",
  "pension_nette",
  "revenu_independant_brut",
  "cotisations_independant",
  "csg_crds_independant",
  "revenu_independant_net",
  "impot_revenu",
] as const;

type Vecteur = Record<string, number>;

function vecteur(c: LignesCascade): Vecteur {
  const v: Vecteur = {};
  for (const champ of CHAMPS) v[champ] = c[champ];
  for (const [k, montant] of Object.entries(c.prestations)) v[`prestations.${k}`] = montant;
  return v;
}

function ecart(a: Vecteur, b: Vecteur): Vecteur {
  const cles = new Set([...Object.keys(a), ...Object.keys(b)]);
  return Object.fromEntries([...cles].map((k) => [k, (b[k] ?? 0) - (a[k] ?? 0)]));
}

// Écart de chaque ligne pour `valeur`, interpolé entre les points de la grille qui l'encadrent
// (la référence est le point zéro) ; null si l'un d'eux n'est pas chiffré.
function interpoler(
  reference: Vecteur,
  points: Record<string, LignesCascade | null>,
  valeur: number,
): Vecteur | null {
  const abscisses = [0, ...Object.keys(points).map(Number)].sort((x, y) => x - y);
  const bas = Math.max(...abscisses.filter((x) => x <= valeur));
  const haut = Math.min(...abscisses.filter((x) => x >= valeur));
  const au = (x: number): Vecteur | null => {
    if (x === 0) return Object.fromEntries(Object.keys(reference).map((k) => [k, 0]));
    const point = points[String(x)];
    return point ? ecart(reference, vecteur(point)) : null;
  };
  const eb = au(bas);
  const eh = au(haut);
  if (!eb || !eh) return null;
  if (haut === bas) return eb;
  const poids = (valeur - bas) / (haut - bas);
  const cles = new Set([...Object.keys(eb), ...Object.keys(eh)]);
  return Object.fromEntries(
    [...cles].map((k) => [k, (1 - poids) * (eb[k] ?? 0) + poids * (eh[k] ?? 0)]),
  );
}

export function approcher(
  reference: LignesCascade,
  identifiant: string,
  mesures: [string, number][],
  grille: Grille,
  leviersIncidence: string[],
  incidence: Incidence = "comptable",
): LignesCascade | null {
  const base = vecteur(reference);
  const total: Vecteur = { ...base };
  for (const [levier, valeur] of mesures) {
    if (valeur === 0 || !(levier in grille)) continue;
    const lecture = leviersIncidence.includes(levier) ? incidence : "comptable";
    const parValeur = grille[levier][lecture];
    if (!parValeur) return null;
    const points = Object.fromEntries(
      Object.entries(parValeur).map(([v, menages]) => [v, menages[identifiant]]),
    );
    const e = interpoler(base, points, valeur);
    if (!e) return null;
    for (const [k, v] of Object.entries(e)) total[k] = (total[k] ?? 0) + v;
  }
  const prestations = Object.fromEntries(
    Object.entries(total)
      .filter(([k, v]) => k.startsWith("prestations.") && Math.max(v, 0) !== 0)
      .map(([k, v]) => [k.slice("prestations.".length), Math.max(v, 0)]),
  );
  const lignes = Object.fromEntries(CHAMPS.map((c) => [c, total[c]])) as Record<
    (typeof CHAMPS)[number],
    number
  >;
  return {
    ...lignes,
    prestations,
    net_apres_impot:
      lignes.net_avant_impot +
      lignes.pension_nette +
      lignes.revenu_independant_net -
      lignes.impot_revenu +
      Object.values(prestations).reduce((s, v) => s + v, 0),
  };
}
