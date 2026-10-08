import { test } from "node:test";
import assert from "node:assert/strict";
import { texte, nombre } from "../lib/textes.ts";

test("texte remplace les variables", () => {
  assert.equal(texte("accueil.annee", { annee: 2025 }), "Année 2025");
});

test("texte manquant : erreur, pas de chaîne vide", () => {
  assert.throws(() => texte("accueil.inexistant"), /texte manquant/);
});

test("variable manquante : erreur", () => {
  assert.throws(() => texte("accueil.annee"), /variable manquante/);
});

test("nombre au format français, une décimale", () => {
  assert.equal(nombre(3460.1).replace(/\s/g, " "), "3 460,1");
});
