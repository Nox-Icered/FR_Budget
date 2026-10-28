import { test } from "node:test";
import assert from "node:assert/strict";
import { plageNulle } from "../lib/hypotheses.ts";

test("plage nulle quand les bornes sont égales", () => {
  assert.equal(plageNulle({ basse: 0.7, haute: 0.7 }), true);
  assert.equal(plageNulle({ basse: 0.5, haute: 0.63 }), false);
});
