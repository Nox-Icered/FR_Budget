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

// Avant et après une réforme, ligne par ligne : les prestations des deux cascades sont réunies
// (une prestation peut apparaître ou disparaître), à zéro quand elles manquent d'un côté.
export function lignesComparees(
  avant: LignesCascade,
  apres: LignesCascade,
): { libelle: string; avant: number; apres: number; ecart: number }[] {
  const cles = [...new Set([...Object.keys(avant.prestations), ...Object.keys(apres.prestations)])];
  const completer = (m: LignesCascade): LignesCascade => ({
    ...m,
    prestations: Object.fromEntries(cles.map((c) => [c, m.prestations[c] ?? 0])),
  });
  const a = lignesCascade(completer(avant));
  const b = lignesCascade(completer(apres));
  if (a.length !== b.length || a.some(([l], i) => l !== b[i][0])) {
    throw new Error("cascades non comparables");
  }
  return a.map(([libelle, v], i) => ({ libelle, avant: v, apres: b[i][1], ecart: b[i][1] - v }));
}
