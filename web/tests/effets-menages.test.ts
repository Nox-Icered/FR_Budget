import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { approcher, type Grille } from "../lib/effets-menages.ts";
import type { LignesCascade } from "../lib/cascade.ts";

// Données exportées par l'API (pnpm donnees, lancé avant les tests en intégration continue).
const lire = (f: string) => JSON.parse(readFileSync(join(process.cwd(), "donnees", f), "utf-8"));
const effets = lire("menages-effets.json");
const menages: (LignesCascade & { id: string })[] = lire("menages-types.json").menages;
const reference = Object.fromEntries(menages.map((m) => [m.id, m]));

test("même approximation que le moteur sur les scénarios de contrôle", () => {
  for (const s of effets.controle.scenarios) {
    for (const [id, attendu] of Object.entries(s.menages) as [string, { approche: number } | null][]) {
      const approche = approcher(
        reference[id],
        id,
        Object.entries(s.mesures) as [string, number][],
        effets.grille as Grille,
        effets.leviers_incidence,
      );
      if (attendu === null) {
        assert.equal(approche, null, `${id}`);
        continue;
      }
      assert.ok(approche);
      const ecart = approche.net_apres_impot - reference[id].net_apres_impot;
      assert.ok(Math.abs(ecart - attendu.approche) < 0.5, `${id} ${JSON.stringify(s.mesures)}`);
    }
  }
});

test("scénario sans mesure : la référence", () => {
  const m = menages[0];
  const r = approcher(m, m.id, [], effets.grille as Grille, effets.leviers_incidence);
  assert.ok(r);
  assert.ok(Math.abs(r.net_apres_impot - m.net_apres_impot) < 0.05);
});
