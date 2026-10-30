import { test } from "node:test";
import assert from "node:assert/strict";
import {
  lignesFiche,
  mesuresDepensesFiscales,
  rechercher,
  LEVIER_GENERIQUE,
} from "../lib/depenses-fiscales.ts";
import type { CatalogueDepensesFiscales } from "../lib/donnees.ts";

const catalogue: CatalogueDepensesFiscales = {
  source: "s",
  annee_cout: 2026,
  unite_cout: "Md€",
  impots: { impot_revenu: { levier: "depenses_fiscales_impot_revenu", cout: 41 } },
  ordre_impots: ["impot_revenu"],
  impots_exclus: ["tva"],
  depenses: [
    {
      code: "110201",
      impot: "impot_revenu",
      libelle: "Réduction d'impôt au titre des dons",
      cout: 2.2,
      annee_chiffrage: 2026,
      fiabilite: "Très bonne",
      rendement_pourcent: 0.02,
    },
    {
      code: "120202",
      impot: "impot_revenu",
      libelle: "Exonération des indemnités",
      cout: 1,
      annee_chiffrage: 2026,
      fiabilite: "Bonne",
      rendement_pourcent: 0.01,
    },
  ],
};

test("les dépenses choisies s'additionnent sur le levier générique", () => {
  const m = mesuresDepensesFiscales(catalogue, { impot_revenu: 0 }, { "110201": 50, "120202": 100 });
  assert.equal(m.length, 1);
  assert.equal(m[0].levier, LEVIER_GENERIQUE);
  assert.ok(Math.abs(m[0].valeur - (50 * 0.02 + 100 * 0.01)) < 1e-12);
});

test("un curseur par impôt donne une mesure en pourcentage", () => {
  const m = mesuresDepensesFiscales(catalogue, { impot_revenu: 30 }, {});
  assert.deepEqual(m, [{ levier: "depenses_fiscales_impot_revenu", valeur: 30 }]);
});

test("recherche sans accents, par numéro ou par mots", () => {
  assert.deepEqual(
    rechercher(catalogue.depenses, "reduction dons", 10).map((d) => d.code),
    ["110201"],
  );
  assert.deepEqual(rechercher(catalogue.depenses, "1202", 10).map((d) => d.code), ["120202"]);
  assert.deepEqual(rechercher(catalogue.depenses, "  ", 10), []);
});

test("fiche descriptive : champs vides retirés, finalité toujours présente", () => {
  const fiche = {
    finalite: "",
    beneficiaires: "131 000 Ménages",
    creation: "1941",
    modification: "1941",
    reference: "code général des impôts 156-II-5°",
    mission: "",
  };
  assert.deepEqual(lignesFiche(fiche), [
    ["finalite", ""],
    ["beneficiaires", "131 000 Ménages"],
    ["creation", "1941"],
    ["reference", "code général des impôts 156-II-5°"],
  ]);
  assert.deepEqual(lignesFiche(null), []);
});
