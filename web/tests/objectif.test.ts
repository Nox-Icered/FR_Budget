import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { auPas, fourchetteValeur, niveau, resoudre, type Objectif } from "../lib/objectif.ts";
import type { ReponsesUnitaires } from "../lib/donnees.ts";

const donnees = JSON.parse(readFileSync("donnees/scenario-unitaire.json", "utf-8")) as ReponsesUnitaires;
const ENTREE = 2027;

test("la valeur trouvée redonne la cible dans le simulateur (leviers linéaires)", () => {
  for (const levier of ["tva_taux_normal", "csg_activite", "ir_plafond_quotient_familial"]) {
    const sans = niveau(donnees, levier, 0, ENTREE, { indicateur: "dette", annee: 2040, cible: 0 }, "central");
    // Baisse de 0,2 point : à la portée des trois leviers dans leurs bornes.
    const objectif: Objectif = { indicateur: "dette", annee: 2040, cible: sans - 0.2 };
    const s = resoudre(donnees, levier, ENTREE, objectif);
    const v = s.parBorne.central;
    assert.ok(v !== null, levier);
    const atteint = niveau(donnees, levier, v, ENTREE, objectif, "central");
    assert.ok(Math.abs(atteint - objectif.cible) < 1e-6, `${levier} : ${atteint}`);
  }
});

test("solde primaire : même principe", () => {
  const objectif0: Objectif = { indicateur: "solde_primaire", annee: 2030, cible: 0 };
  const sans = niveau(donnees, "tva_taux_normal", 0, ENTREE, objectif0, "central");
  const objectif = { ...objectif0, cible: sans + 0.2 };
  const v = resoudre(donnees, "tva_taux_normal", ENTREE, objectif).parBorne.central;
  assert.ok(v !== null && v > 0);
  assert.ok(Math.abs(niveau(donnees, "tva_taux_normal", v, ENTREE, objectif, "central") - objectif.cible) < 1e-6);
});

test("cible hors de portée dans les bornes du levier : aucune valeur", () => {
  const objectif: Objectif = { indicateur: "dette", annee: 2040, cible: 0 };
  const s = resoudre(donnees, "accise_gazole", ENTREE, objectif);
  assert.equal(s.parBorne.central, null);
  assert.equal(fourchetteValeur(s), null);
});

test("levier non linéaire : un cran de la grille qui atteint la cible", () => {
  const levier = "retraites_age_legal";
  const sans = niveau(donnees, levier, 0, ENTREE, { indicateur: "dette", annee: 2046, cible: 0 }, "central");
  const objectif: Objectif = { indicateur: "dette", annee: 2046, cible: sans - 0.5 };
  const v = resoudre(donnees, levier, ENTREE, objectif).parBorne.central;
  assert.ok(v !== null && v > 0);
  assert.ok(String(v) in (donnees.leviers[levier].grille ?? {}));
  assert.ok(niveau(donnees, levier, v, ENTREE, objectif, "central") <= objectif.cible + 1e-9);
});

test("fourchette ordonnée et arrondi au pas vers l'extérieur", () => {
  const sans = niveau(donnees, "tva_taux_normal", 0, ENTREE, { indicateur: "dette", annee: 2040, cible: 0 }, "central");
  const f = fourchetteValeur(resoudre(donnees, "tva_taux_normal", ENTREE, { indicateur: "dette", annee: 2040, cible: sans - 1 }));
  assert.ok(f && f.bas <= f.central && f.central <= f.haut);
  assert.equal(auPas(0.42, 0.1), 0.5);
  assert.equal(auPas(-0.42, 0.1), -0.5);
  assert.equal(auPas(0.5, 0.1), 0.5);
});

test("réglage au pas : jamais hors des limites du curseur, et il atteint la cible", async () => {
  const { reglageAuPas } = await import("../lib/objectif.ts");
  const levier = "is_surtaxe_grandes_entreprises";
  const [, haut] = donnees.leviers[levier].bornes;
  const objectif0: Objectif = { indicateur: "dette", annee: 2040, cible: 0 };
  // Cible atteinte juste sous la borne haute : l'arrondi vers l'extérieur sortirait du curseur.
  const presBorne = niveau(donnees, levier, haut - 0.1, ENTREE, objectif0, "central");
  const objectif = { ...objectif0, cible: presBorne };
  const v = resoudre(donnees, levier, ENTREE, objectif).parBorne.central;
  assert.ok(v !== null);
  const r = reglageAuPas(donnees, levier, 1, ENTREE, objectif, v);
  assert.ok(r === null || r <= haut + 1e-9);
  const sans = niveau(donnees, "tva_taux_normal", 0, ENTREE, objectif0, "central");
  const obj2 = { ...objectif0, cible: sans - 0.2 };
  const v2 = resoudre(donnees, "tva_taux_normal", ENTREE, obj2).parBorne.central;
  const r2 = reglageAuPas(donnees, "tva_taux_normal", 0.1, ENTREE, obj2, v2 ?? 0);
  assert.ok(r2 !== null && niveau(donnees, "tva_taux_normal", r2, ENTREE, obj2, "central") <= obj2.cible + 1e-9);
});
