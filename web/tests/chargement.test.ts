import { test } from "node:test";
import assert from "node:assert/strict";
import { adresseReponses, chargerReponses } from "../lib/chargement.ts";

test("adresse propre à chaque version", () => {
  assert.equal(adresseReponses("a.b.c"), "/donnees/scenario-unitaire.a.b.c.json");
  assert.notEqual(adresseReponses("a.b.c"), adresseReponses("a.b.d"));
});

test("une seule requête par version, puis nouvelle tentative après un échec", async () => {
  const appels: string[] = [];
  let reponse: Response = new Response("", { status: 503 });
  globalThis.fetch = (async (url: string) => {
    appels.push(url);
    return reponse;
  }) as typeof fetch;
  await assert.rejects(chargerReponses("v1"));
  await new Promise((ok) => setTimeout(ok, 0));
  reponse = new Response(JSON.stringify({ annees: [2027] }), { status: 200 });
  const [a, b] = await Promise.all([chargerReponses("v1"), chargerReponses("v1")]);
  assert.deepEqual(a, { annees: [2027] });
  assert.equal(a, b);
  await chargerReponses("v1");
  assert.deepEqual(appels, [adresseReponses("v1"), adresseReponses("v1")]);
});
