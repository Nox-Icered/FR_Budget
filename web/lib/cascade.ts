// Lignes de la cascade d'un ménage (ménages types et ménage saisi) : celles du salaire pour un
// ménage qui en a un, de la pension pour un retraité, du revenu d'un indépendant.
import { texte } from "./textes.ts";

export type LignesCascade = {
  cout_employeur: number;
  salaire_brut: number;
  net_avant_impot: number;
  pension_brute: number;
  pension_nette: number;
  revenu_independant_brut: number;
  cotisations_independant: number;
  csg_crds_independant: number;
  revenu_independant_net: number;
  impot_revenu: number;
  prestations: Record<string, number>;
  net_apres_impot: number;
};

export function lignesCascade(m: LignesCascade): [string, number][] {
  const salaire: [string, number][] =
    m.salaire_brut > 0
      ? [
          [texte("menages.cout_employeur"), m.cout_employeur],
          [texte("menages.salaire_brut"), m.salaire_brut],
          [texte("menages.net_avant_impot"), m.net_avant_impot],
        ]
      : [];
  const pension: [string, number][] =
    m.pension_brute > 0
      ? [
          [texte("menages.pension_brute"), m.pension_brute],
          [texte("menages.pension_nette"), m.pension_nette],
        ]
      : [];
  const independant: [string, number][] =
    m.revenu_independant_brut > 0
      ? [
          [texte("menages.revenu_independant_brut"), m.revenu_independant_brut],
          [texte("menages.cotisations_independant"), -m.cotisations_independant],
          [texte("menages.csg_crds_independant"), -m.csg_crds_independant],
          [texte("menages.revenu_independant_net"), m.revenu_independant_net],
        ]
      : [];
  return [
    ...salaire,
    ...pension,
    ...independant,
    [texte("menages.impot_revenu"), -m.impot_revenu],
    ...Object.entries(m.prestations).map(
      ([cle, v]): [string, number] => [texte(`menages.prestations.${cle}`), v],
    ),
    [texte("menages.net_apres_impot"), m.net_apres_impot],
  ];
}

// Lignes de plusieurs cascades alignées : les prestations de toutes sont réunies (une
// prestation peut apparaître ou disparaître), à zéro quand elles manquent d'une cascade.
function lignesAlignees(cascades: LignesCascade[]): [string, number][][] {
  const cles = [...new Set(cascades.flatMap((m) => Object.keys(m.prestations)))];
  const lignes = cascades.map((m) =>
    lignesCascade({
      ...m,
      prestations: Object.fromEntries(cles.map((c) => [c, m.prestations[c] ?? 0])),
    }),
  );
  const [premiere] = lignes;
  if (lignes.some((l) => l.length !== premiere.length || l.some(([x], i) => x !== premiere[i][0]))) {
    throw new Error("cascades non comparables");
  }
  return lignes;
}

// Avant et après une réforme, ligne par ligne.
export function lignesComparees(
  avant: LignesCascade,
  apres: LignesCascade,
): { libelle: string; avant: number; apres: number; ecart: number }[] {
  const [a, b] = lignesAlignees([avant, apres]);
  return a.map(([libelle, v], i) => ({ libelle, avant: v, apres: b[i][1], ecart: b[i][1] - v }));
}

// Cascade au revenu central et sa fourchette sur les variantes de revenu (revenu bas et haut :
// bornes des hypothèses d'évolution des revenus), ligne par ligne.
export function lignesEnFourchette(
  central: LignesCascade,
  variantes: LignesCascade[],
): { libelle: string; valeur: number; bas: number; haut: number }[] {
  const [c, ...autres] = lignesAlignees([central, ...variantes]);
  return c.map(([libelle, v], i) => {
    const valeurs = [v, ...autres.map((l) => l[i][1])];
    return { libelle, valeur: v, bas: Math.min(...valeurs), haut: Math.max(...valeurs) };
  });
}

// Avant et après une réforme au revenu central (première paire), avec la fourchette de l'écart
// sur les variantes de revenu (paires suivantes, avant et après dans la même variante).
export function comparaisonsEnFourchette(
  paires: [LignesCascade, LignesCascade][],
): { libelle: string; avant: number; apres: number; ecart: number; ecart_bas: number; ecart_haut: number }[] {
  const lignes = lignesAlignees(paires.flat());
  const [avant, apres] = lignes;
  return avant.map(([libelle, v], i) => {
    const ecarts = paires.map((_, k) => lignes[2 * k + 1][i][1] - lignes[2 * k][i][1]);
    return {
      libelle,
      avant: v,
      apres: apres[i][1],
      ecart: ecarts[0],
      ecart_bas: Math.min(...ecarts),
      ecart_haut: Math.max(...ecarts),
    };
  });
}
