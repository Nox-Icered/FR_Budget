import { test } from "node:test";
import assert from "node:assert/strict";
import {
  decoder,
  encoder,
  problemes,
  versCsv,
  versJson,
  type EtatScenario,
} from "../lib/etat.ts";
import type {
  CatalogueCreditsMissions,
  CatalogueDepensesFiscales,
  ReponsesUnitaires,
} from "../lib/donnees.ts";

const etat: EtatScenario = {
  annee: 2027,
  leviers: { tva_taux_normal: 1, accise_gazole: 0, csg_activite: -0.5 },
  parImpot: { impot_revenu: 10 },
  parDepense: { "110201": 50 },
  parMission: { justice: -5 },
  version: "a.b.c",
};

test("aller-retour par le lien, réglages nuls omis", () => {
  const lien = encoder(etat);
  assert.ok(!lien.includes("accise_gazole"));
  const relu = decoder(`https://exemple.fr/simulateur/?${lien}`);
  assert.deepEqual(relu, { ...etat, leviers: { tva_taux_normal: 1, csg_activite: -0.5 } });
});

test("un lien illisible est refusé", () => {
  assert.equal(decoder("?a=2027&l=tva_taux_normal:abc"), null);
  assert.equal(decoder("?l=tva_taux_normal:1"), null);
});

const levier = (bornes: [number, number]) => ({
  statut: "beta" as const,
  rendement_unitaire: 1,
  effet_unitaire: 1,
  taux_reference: 0,
  bornes,
  reponses: { "2027": { unite_dette: [[0]], unite_solde: [[0]] } },
});
const donnees = {
  unite: "% du PIB",
  annee_reference: 2025,
  annees: [2027],
  base_dette: [[100]],
  base_solde: [[0]],
  indices_effet: [0, 0, 0],
  leviers: {
    tva_taux_normal: levier([-10, 10]),
    remunerations_point_indice: levier([-5, 5]),
    indexation_pensions_prestations: levier([-2, 1]),
  },
} as unknown as ReponsesUnitaires;
const catalogue = {
  impots: { impot_revenu: { levier: "depenses_fiscales_impot_revenu", cout: 1 } },
  depenses: [{ code: "110201", impot: "impot_revenu", rendement_pourcent: 0.01 }],
} as unknown as CatalogueDepensesFiscales;
const missions = {
  bornes: [-20, 20],
  missions: [
    { identifiant: "justice", rendement_pourcent: -0.1 },
    { identifiant: "solidarite_insertion_et_egalite_des_chances", rendement_pourcent: -0.3 },
  ],
} as unknown as CatalogueCreditsMissions;

const base = (e: Partial<EtatScenario>): EtatScenario => ({
  annee: 2027,
  leviers: {},
  parImpot: {},
  parDepense: {},
  parMission: {},
  ...e,
});

test("contrôles repris du moteur", () => {
  assert.deepEqual(problemes(base({ leviers: { tva_taux_normal: 1 } }), donnees, catalogue, missions), []);
  assert.deepEqual(problemes(base({ annee: 2099 }), donnees, catalogue, missions), ["annee"]);
  assert.deepEqual(problemes(base({ leviers: { inconnu: 1 } }), donnees, catalogue, missions), [
    "levier_inconnu",
  ]);
  assert.deepEqual(problemes(base({ leviers: { tva_taux_normal: 11 } }), donnees, catalogue, missions), [
    "hors_bornes",
  ]);
  assert.deepEqual(
    problemes(
      base({ leviers: { remunerations_point_indice: 1 }, parMission: { justice: -1 } }),
      donnees,
      catalogue,
      missions,
    ),
    ["double_compte"],
  );
  assert.deepEqual(
    problemes(
      base({
        leviers: { indexation_pensions_prestations: -1 },
        parMission: { solidarite_insertion_et_egalite_des_chances: -1 },
      }),
      donnees,
      catalogue,
      missions,
    ),
    ["double_compte"],
  );
  assert.deepEqual(
    problemes(base({ parImpot: { impot_revenu: 10 }, parDepense: { "110201": 5 } }), donnees, catalogue, missions),
    ["double_compte"],
  );
});

test("exports CSV et JSON", () => {
  const f = { bas: -1, central: 0, haut: 1 };
  const lignes = [{ annee: 2027, dette: f, solde_primaire: f, ecart_dette: f, ecart_solde_primaire: f }];
  const csv = versCsv([{ nom: "A", etat, lignes }]);
  assert.equal(csv.split("\n")[1], "A;2027;-1;0;1;-1;0;1;-1;0;1");
  const json = JSON.parse(versJson([{ nom: "A", etat, lignes }], { moteur: "m", registres: "r", donnees: "d" }));
  assert.equal(json.scenarios[0].lien.startsWith("?a=2027"), true);
  assert.equal(json.version.moteur, "m");
});
