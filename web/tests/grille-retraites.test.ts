import { test } from "node:test";
import assert from "node:assert/strict";
import { calculer } from "../lib/scenario.ts";
import type { ReponsesUnitaires } from "../lib/donnees.ts";

// Trois trajectoires (centrale, effet bas, effet haut), deux années.
const unite = (x: number) => [
  [x, x],
  [x * 0.5, x * 0.5],
  [x * 2, x * 2],
];
const donnees = {
  unite: "% du PIB",
  annee_reference: 2025,
  annees: [2027, 2028],
  base_dette: [
    [100, 100],
    [100, 100],
    [100, 100],
  ],
  base_solde: [
    [0, 0],
    [0, 0],
    [0, 0],
  ],
  indices_effet: [0, 1, 2],
  leviers: {
    retraites_age_legal: {
      bornes: [-1, 3],
      reponses: { "2027": { unite_dette: unite(-1), unite_solde: unite(1) } },
      grille: {
        "2": { "2027": { unite_dette: unite(-1.5), unite_solde: unite(1.5) } },
        "-1": { "2027": { unite_dette: unite(0.8), unite_solde: unite(-0.8) } },
      },
    },
  },
} as unknown as ReponsesUnitaires;

test("levier non linéaire : réponse exacte du cran, sans multiplier par la valeur", () => {
  const [ligne] = calculer(donnees, [{ levier: "retraites_age_legal", valeur: 2 }], 2027);
  assert.equal(ligne.ecart_solde_primaire.central, 1.5);
});

test("levier non linéaire négatif : les bornes du cran ne s'échangent pas", () => {
  const [ligne] = calculer(donnees, [{ levier: "retraites_age_legal", valeur: -1 }], 2027);
  assert.equal(ligne.ecart_solde_primaire.central, -0.8);
  assert.equal(ligne.ecart_solde_primaire.bas, -1.6);
  assert.equal(ligne.ecart_solde_primaire.haut, -0.4);
});
