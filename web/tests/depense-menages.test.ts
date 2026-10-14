import { test } from "node:test";
import assert from "node:assert/strict";
import { effetDepense } from "../lib/depense-menages.ts";
import type { DepenseMenages } from "../lib/donnees.ts";

const f = (bas: number, central: number, haut: number) => ({ bas, central, haut });
const DONNEES: DepenseMenages = {
  annee: 2025,
  annee_enquete: 2017,
  unite: "",
  leviers: ["tva_taux_normal", "accise_gazole", "accise_essences"],
  sources: [],
  controles: [],
  nomenclatures: {
    decile: [
      {
        id: "1",
        consommation: 20000,
        effets: {
          tva_taux_normal: f(50, 75, 100),
          accise_gazole: f(3, 3, 3),
          accise_essences: f(2, 2, 2),
        },
      },
    ],
    type_menage: [],
  },
};

test("aucune mesure de TVA ou d'accise : pas de tableau", () => {
  assert.equal(effetDepense(DONNEES, "decile", { csg_activite: 1 }), null);
});

test("mesures additionnées, fourchette retournée pour une baisse", () => {
  const [ligne] = effetDepense(DONNEES, "decile", { tva_taux_normal: -1, accise_gazole: 10 }) ?? [];
  assert.deepEqual(ligne.effet, { bas: -100 + 30, central: -75 + 30, haut: -50 + 30 });
  assert.equal(ligne.part.central, (-75 + 30) / 20000);
});
