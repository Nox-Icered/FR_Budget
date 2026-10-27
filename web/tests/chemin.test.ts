import { test } from "node:test";
import assert from "node:assert/strict";
import { chemin, normaliser } from "../lib/chemin.ts";
import { adresseReponses } from "../lib/chargement.ts";

test("préfixe vide : adresses inchangées (site à la racine du domaine)", () => {
  assert.equal(normaliser(undefined), "");
  assert.equal(normaliser(" "), "");
  assert.equal(chemin("/sources/#x", ""), "/sources/#x");
  assert.equal(adresseReponses("a.b.c"), "/donnees/scenario-unitaire.a.b.c.json");
});

test("préfixe GitHub Pages : ajouté devant chaque adresse, barres normalisées", () => {
  assert.equal(normaliser("/FR_Budget"), "/FR_Budget");
  assert.equal(normaliser("FR_Budget/"), "/FR_Budget");
  assert.equal(chemin("/validation/", normaliser("/FR_Budget/")), "/FR_Budget/validation/");
});
