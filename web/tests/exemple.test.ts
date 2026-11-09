import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { COTES, construireExemple, type ChoixExemple } from "../lib/exemple.ts";
import { niveau, type Objectif } from "../lib/objectif.ts";
import { LEVIERS_PUBLICS } from "../lib/etat.ts";
import type { ReponsesUnitaires } from "../lib/donnees.ts";

const donnees = JSON.parse(readFileSync("donnees/scenario-unitaire.json", "utf-8")) as ReponsesUnitaires;
const ENTREE = 2027;
const PAS = Object.fromEntries(LEVIERS_PUBLICS.map((l) => [l.id, l.pas]));
const sans = (o: Objectif) => niveau(donnees, "tva_taux_normal", 0, ENTREE, o, "central");
const contribution = (levier: string, valeur: number, o: Objectif) =>
  niveau(donnees, levier, valeur, ENTREE, o, "central") - sans(o);

function objectif(ecart: number, indicateur: Objectif["indicateur"] = "dette"): Objectif {
  const o: Objectif = { indicateur, annee: 2040, cible: 0 };
  return { ...o, cible: sans(o) + ecart };
}

function choix(leviers: string[], partRecettes: number, o: Objectif): ChoixExemple {
  return { leviers, partRecettes, entree: ENTREE, objectif: o, pas: PAS };
}

test("chaque mesure du simulateur est rangée en recette ou en dépense", () => {
  for (const { id } of LEVIERS_PUBLICS) assert.ok(id in COTES, id);
});

test("l'exemple atteint la cible après arrondi au pas, dans le simulateur", () => {
  const o = objectif(-2);
  const e = construireExemple(donnees, choix(["tva_taux_normal", "csg_activite", "remunerations_point_indice", "remunerations_effectifs"], 0.5, o));
  assert.deepEqual(e.problemes, []);
  assert.ok(e.atteint !== null && e.atteint.central <= o.cible + 1e-9, `${e.atteint?.central} / ${o.cible}`);
  for (const m of e.mesures) {
    const n = Math.round(m.valeur / PAS[m.levier]);
    assert.ok(Math.abs(m.valeur - n * PAS[m.levier]) < 1e-9, `${m.levier} au pas`);
  }
});

test("parts égales de chaque côté avant arrondi, hors limites de curseur", () => {
  const o = objectif(-1);
  const e = construireExemple(donnees, choix(["tva_taux_normal", "csg_activite", "remunerations_point_indice", "remunerations_effectifs"], 0.3, o));
  const parCote = (cote: "recettes" | "depenses") => e.mesures.filter((m) => m.cote === cote);
  for (const [cote, part] of [["recettes", 0.3], ["depenses", 0.7]] as const) {
    for (const m of parCote(cote)) {
      assert.ok(Math.abs(m.part - (part * -1) / 2) < 1e-9, `${m.levier} : ${m.part}`);
      // La valeur avant arrondi apporte exactement sa part.
      assert.ok(Math.abs(contribution(m.levier, m.valeurExacte, o) - m.part) < 1e-9, m.levier);
    }
  }
});

test("une mesure à la limite de son curseur y reste, le reste va aux autres mesures du même côté", () => {
  // Accise sur l'essence : bornée à ± 14,21 c/l, elle ne peut pas porter la moitié de 3 points.
  const o = objectif(-3);
  const e = construireExemple(donnees, choix(["accise_essences", "tva_taux_normal"], 1, o));
  assert.deepEqual(e.problemes, []);
  const accise = e.mesures.find((m) => m.levier === "accise_essences");
  const tva = e.mesures.find((m) => m.levier === "tva_taux_normal");
  assert.ok(accise?.aLaLimite && tva && !tva.aLaLimite);
  assert.ok(Math.abs(accise.part + tva.part - -3) < 1e-9);
  assert.ok(Math.abs(tva.part) > 1.5);
});

test("côté sans mesure cochée : signalé, aucun exemple", () => {
  const o = objectif(-1);
  const e = construireExemple(donnees, choix(["tva_taux_normal"], 0.5, o));
  assert.deepEqual(e.problemes, ["cote_vide_depenses"]);
  assert.equal(e.atteint, null);
  assert.deepEqual(e.mesures, []);
});

test("côté insuffisant dans les limites des curseurs : signalé, rien ne passe sur l'autre côté", () => {
  // TVA (± 10 points) et accise sur le gazole ne portent pas 60 points de dette.
  const o = objectif(-60);
  const e = construireExemple(donnees, choix(["accise_gazole", "tva_taux_normal", "remunerations_point_indice"], 1, o));
  assert.ok(e.problemes.includes("insuffisant_recettes"), e.problemes.join());
  assert.equal(e.atteint, null);
});

test("âge effectif et âge légal de départ ne se cumulent pas", () => {
  const o = objectif(-1);
  const e = construireExemple(donnees, choix(["retraites_age_depart", "retraites_age_legal"], 0, o));
  assert.deepEqual(e.problemes, ["double_compte"]);
});

test("curseur à 0 % ou 100 % : un seul côté mobilisé", () => {
  const o = objectif(-1);
  const leviers = ["tva_taux_normal", "remunerations_point_indice"];
  const tout = construireExemple(donnees, choix(leviers, 1, o));
  assert.deepEqual(tout.mesures.map((m) => m.levier), ["tva_taux_normal"]);
  const rien = construireExemple(donnees, choix(leviers, 0, o));
  assert.deepEqual(rien.mesures.map((m) => m.levier), ["remunerations_point_indice"]);
  // Un côté sans part n'a pas besoin de mesure cochée.
  assert.deepEqual(construireExemple(donnees, choix(["tva_taux_normal"], 1, o)).problemes, []);
});

test("levier à crans (âge légal) : cran qui atteint au moins sa part", () => {
  const o = objectif(-0.5);
  const e = construireExemple(donnees, choix(["retraites_age_legal", "tva_taux_normal"], 0.5, o));
  assert.deepEqual(e.problemes, []);
  const age = e.mesures.find((m) => m.levier === "retraites_age_legal");
  assert.ok(age && String(age.valeur) in (donnees.leviers.retraites_age_legal.grille ?? {}));
  assert.ok(e.atteint !== null && e.atteint.central <= o.cible + 1e-9);
});

test("solde primaire et cible au-dessus du niveau sans mesure : mêmes règles, signe inverse", () => {
  const o = objectif(-0.3, "solde_primaire");
  const e = construireExemple(donnees, choix(["tva_taux_normal", "remunerations_point_indice"], 0.5, o));
  assert.deepEqual(e.problemes, []);
  assert.ok(e.mesures.length === 2 && e.mesures.every((m) => m.part < 0));
  assert.ok(e.atteint !== null && e.atteint.central <= o.cible + 1e-9);
});

test("fourchette du résultat : basse ≤ centrale ≤ haute", () => {
  const e = construireExemple(donnees, choix(["tva_taux_normal", "remunerations_point_indice"], 0.5, objectif(-1)));
  assert.ok(e.atteint && e.atteint.bas <= e.atteint.central && e.atteint.central <= e.atteint.haut);
});

test("progression de l'ONDAM et mesures qu'il contient : refusées ensemble, comme dans le simulateur", async () => {
  const { exclue, incompatibles } = await import("../lib/exemple.ts");
  const o = objectif(-1);
  for (const autre of [
    "franchises_participations",
    "ij_plafond_smic",
    "ticket_moderateur_consultations",
    "ticket_moderateur_dentaire",
  ]) {
    const e = construireExemple(donnees, choix(["ondam_progression", autre], 0, o));
    assert.deepEqual(e.problemes, ["double_compte"]);
    assert.ok(exclue(autre, ["ondam_progression"]));
    assert.ok(exclue("ondam_progression", [autre]));
  }
  assert.ok(!incompatibles(["franchises_participations", "ij_plafond_smic"]));
  assert.ok(!exclue("tva_taux_normal", ["ondam_progression"]));
});
