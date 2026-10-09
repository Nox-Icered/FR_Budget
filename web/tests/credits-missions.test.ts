import { test } from "node:test";
import assert from "node:assert/strict";
import { mesuresCreditsMissions, LEVIER_GENERIQUE_CREDITS } from "../lib/credits-missions.ts";
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
