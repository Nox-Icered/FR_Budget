import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  decoderBareme,
  effetBareme,
  encoderBareme,
  impotParPart,
  mesureBareme,
  problemesBareme,
  type DonneesBareme,
} from "../lib/bareme-ir.ts";

const donnees = JSON.parse(readFileSync("donnees/bareme-ir.json", "utf-8")) as DonneesBareme;

test("barème simple : impôt par part", () => {
  const b = { seuils: [0, 10000, 20000], taux: [0, 0.1, 0.3], decote: null };
  assert.equal(impotParPart(b, 5000), 0);
  assert.equal(impotParPart(b, 30000), 1000 + 3000);
});

test("le calcul du site redonne celui du moteur sur les barèmes de contrôle", () => {
  for (const c of donnees.controles) {
    const f = effetBareme(donnees, c.bareme);
    for (const borne of ["bas", "central", "haut"] as const) {
      const ecart = Math.abs(f[borne] - c.effet[borne]);
      assert.ok(ecart <= 1e-3 * Math.max(1, Math.abs(c.effet[borne])), `${c.nom} ${borne} : ${f[borne]} / ${c.effet[borne]}`);
    }
  }
});

test("barème de référence : aucun effet, aucune mesure", () => {
  const f = effetBareme(donnees, donnees.bareme_reference);
  assert.equal(f.central, 0);
  assert.deepEqual(mesureBareme(donnees, donnees.bareme_reference), []);
});

test("lien : aller-retour du barème", () => {
  const b = { ...donnees.controles[0].bareme };
  assert.deepEqual(decoderBareme(encoderBareme(b)), b);
  const sans = { ...b, decote: null };
  assert.deepEqual(decoderBareme(encoderBareme(sans)), sans);
  assert.equal(decoderBareme("n'importe quoi"), null);
});

test("barème invalide : seuils non croissants, taux hors de 0 à 100 %", () => {
  assert.deepEqual(problemesBareme({ seuils: [0, 20000, 10000], taux: [0, 0.1, 0.2], decote: null }), ["seuils"]);
  assert.deepEqual(problemesBareme({ seuils: [0, 10000], taux: [0, 1.5], decote: null }), ["taux"]);
});

test("état du simulateur : barème dans le lien, double compte avec la revalorisation des seuils", async () => {
  const { decoder, encoder, problemes, mesures } = await import("../lib/etat.ts");
  const bareme = donnees.controles[0].bareme;
  const etat = { annee: 2027, leviers: {}, parImpot: {}, parDepense: {}, parMission: {}, bareme };
  const relu = decoder(encoder(etat));
  assert.deepEqual(relu?.bareme, bareme);
  const catalogue = { impots: {}, depenses: [] } as never;
  const missions = { missions: [], bornes: [-10, 10] } as never;
  const unitaires = { leviers: {} } as never;
  const avecSeuils = { ...etat, leviers: { ir_seuils_bareme: 1 } };
  assert.ok(problemes(avecSeuils, unitaires, catalogue, missions).includes("double_compte"));
  const m = mesures(etat, { impots: {}, depenses: [] } as never, { missions: [] } as never, donnees);
  assert.equal(m.length, 1);
  assert.equal(m[0].levier, "ir_bareme");
  assert.ok(Math.abs(m[0].valeur - donnees.controles[0].effet.central) < 1e-3);
});

test("barème hors des bornes du levier générique : signalé, pas de mesure", async () => {
  const { horsBornes } = await import("../lib/bareme-ir.ts");
  const ref = donnees.bareme_reference;
  const extreme = { ...ref, taux: ref.taux.map(() => 1) };
  assert.ok(horsBornes(donnees, extreme));
  assert.deepEqual(mesureBareme(donnees, extreme), []);
  assert.ok(!horsBornes(donnees, donnees.controles[0].bareme));
});

test("ménages types : le calcul du site redonne celui du moteur (lui-même égal à OpenFisca)", async () => {
  const { ecartMenage } = await import("../lib/bareme-ir.ts");
  for (const c of donnees.controles) {
    for (const [ident, attendu] of Object.entries(donnees.menages_types.controles[c.nom])) {
      assert.ok(Math.abs(ecartMenage(donnees, c.bareme, ident) - attendu) < 0.5, `${c.nom} ${ident}`);
    }
  }
  assert.equal(ecartMenage(donnees, donnees.bareme_reference, "cadre_p95"), 0);
});
