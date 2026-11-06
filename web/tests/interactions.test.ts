import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { avecInteractions, calculer, interactionsNonChiffrees, type MesureSite } from "../lib/scenario.ts";
import type { ReponsesUnitaires } from "../lib/donnees.ts";

const donnees = JSON.parse(readFileSync("donnees/scenario-unitaire.json", "utf-8")) as ReponsesUnitaires;
const ENTREE = 2027;
const croises = Object.entries(donnees.leviers).filter(([, l]) => l.interaction);

const ecart = (mesures: MesureSite[]) => calculer(donnees, mesures, ENTREE).map((l) => l.ecart_solde_primaire.central);
function croise(a: string, x: number, b: string, y: number): number[] {
  const ensemble = ecart([{ levier: a, valeur: x }, { levier: b, valeur: y }]);
  const seulA = ecart([{ levier: a, valeur: x }]);
  const seulB = ecart([{ levier: b, valeur: y }]);
  return ensemble.map((e, i) => e - seulA[i] - seulB[i]);
}

test("les termes croisés exportés nomment deux leviers exportés", () => {
  assert.ok(croises.length >= 3);
  for (const [id, l] of croises) {
    for (const levier of l.interaction ?? []) assert.ok(levier in donnees.leviers, `${id} : ${levier}`);
  }
});

test("terme croisé proportionnel au produit des réglages, nul si l'un est à zéro", () => {
  for (const [, l] of croises) {
    const [a, b] = l.interaction as [string, string];
    const un = croise(a, 1, b, 1);
    const autre = croise(a, -2, b, 1.5);
    assert.ok(un.some((v) => Math.abs(v) > 0), `${a} × ${b}`);
    un.forEach((v, i) => assert.ok(Math.abs(autre[i] + 3 * v) < 1e-9));
    assert.ok(croise(a, 1, b, 0).every((v) => v === 0));
  }
});

test("avecInteractions n'ajoute un terme que pour deux leviers réglés", () => {
  const [id, l] = croises[0];
  const [a, b] = l.interaction as [string, string];
  assert.deepEqual(avecInteractions(donnees, [{ levier: a, valeur: 2 }]).length, 1);
  const m = avecInteractions(donnees, [{ levier: a, valeur: 2 }, { levier: b, valeur: -1 }]);
  assert.deepEqual(m[2], { levier: id, valeur: -2 });
});

test("interactions non chiffrées : signalées seulement quand les deux côtés sont réglés", () => {
  assert.deepEqual(interactionsNonChiffrees(donnees, [{ levier: "tva_taux_normal", valeur: 1 }]), []);
  assert.deepEqual(
    interactionsNonChiffrees(donnees, [
      { levier: "tva_taux_normal", valeur: 1 },
      { levier: "accise_gazole", valeur: 2 },
    ]),
    ["accises_tva"],
  );
  assert.deepEqual(
    interactionsNonChiffrees(donnees, [
      { levier: "tva_taux_normal", valeur: 1 },
      { levier: "accise_gazole", valeur: 0 },
    ]),
    [],
  );
});

test("chaque interaction a son texte", async () => {
  const textes = JSON.parse(readFileSync("messages/fr.json", "utf-8"));
  for (const [id] of croises) assert.ok(textes.simulateur.interactions.chiffrees[id], id);
  for (const p of donnees.interactions_non_chiffrees ?? [])
    assert.ok(textes.simulateur.interactions.mecanismes[p.mecanisme], p.mecanisme);
});
