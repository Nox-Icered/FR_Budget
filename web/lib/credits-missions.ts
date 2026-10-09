// Leviers « crédits par mission » (moteur/src/fr_budget/scenario.py) : variation de x % des
// crédits d'une mission. Les missions réglées deviennent au plus deux mesures sur le levier
// générique « credits_missions » (hausse de 1 Md€ de 2025) : la somme des hausses et la somme
// des baisses, pour que chaque borne de la fourchette reste celle du moteur.
import type { CatalogueCreditsMissions } from "./donnees";
import type { MesureSite } from "./scenario";

export const LEVIER_GENERIQUE_CREDITS = "credits_missions";

export function mesuresCreditsMissions(
  catalogue: CatalogueCreditsMissions,
  reglages: Record<string, number>,
): MesureSite[] {
  let hausses = 0;
  let baisses = 0;
  for (const m of catalogue.missions) {
    // rendement_pourcent est l'effet d'une hausse d'un pour cent (négatif) : la valeur du
    // levier générique, en Md€ de hausse, en est l'opposé.
    const valeur = -(reglages[m.identifiant] ?? 0) * m.rendement_pourcent;
    if (valeur > 0) hausses += valeur;
    if (valeur < 0) baisses += valeur;
  }
  return [hausses, baisses]
    .filter((v) => v !== 0)
    .map((valeur) => ({ levier: LEVIER_GENERIQUE_CREDITS, valeur }));
}
