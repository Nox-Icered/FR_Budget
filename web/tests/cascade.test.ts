import { test } from "node:test";
import assert from "node:assert/strict";
import {
  comparaisonsEnFourchette,
  lignesComparees,
  lignesEnFourchette,
  type LignesCascade,
} from "../lib/cascade.ts";

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

test("fourchette selon le revenu : extrêmes ligne par ligne, prestation absente à zéro", () => {
  const bas = { ...BASE, salaire_brut: 23900, prestations: { ppa: 1050, asf: 5 } };
  const haut = { ...BASE, salaire_brut: 24000, prestations: {} };
  const lignes = Object.fromEntries(lignesEnFourchette(BASE, [bas, haut]).map((l) => [l.libelle, l]));
  assert.deepEqual(
    { ...lignes["Salaire brut"] },
    { libelle: "Salaire brut", valeur: 24000, bas: 23900, haut: 24000 },
  );
  assert.equal(lignes["Prime d'activité"].bas, 0);
  assert.equal(lignes["Prime d'activité"].haut, 1050);
  assert.equal(lignes["Allocation de soutien familial"].valeur, 0);
});

test("écart en fourchette : écart central de la première paire, extrêmes sur les paires", () => {
  const apres = { ...BASE, net_avant_impot: 18800 };
  const basAvant = { ...BASE, net_avant_impot: 18900 };
  const basApres = { ...BASE, net_avant_impot: 18650 };
  const lignes = comparaisonsEnFourchette([
    [BASE, apres],
    [basAvant, basApres],
  ]);
  const net = lignes.find((l) => l.libelle === "Salaire net avant impôt");
  assert.ok(net);
  assert.equal(net.ecart, -200);
  assert.equal(net.ecart_bas, -250);
  assert.equal(net.ecart_haut, -200);
});
