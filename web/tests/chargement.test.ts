import { test } from "node:test";
import assert from "node:assert/strict";
import { ADRESSE_REPONSES, chargerReponses } from "../lib/chargement.ts";

test("une seule requête, puis nouvelle tentative après un échec", async () => {
  const appels: string[] = [];
  let reponse: Response = new Response("", { status: 503 });
  globalThis.fetch = (async (url: string) => {
    appels.push(url);
    return reponse;
  }) as typeof fetch;
  await assert.rejects(chargerReponses());
  await new Promise((ok) => setTimeout(ok, 0));
  reponse = new Response(JSON.stringify({ annees: [2027] }), { status: 200 });
  const [a, b] = await Promise.all([chargerReponses(), chargerReponses()]);
  assert.deepEqual(a, { annees: [2027] });
  assert.equal(a, b);
  await chargerReponses();
  assert.deepEqual(appels, [ADRESSE_REPONSES, ADRESSE_REPONSES]);
});
