import { test } from "node:test";
import assert from "node:assert/strict";
import { espacer, miseEnPage, regrouper } from "../lib/sankey.ts";

const ressources = [
  { id: "a", libelle: "A", montant: 60 },
  { id: "b", libelle: "B", montant: 40 },
];
const emplois = [
  { id: "x", libelle: "X", montant: 70 },
  { id: "y", libelle: "Y", montant: 20 },
  { id: "z", libelle: "Z", montant: 6 },
  { id: "w", libelle: "W", montant: 4 },
];

test("les petits emplois sont regroupés, le total ne change pas", () => {
  const r = regrouper(emplois, 0.1, (n) => `Autres (${n})`);
  assert.deepEqual(r.map((f) => f.id), ["x", "y", "autres"]);
  assert.equal(r.at(-1)!.montant, 10);
  assert.equal(r.at(-1)!.libelle, "Autres (2)");
});

test("chaque côté du diagramme a la hauteur de la barre centrale, sans recouvrement", () => {
  const m = miseEnPage(ressources, emplois, 200, 10);
  const echelle = m.centre.hauteur / m.total;
  for (const cote of [m.gauche, m.droite]) {
    assert.ok(Math.abs(cote.reduce((s, n) => s + n.hauteur, 0) - m.centre.hauteur) < 1e-9);
    cote.slice(1).forEach((n, i) => assert.ok(n.y >= cote[i].y + cote[i].hauteur));
    cote.forEach((n) => assert.ok(Math.abs(n.hauteur - n.montant * echelle) < 1e-9));
  }
  // Les liens remplissent la barre centrale de haut en bas, sans trou.
  const fin = m.liensDroite.at(-1)!;
  assert.ok(Math.abs(fin.y0 + fin.epaisseur - (m.centre.y + m.centre.hauteur)) < 1e-9);
});

test("espacer : étiquettes trop proches repoussées vers le bas, les autres inchangées", () => {
  assert.deepEqual(espacer([10, 100, 105, 108], 15), [10, 100, 115, 130]);
  assert.deepEqual(espacer([0, 50], 15), [0, 50]);
});
