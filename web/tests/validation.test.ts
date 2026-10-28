import { test } from "node:test";
import assert from "node:assert/strict";
import { libelleCommun } from "../lib/validation.ts";

test("libellé commun aux deux bornes d'une fourchette", () => {
  assert.equal(
    libelleCommun(
      "Effet sur le solde à court terme (2 ans), borne basse des simulations",
      "Effet sur le solde à court terme (2 ans), borne haute des simulations",
    ),
    "Effet sur le solde à court terme (2 ans)",
  );
  assert.equal(libelleCommun("abc", "abd"), "ab");
});
