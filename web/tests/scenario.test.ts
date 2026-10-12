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
  const [, l] = calculer(donnees, [{ levier: "l", valeur: 0 }], 2027);
  assert.deepEqual(l.dette, { bas: 101, central: 101, haut: 103 });
  assert.equal(l.ecart_dette.central, 0);
});

test("niveau = base + x * unité, bornes = extrêmes, ordre conservé pour x négatif", () => {
  const [, l] = calculer(donnees, [{ levier: "l", valeur: -2 }], 2027);
  assert.equal(l.dette.central, 103);
  assert.equal(l.dette.haut, 105);
  assert.ok(Math.abs(l.ecart_dette.bas - 1.8) < 1e-12);
  assert.ok(Math.abs(l.ecart_dette.haut - 2.2) < 1e-12);
  assert.ok(l.ecart_solde_primaire.bas <= l.ecart_solde_primaire.central);
});

test("deux leviers s'additionnent", () => {
  const deux = { ...donnees, leviers: { ...donnees.leviers, m: donnees.leviers.l } };
  const [, a] = calculer(deux, [{ levier: "l", valeur: 1 }], 2027);
  const [, b] = calculer(deux, [{ levier: "l", valeur: 1 }, { levier: "m", valeur: 2 }], 2027);
  assert.ok(Math.abs(b.ecart_dette.central - 3 * a.ecart_dette.central) < 1e-12);
});

test("mesures de signes opposés : bornes combinées comme dans le moteur", () => {
  // Moteur (fr_budget.scenario) : borne basse = somme des bornes basses de chaque mesure,
  // une mesure négative prenant sa réponse haute. +1 et -1 sur des réponses 0,9 à 1,1 :
  // écart central 0, bornes -0,2 et +0,2.
  const deux = { ...donnees, leviers: { ...donnees.leviers, m: donnees.leviers.l } };
  const [, l] = calculer(deux, [{ levier: "l", valeur: 1 }, { levier: "m", valeur: -1 }], 2027);
  assert.ok(Math.abs(l.ecart_solde_primaire.central) < 1e-12);
  assert.ok(Math.abs(l.ecart_solde_primaire.bas + 0.2) < 1e-12);
  assert.ok(Math.abs(l.ecart_solde_primaire.haut - 0.2) < 1e-12);
});

// Croissance : supplément de 0,5 point de dette par unité et par point de multiplicateur sur
// toutes les trajectoires ; multiplicateur 0,4 (bas 0,2, haut 0,6).
const avecCroissance: ReponsesUnitaires = {
  ...donnees,
  leviers: {
    l: {
      ...donnees.leviers.l,
      multiplicateur: { bas: 0.2, central: 0.4, haut: 0.6 },
      reponses: {
        "2027": {
          ...donnees.leviers.l.reponses["2027"],
          croissance_dette: [
            [0, 0.5],
            [0, 0.5],
            [0, 0.5],
            [0, 0.5],
          ],
          croissance_solde: [
            [0, -0.2],
            [0, -0.2],
            [0, -0.2],
            [0, -0.2],
          ],
        },
      },
    },
  },
};

test("croissance désactivée par défaut", () => {
  assert.deepEqual(
    calculer(avecCroissance, [{ levier: "l", valeur: 1 }], 2027),
    calculer(donnees, [{ levier: "l", valeur: 1 }], 2027),
  );
});

test("croissance : unité + m * supplément, coins du multiplicateur dans la fourchette", () => {
  const [, l] = calculer(avecCroissance, [{ levier: "l", valeur: 1 }], 2027, true);
  // Central : -1 + 0,4 x 0,5 = -0,8. Coins : -0,9 + 0,2 x 0,5 = -0,8 ; -1,1 + 0,1 = -1,0 ;
  // -0,9 + 0,3 = -0,6 ; -1,1 + 0,3 = -0,8.
  assert.ok(Math.abs(l.ecart_dette.central + 0.8) < 1e-12);
  assert.ok(Math.abs(l.ecart_dette.bas + 1.0) < 1e-12);
  assert.ok(Math.abs(l.ecart_dette.haut + 0.6) < 1e-12);
  assert.ok(Math.abs(l.ecart_solde_primaire.central - 0.92) < 1e-12);
  // Niveaux : la variante de baseline (103) avec l'effet central.
  assert.ok(Math.abs(l.dette.haut - 102.2) < 1e-12);
});
