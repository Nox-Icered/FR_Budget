// Leviers « dépenses fiscales » (moteur/src/fr_budget/scenario.py) : réduction de x % des
// dépenses d'un impôt (un levier par impôt) ou d'une dépense choisie dans le catalogue. Une
// dépense choisie devient une mesure sur le levier générique « depense_fiscale » (1 Md€ de
// 2025) de valeur x * rendement d'un pour cent : le modèle est linéaire.
import type { CatalogueDepensesFiscales, DepenseFiscale, FicheDepense } from "./donnees";
import type { MesureSite } from "./scenario";

export const LEVIER_GENERIQUE = "depense_fiscale";

export function mesuresDepensesFiscales(
  catalogue: CatalogueDepensesFiscales,
  parImpot: Record<string, number>,
  parDepense: Record<string, number>,
): MesureSite[] {
  const mesures: MesureSite[] = Object.entries(parImpot)
    .filter(([, x]) => x !== 0)
    .map(([impot, x]) => ({ levier: catalogue.impots[impot].levier, valeur: x }));
  const total = catalogue.depenses.reduce(
    (somme, d) => somme + (parDepense[d.code] ?? 0) * d.rendement_pourcent,
    0,
  );
  if (total !== 0) mesures.push({ levier: LEVIER_GENERIQUE, valeur: total });
  return mesures;
}

// Recherche sans accents ni casse, sur le numéro ou les mots du libellé et de la finalité.
const normaliser = (s: string) =>
  s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export function rechercher(
  depenses: DepenseFiscale[],
  requete: string,
  maximum: number,
): DepenseFiscale[] {
  const mots = normaliser(requete).split(/\s+/).filter(Boolean);
  if (mots.length === 0) return [];
  return depenses
    .filter((d) => {
      const cible = `${d.code} ${normaliser(d.libelle)} ${normaliser(d.fiche?.finalite ?? "")}`;
      return mots.every((m) => cible.includes(m));
    })
    .slice(0, maximum);
}

// Lignes de la fiche descriptive à afficher (clé du texte, valeur), sans les champs vides ;
// la finalité est toujours présente, « non indiquée » si la fiche n'en donne pas.
export function lignesFiche(fiche: FicheDepense | null | undefined): [string, string][] {
  if (!fiche) return [];
  const lignes: [string, string][] = [
    ["finalite", fiche.finalite],
    ["beneficiaires", fiche.beneficiaires],
    ["creation", fiche.creation],
    ["modification", fiche.modification === fiche.creation ? "" : fiche.modification],
    ["mission", fiche.mission],
    ["reference", fiche.reference],
  ];
  return lignes.filter(([cle, v]) => cle === "finalite" || v !== "");
}
