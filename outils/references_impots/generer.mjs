// Génère les valeurs de référence « impots.gouv.fr » de l'impôt sur le revenu des ménages types.
//
// Source : simulateur officiel de calcul de l'impôt 2026 sur les revenus 2025, modèle
// simplifié (https://simulateur-ir-ifi.impots.gouv.fr/calcul_impot/2026/simplifie/index.htm).
// Chaque déclaration (registres/references/menages/cas_impot_revenu.json, écrite par
// pipelines/menages/cas_impot.py) est saisie dans le formulaire ; la page de résultat est
// relevée telle quelle (lignes « Nombre de parts », « Revenu fiscal de référence »,
// « Droits simples », « Décote », « Impôt sur le revenu net », montant restant à payer).
//
// Usage : npm ci && npx playwright-core install chromium && npm run generer
// (ou CHROMIUM=/chemin/vers/chrome npm run generer)
import { readFileSync, writeFileSync } from "node:fs";
import { chromium } from "playwright-core";

const ADRESSE = "https://simulateur-ir-ifi.impots.gouv.fr/calcul_impot/2026/simplifie/index.htm";
const ENTREE = new URL("../../registres/references/menages/cas_impot_revenu.json", import.meta.url);
const SORTIE = new URL("../../registres/references/menages/impots_gouv_ir2026.json", import.meta.url);
// Libellé de la page de résultat → clé de sortie.
const LIGNES = {
  "Nombre de parts": "nombre_parts",
  "Revenu fiscal de référence": "revenu_fiscal_reference",
  "Droits simples": "droits_simples",
  "Décote": "decote",
  "Impôt sur le revenu net": "impot_net",
  "MONTANT RESTANT À PAYER AU TITRE DE L'ANNÉE 2025 *": "restant_a_payer",
};

function relever(texte) {
  const resultats = {};
  for (const ligne of texte.split("\n")) {
    // Les lignes de résultat commencent par une tabulation : cellules non vides seulement.
    const cellules = ligne.split("\t").map((x) => x.trim()).filter(Boolean);
    const [libelle, valeur] = [cellules[0], cellules.at(-1)];
    if (cellules.length >= 2 && libelle in LIGNES && /^-?[\d ]+([,.]\d+)?$/.test(valeur)) {
      resultats[LIGNES[libelle]] = Number(valeur.replace(/ /g, "").replace(",", "."));
    }
  }
  return resultats;
}

// Modèle complet, pour les déclarations qui portent un bénéfice (case 5KC, revenus
// industriels et commerciaux professionnels) : le formulaire est réparti sur plusieurs pages,
// dont le simulateur range les cases dans un panier par ses propres fonctions (suite1 pour
// l'état civil, suite2 pour le choix des rubriques, suite11 pour la page 11), puis restit()
// construit le formulaire envoyé au serveur.
const ADRESSE_COMPLET = ADRESSE.replace("/simplifie/", "/complet/");
const CASES_COMPLET = ["5KC"];

async function saisirComplet(page, d) {
  await page.goto(ADRESSE_COMPLET, { waitUntil: "networkidle" });
  await page.evaluate((d) => {
    document.querySelector(`#pre_situation_famille${d.situation}`).checked = true;
    document.querySelector("#pre_situation_residenceM").checked = true;
    document.form1._0DA.value = d["0DA"];
    if (d["0CF"]) document.form1._0CF.value = String(d["0CF"]);
    suite1();
    document.querySelector("#revenu9").checked = true;
    suite2();
    document.form11._5KC.value = String(d["5KC"]);
    suite11();
  }, d);
  await Promise.all([
    page.waitForURL(/calc-2026\.cgi/),
    page.evaluate(() => {
      restit();
      document.form19.submit();
    }),
  ]);
}

const { cas } = JSON.parse(readFileSync(ENTREE, "utf8"));
const navigateur = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
const sorties = [];
for (const c of cas) {
  const d = c.declaration;
  const page = await navigateur.newPage();
  if (CASES_COMPLET.some((k) => d[k])) {
    await saisirComplet(page, d);
  } else {
    await page.goto(ADRESSE, { waitUntil: "domcontentloaded" });
    await page.check(`#situation_famille${d.situation}`);
    await page.check("#Bpre_situation_residence");
    await page.fill('[name="0DA"]', d["0DA"]);
    if (d["0DB"]) await page.fill('[name="0DB"]', d["0DB"]);
    if (d["0CF"]) await page.fill('[name="0CF"]', String(d["0CF"]));
    if (d["0BT"]) await page.check('[name="0BT"]');
    await page.fill('[name="1AJ"]', String(d["1AJ"]));
    if (d["1BJ"]) await page.fill('[name="1BJ"]', String(d["1BJ"]));
    if (d["1AS"]) await page.fill('[name="1AS"]', String(d["1AS"]));
    await Promise.all([page.waitForURL(/calc-2026\.cgi/), page.getByAltText("lancer la simulation").click()]);
  }
  const texte = await page.locator("body").innerText();
  const resultats = relever(texte);
  if (!("restant_a_payer" in resultats)) throw new Error(`${c.id} : résultat introuvable`);
  sorties.push({ id: c.id, revenus: c.revenus, declaration: d, resultats });
  console.log(c.id, resultats);
  await page.close();
}
await navigateur.close();
writeFileSync(
  SORTIE,
  JSON.stringify(
    {
      source: {
        nom: "Simulateur de calcul de l'impôt 2026 sur les revenus 2025 (modèle simplifié ; modèle complet pour les bénéfices)",
        editeur: "Direction générale des Finances publiques",
        url: ADRESSE,
        script: "outils/references_impots/generer.mjs",
        genere_le: new Date().toISOString().slice(0, 10),
      },
      cas: sorties,
    },
    null,
    2,
  ) + "\n",
);
