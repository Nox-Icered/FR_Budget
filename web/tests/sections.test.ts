import { test } from "node:test";
import assert from "node:assert/strict";
import { correspond, reglees, SECTIONS } from "../lib/sections.ts";
import { LEVIERS_PUBLICS } from "../lib/etat.ts";

test("chaque levier publié est dans une seule section", () => {
  const ranges = SECTIONS.flatMap((s) => s.leviers);
  assert.equal(new Set(ranges).size, ranges.length);
  assert.deepEqual([...ranges].sort(), LEVIERS_PUBLICS.map((l) => l.id).sort());
});

test("recherche sans accents ni casse, tous les mots", () => {
  assert.ok(correspond("Durée d'indemnisation du chômage", "CHOMAGE duree"));
  assert.ok(!correspond("Taux normal de TVA", "tva chomage"));
  assert.ok(correspond("Taux normal de TVA", "  "));
});

test("nombre de leviers réglés", () => {
  assert.equal(reglees(["a", "b", "c"], { a: 1, b: 0 }), 1);
});
