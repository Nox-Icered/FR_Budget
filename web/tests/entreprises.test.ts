import { test } from "node:test";
import assert from "node:assert/strict";
import { effetScenario, GROUPES } from "../lib/entreprises.ts";
import type { Entreprises } from "../lib/donnees.ts";

const classe = (id: string, effet: [number, number, number]) => ({
  id,
  libelle: id,
  part: { bas: 0.5, central: 0.5, haut: 0.5 },
  effet: { bas: effet[0], central: effet[1], haut: effet[2] },
  effectifs: 10,
  entreprises: null,
});
const DONNEES: Entreprises = {
  unite: "",
  annee_urssaf: 2024,
  annees_is: [2025, 2024],
  controles: [],
  leviers: [
    {
      id: "cotisations_patronales_taux",
      effet_national: { bas: 2, central: 2, haut: 2 },
      sources: [],
      nomenclatures: { taille: [classe("a", [1, 1, 1]), classe("b", [1, 1, 1])], secteur: [] },
    },
    {
      id: "allegements_generaux",
      effet_national: { bas: -0.4, central: -0.3, haut: -0.2 },
      sources: [],
      nomenclatures: {
        taille: [classe("a", [-0.2, -0.15, -0.1]), classe("b", [-0.2, -0.15, -0.1])],
        secteur: [],
      },
    },
  ],
};

test("mesures additionnées par classe, fourchette retournée pour une valeur négative", () => {
  const r = effetScenario(DONNEES, GROUPES.cotisations, "taille", {
    cotisations_patronales_taux: 1,
    allegements_generaux: -10,
  });
  assert.ok(r);
  // Allègements réduits de 10 % : la charge augmente de 1 à 2 (bornes inversées par le signe).
  assert.deepEqual(
    r.map((x) => x.effet),
    [
      { bas: 2, central: 2.5, haut: 3 },
      { bas: 2, central: 2.5, haut: 3 },
    ],
  );
});

test("aucune mesure du groupe : pas de tableau", () => {
  assert.equal(effetScenario(DONNEES, GROUPES.cotisations, "taille", { tva_taux_normal: 1 }), null);
});
