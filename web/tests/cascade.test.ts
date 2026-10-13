import { test } from "node:test";
import assert from "node:assert/strict";
import { lignesComparees, type LignesCascade } from "../lib/cascade.ts";

const BASE: LignesCascade = {
  cout_employeur: 30000,
  salaire_brut: 24000,
  net_avant_impot: 19000,
  pension_brute: 0,
  pension_nette: 0,
  revenu_independant_brut: 0,
  cotisations_independant: 0,
  csg_crds_independant: 0,
  revenu_independant_net: 0,
  impot_revenu: 500,
  prestations: { ppa: 1000 },
  net_apres_impot: 19500,
};

test("écart ligne par ligne, prestations réunies", () => {
  const apres = {
    ...BASE,
    net_avant_impot: 18800,
    impot_revenu: 480,
    prestations: { ppa: 1100, asf: 10 },
    net_apres_impot: 19430,
  };
  const lignes = lignesComparees(BASE, apres);
  const parLibelle = Object.fromEntries(lignes.map((l) => [l.libelle, l]));
  assert.equal(parLibelle["Salaire net avant impôt"].ecart, -200);
  // Impôt affiché en négatif : une baisse d'impôt est un écart positif.
  assert.equal(parLibelle["Impôt sur le revenu (dû sur ces revenus)"].ecart, 20);
  assert.equal(parLibelle["Prime d'activité"].ecart, 100);
  assert.equal(parLibelle["Allocation de soutien familial"].avant, 0);
  assert.equal(parLibelle["Allocation de soutien familial"].apres, 10);
});
