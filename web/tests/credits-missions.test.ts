import { test } from "node:test";
import assert from "node:assert/strict";
import {
  auPas,
  equivalentMission,
  mesuresCreditsMissions,
  LEVIER_GENERIQUE_CREDITS,
} from "../lib/credits-missions.ts";
import type { CatalogueCreditsMissions } from "../lib/donnees.ts";

const catalogue: CatalogueCreditsMissions = {
  source: "s",
  annee_credits: 2026,
  unite_credits: "Md€",
  bornes: [-20, 20],
  missions: [
    { identifiant: "a", libelle: "A", credits: 10, rendement_pourcent: -0.1 },
    { identifiant: "b", libelle: "B", credits: 20, rendement_pourcent: -0.2 },
    { identifiant: "c", libelle: "C", credits: 5, rendement_pourcent: -0.05 },
  ],
};

test("hausses et baisses forment deux mesures génériques", () => {
  const m = mesuresCreditsMissions(catalogue, { a: 10, b: -5, c: 2 });
  assert.equal(m.length, 2);
  assert.ok(m.every((x) => x.levier === LEVIER_GENERIQUE_CREDITS));
  assert.ok(Math.abs(m[0].valeur - (10 * 0.1 + 2 * 0.05)) < 1e-12);
  assert.ok(Math.abs(m[1].valeur - -5 * 0.2) < 1e-12);
});

test("aucune mesure sans réglage", () => {
  assert.deepEqual(mesuresCreditsMissions(catalogue, { a: 0 }), []);
});

test("aide au chiffrage : un programme de 25 % de la mission, +10 %, donne +2,5 % de la mission", () => {
  assert.equal(equivalentMission(25, 100, 10), 2.5);
  assert.equal(auPas(2.5, 1, [-20, 20]), 3);
  assert.equal(auPas(-0.4, 1, [-20, 20]), 0);
  assert.equal(auPas(35, 1, [-20, 20]), 20);
});
