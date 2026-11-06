import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { repartitionDeciles } from "../lib/deciles.ts";
import type { Deciles } from "../lib/donnees.ts";

const donnees = JSON.parse(readFileSync("donnees/deciles.json", "utf-8")) as Deciles;

test("aucune mesure : pas de répartition", () => {
  assert.equal(repartitionDeciles(donnees, []), null);
  assert.equal(repartitionDeciles(donnees, [{ levier: "tva_taux_normal", valeur: 0 }]), null);
});

test("la somme des dixièmes redonne l'effet national (valeur centrale)", () => {
  const r = repartitionDeciles(donnees, [{ levier: "tva_taux_normal", valeur: 1 }]);
  assert.ok(r);
  const total = r.milliards.reduce((s, f) => s + f.central, 0);
  assert.ok(Math.abs(total + donnees.leviers.tva_taux_normal.rendement.central) < 1e-9);
  for (const f of r.eurosParUc) assert.ok(f.bas <= f.central && f.central <= f.haut && f.haut < 0);
});

test("parts de chaque variante : dix dixièmes qui somment à un", () => {
  for (const [id, l] of Object.entries(donnees.leviers)) {
    for (const p of [l.centrale, ...l.variantes]) {
      assert.equal(p.length, 10, id);
      assert.ok(Math.abs(p.reduce((s, x) => s + x, 0) - 1) < 1e-9, id);
    }
  }
});

test("mesures non réparties : signalées, sans effet dans le tableau", () => {
  const r = repartitionDeciles(donnees, [{ levier: "remunerations_point_indice", valeur: 1 }]);
  assert.ok(r);
  assert.deepEqual(r.nonRepartis, ["remunerations_point_indice"]);
  assert.ok(r.milliards.every((f) => f.central === 0));
  assert.ok(donnees.non_repartis.includes("remunerations_point_indice"));
});

test("terme croisé ajouté quand ses deux leviers sont réglés", () => {
  const a = repartitionDeciles(donnees, [{ levier: "indexation_pensions_prestations", valeur: 1 }]);
  const b = repartitionDeciles(donnees, [{ levier: "csg_retraites", valeur: 1 }]);
  const ab = repartitionDeciles(donnees, [
    { levier: "indexation_pensions_prestations", valeur: 1 },
    { levier: "csg_retraites", valeur: 1 },
  ]);
  assert.ok(a && b && ab);
  const somme = (r: typeof a) => r.milliards.reduce((s, f) => s + f.central, 0);
  assert.ok(Math.abs(somme(ab) - somme(a) - somme(b)) > 0);
});

test("chaque dixième a son nom", () => {
  const textes = JSON.parse(readFileSync("messages/fr.json", "utf-8"));
  for (let i = 1; i <= 10; i++) assert.ok(textes.simulateur.deciles.noms[String(i)]);
});
