import { test } from "node:test";
import assert from "node:assert/strict";
import { calculer } from "../lib/scenario.ts";
import type { ReponsesUnitaires } from "../lib/donnees.ts";

const donnees: ReponsesUnitaires = {
  unite: "% du PIB",
  annee_reference: 2025,
  annees: [2026, 2027],
  base_dette: [
    [100, 101],
    [100, 103],
    [100, 101],
    [100, 101],
  ],
  base_solde: [
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
  ],
  indices_effet: [0, 2, 3],
  leviers: {
    l: {
      statut: "beta",
      rendement_unitaire: 1,
      effet_unitaire: 1,
      taux_reference: 20,
      bornes: [-10, 10],
      reponses: {
        "2027": {
          unite_dette: [
            [0, -1],
            [0, -1],
            [0, -0.9],
            [0, -1.1],
          ],
          unite_solde: [
            [0, 1],
            [0, 1],
            [0, 0.9],
            [0, 1.1],
          ],
        },
      },
    },
  },
};

test("valeur nulle : niveaux de la baseline, écarts nuls", () => {
  const [, l] = calculer(donnees, "l", 0, 2027);
  assert.deepEqual(l.dette, { bas: 101, central: 101, haut: 103 });
  assert.equal(l.ecart_dette.central, 0);
});

test("niveau = base + x * unité, bornes = extrêmes, ordre conservé pour x négatif", () => {
  const [, l] = calculer(donnees, "l", -2, 2027);
  assert.equal(l.dette.central, 103);
  assert.equal(l.dette.haut, 105);
  assert.ok(Math.abs(l.ecart_dette.bas - 1.8) < 1e-12);
  assert.ok(Math.abs(l.ecart_dette.haut - 2.2) < 1e-12);
  assert.ok(l.ecart_solde_primaire.bas <= l.ecart_solde_primaire.central);
});
