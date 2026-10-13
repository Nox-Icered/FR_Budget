import { test } from "node:test";
import assert from "node:assert/strict";
import {
  adresseService,
  calculer,
  decoderScenarioMenage,
  encoderScenarioMenage,
  preparer,
  type Bornes,
  type MenageFormulaire,
} from "../lib/mon-menage.ts";

const BORNES: Bornes = {
  annee: 2025,
  adultes_max: 2,
  enfants_max: 8,
  montant_mensuel_max: 100000,
  annee_naissance_adulte_min: 1915,
  annee_naissance_adulte_max: 2009,
  annee_naissance_enfant_min: 2000,
  annee_naissance_enfant_max: 2025,
};

const SAISIE: MenageFormulaire = {
  adultes: [
    { statut: "salarie", montant: "2 345,67", naissance: "1984", cadre: true },
    { statut: "retraite", montant: "1432.1", naissance: "1957", cadre: true },
  ],
  enfants: ["2014"],
};

test("la saisie devient le corps de la requête", () => {
  const r = preparer(SAISIE, BORNES);
  assert.ok("corps" in r);
  assert.deepEqual(r.corps, {
    adultes: [
      { statut: "salarie", montant_mensuel: 2345.67, annee_naissance: 1984, cadre: true },
      // Seul un salarié peut être cadre.
      { statut: "retraite", montant_mensuel: 1432.1, annee_naissance: 1957, cadre: false },
    ],
    annees_naissance_enfants: [2014],
  });
});

test("une saisie hors bornes est signalée, sans requête", () => {
  const r = preparer(
    {
      adultes: [{ statut: "salarie", montant: "abc", naissance: "2020", cadre: false }],
      enfants: ["1990"],
    },
    BORNES,
  );
  assert.ok("problemes" in r);
  assert.deepEqual(
    r.problemes.map((p) => p.cle),
    ["montant", "naissance_adulte", "naissance_enfant"],
  );
});

test("aucun adulte ou trop d'enfants", () => {
  const r = preparer({ adultes: [], enfants: Array(9).fill("2010") }, BORNES);
  assert.ok("problemes" in r);
  assert.deepEqual(
    r.problemes.map((p) => p.cle),
    ["adultes", "enfants"],
  );
});

test("adresse du service : absente tant que l'API n'est pas hébergée", () => {
  assert.equal(adresseService(undefined), null);
  assert.equal(adresseService("  "), null);
  assert.equal(adresseService("https://api.exemple.fr/"), "https://api.exemple.fr/mon-menage");
});

test("la saisie part dans le corps d'un POST, jamais dans l'adresse", async () => {
  const r = preparer(SAISIE, BORNES);
  assert.ok("corps" in r);
  let appel: { url: string; init: RequestInit } | undefined;
  const faux = (async (url: string, init: RequestInit) => {
    appel = { url, init };
    return new Response("{}", { status: 200 });
  }) as unknown as typeof fetch;
  await calculer("https://api.exemple.fr/mon-menage", r.corps, faux);
  assert.ok(appel);
  assert.equal(appel.url, "https://api.exemple.fr/mon-menage");
  assert.equal(appel.init.method, "POST");
  assert.equal(appel.init.cache, "no-store");
  assert.deepEqual(JSON.parse(String(appel.init.body)), r.corps);
});

test("une réponse en erreur ne renvoie pas de résultat", async () => {
  const faux = (async () => new Response("", { status: 422 })) as unknown as typeof fetch;
  await assert.rejects(calculer("https://x/mon-menage", { adultes: [], annees_naissance_enfants: [] }, faux));
});

const LEVIERS = [
  { id: "csg_activite", bornes: [-2, 2] as [number, number] },
  { id: "ir_seuils_bareme", bornes: [-3, 3] as [number, number] },
  { id: "cotisations_patronales_taux", bornes: [-2, 2] as [number, number] },
];
const INCIDENCE = ["cotisations_patronales_taux"];

test("scénario transmis par l'adresse : mesures seulement, aller-retour", () => {
  const s = {
    mesures: { csg_activite: 1.5, cotisations_patronales_taux: -1, tva_taux_normal: 0 },
    incidence: "salaire" as const,
  };
  const adresse = encoderScenarioMenage(s);
  assert.equal(adresse, "m=csg_activite%3A1.5%3Bcotisations_patronales_taux%3A-1&i=salaire");
  assert.deepEqual(decoderScenarioMenage(adresse, LEVIERS, INCIDENCE), {
    mesures: { csg_activite: 1.5, cotisations_patronales_taux: -1 },
    incidence: "salaire",
  });
  assert.equal(encoderScenarioMenage({ mesures: { csg_activite: 0 }, incidence: "comptable" }), "");
});

test("scénario de l'adresse refusé comme par le service de calcul", () => {
  for (const recherche of [
    "m=inconnu%3A1", // levier inconnu
    "m=csg_activite%3Aabc", // valeur illisible
    "m=csg_activite%3A", // valeur absente
    "m=csg_activite%3A5", // hors des bornes
    "m=csg_activite%3A1&i=salaire", // lecture répercutée sans cotisation patronale
    "m=csg_activite%3A1&i=salair", // lecture inconnue
  ]) {
    assert.equal(decoderScenarioMenage(recherche, LEVIERS, INCIDENCE), null, recherche);
  }
  assert.equal(decoderScenarioMenage("", LEVIERS, INCIDENCE), null);
});
