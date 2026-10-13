// Génère les valeurs de référence « mesdroitssociaux.gouv.fr » de la prime d'activité des
// ménages types.
//
// Source : simulateur officiel du RSA et de la prime d'activité
// (https://www.mesdroitssociaux.gouv.fr/simulateurs/rsa-pa), sans connexion. Il applique la
// législation du jour et demande les ressources des quatre derniers mois.
// Chaque cas (registres/references/menages/cas_prestations.json, écrit par
// pipelines/menages/cas_prestations.py) est saisi étape par étape : foyer, enfants,
// ressources de chaque adulte (salaires, puis prestations familiales versées), logement.
// Les salaires saisis sont les revenus d'activité qu'OpenFisca retient pour la prime d'activité
// (salaire net), et non le net fiscal que demande le libellé du formulaire : la CAF retient le
// montant net social, et le modèle et le simulateur doivent partir du même revenu.
// La ligne « Prime d'activité  Montant estimé : … € /mois » de la page de résultat est relevée.
//
// Le code postal est complété par une liste de communes que le site charge auprès de
// geo.api.gouv.fr : sans ce service, l'étape du logement échoue.
//
// Usage : npm ci && npm run generer [-- identifiant ...]
// (CHROMIUM=/chemin/vers/chrome pour un navigateur déjà installé). Sans identifiant, tous les
// cas sont saisis ; les résultats remplacent ceux des mêmes cas dans le fichier de sortie.
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { chromium } from "playwright-core";

const ADRESSE = "https://www.mesdroitssociaux.gouv.fr/simulateurs/rsa-pa";
const ENTREE = new URL("../../registres/references/menages/cas_prestations.json", import.meta.url);
const SORTIE = new URL(
  "../../registres/references/menages/mesdroitssociaux_pa_2026.json",
  import.meta.url,
);
// Prestation du ménage type → case « autres ressources » du simulateur.
const AUTRES_RESSOURCES = {
  asf: "ALLOCallocationSoutienFamilial",
  af: "ALLOCallocationFamiliale",
};
const ATTENTE = 2500;

async function saisir(page, c) {
  page.setDefaultTimeout(20000);
  const bouton = async (nom = "Valider") => {
    await page.getByRole("button", { name: nom, exact: true }).first().click();
    await page.waitForTimeout(ATTENTE);
  };
  // Les boutons radio et cases à cocher sont masqués : on clique leur libellé.
  const choisir = (id) => page.locator(`label[for="${id}"]`).click();
  const taper = async (selecteur, valeur) => {
    const champ = page.locator(selecteur);
    await champ.click();
    await champ.fill("");
    await champ.pressSequentially(String(valeur));
    await champ.press("Tab");
  };
  const personne = async (prenom, naissance) => {
    const [annee, mois, jour] = naissance.split("-");
    await page.fill("#prenom", prenom);
    await page.fill("#dateNaissancejj", jour);
    await page.fill("#dateNaissancemm", mois);
    await page.fill("#dateNaissancessaa", annee);
    await choisir("sexeF");
  };

  await page.goto(ADRESSE, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(4000);
  await page.getByRole("button", { name: "Tout refuser" }).click().catch(() => {});
  // Trois questions préalables (exploitant agricole, etc.) : « Non ».
  const non = page.getByText("Non", { exact: true });
  for (let i = 0; i < (await non.count()); i++) await non.nth(i).click();
  await page.getByRole("button", { name: "Simuler le RSA et la PA" }).click();
  await page.waitForURL(/rsa-pa\/foyer/);
  await page.waitForTimeout(3000);

  // Foyer : déclarant, conjoint, enfants.
  const [declarant, conjoint] = c.adultes;
  await personne("A", declarant.naissance);
  await choisir(c.couple ? "situationMatrimonialeM" : "situationMatrimonialeC");
  await choisir("isRegimeAlsaceMoselle-false");
  await choisir("situationProfessionnelleSAL");
  await page.waitForTimeout(600);
  await choisir("situationScolaireNO");
  await choisir("situationPersonnelleNO");
  await bouton();
  if (conjoint) {
    await personne("B", conjoint.naissance);
    await choisir("isRegimeAlsaceMoselle-false");
    await bouton();
    await choisir("situationProfessionnelleSAL");
    await page.waitForTimeout(600);
    await choisir("situationScolaireNO");
    await choisir("situationPersonnelleNO");
    await bouton();
  }
  for (const [k, naissance] of c.enfants.entries()) {
    await bouton("Ajouter un enfant");
    await personne(`E${k + 1}`, naissance);
    await choisir("gardeAlternee-false");
    await page.waitForTimeout(600);
    await bouton();
  }
  await bouton("Suivant");

  // Ressources de chaque adulte ; les prestations familiales sont déclarées par le premier.
  for (const [k, adulte] of c.adultes.entries()) {
    await page.getByText("Compléter les ressources", { exact: true }).first().click();
    await page.waitForTimeout(ATTENTE);
    await choisir("ressourcessalairesDontPrimes");
    await bouton();
    for (const [i, montant] of adulte.salaires.entries()) await taper(`#ressource-${i}`, montant);
    await bouton();
    const autres = k === 0 ? c.autres_ressources : [];
    if (autres.length === 0) {
      await choisir("topAucuneDeCesRessources");
      await bouton();
    } else {
      for (const r of autres) await choisir(AUTRES_RESSOURCES[r.prestation]);
      await bouton();
      for (const r of autres) {
        for (const [i, montant] of r.montants.entries()) await taper(`#ressource-${i}`, montant);
        await bouton();
      }
    }
  }
  await bouton("Suivant");

  // Logement : la commune vient d'une liste de suggestions, parfois lente (cinq essais).
  await page.waitForURL(/logement/);
  await page.getByLabel("Code postal ou ville").waitFor({ timeout: 25000 });
  const commune = page.locator("input[aria-controls*=logementCommune], input[role=combobox]").first();
  const suggestion = page.locator("#logementCommune-listbox-option-0");
  for (let essai = 1; ; essai++) {
    await commune.fill("");
    await commune.click();
    await commune.pressSequentially(c.logement.code_postal, { delay: 150 });
    await choisir("logementTypeSituationLOCATAIRE");
    try {
      await suggestion.waitFor({ timeout: 30000 });
      break;
    } catch (erreur) {
      if (essai >= 5) throw erreur;
    }
  }
  const nomCommune = (await suggestion.innerText()).trim();
  await suggestion.click();
  await page.waitForTimeout(1000);
  if (!(await page.locator("#logementTypeSituationLOCATAIRE").isChecked())) {
    await choisir("logementTypeSituationLOCATAIRE");
  }
  await taper("#logementLoyer", c.logement.loyer);
  await bouton();
  await bouton("Voir les résultats");
  await page.waitForTimeout(5000);

  const texte = (await page.locator("main").innerText()).replace(/\s+/g, " ");
  const pa = texte.match(/Prime d'activité Montant estimé : (\d[\d ]*)\s*€/);
  if (!pa) throw new Error(`${c.id} : montant de la prime d'activité introuvable`);
  const rsa = texte.match(/RSA Montant estimé : (\d[\d ]*)\s*€/);
  return {
    commune: nomCommune,
    prime_activite: Number(pa[1].replace(/ /g, "")),
    ...(rsa ? { rsa: Number(rsa[1].replace(/ /g, "")) } : {}),
    texte_resultat: texte.slice(texte.indexOf("Prime d'activité"), texte.indexOf("Prime d'activité") + 200),
  };
}

const { cas } = JSON.parse(readFileSync(ENTREE, "utf8"));
const demandes = process.argv.slice(2);
const precedent = existsSync(SORTIE) ? JSON.parse(readFileSync(SORTIE, "utf8")).cas : [];
const resultats = new Map(precedent.map((c) => [c.id, c]));
const navigateur = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
const date = new Date().toISOString().slice(0, 10);
let echecs = 0;
for (const c of cas.filter((x) => demandes.length === 0 || demandes.includes(x.id))) {
  const page = await navigateur.newPage({ viewport: { width: 1280, height: 900 } });
  try {
    const { texte_resultat, ...releve } = await saisir(page, c);
    resultats.set(c.id, { ...c, simule_le: date, resultats: releve, texte_resultat });
    console.log(c.id, releve);
  } catch (erreur) {
    echecs += 1;
    console.error(c.id, "échec :", erreur.message.split("\n")[0]);
    if (process.env.DEBUG) console.error((await page.locator("body").innerText()).replace(/\n+/g, " | ").slice(0, 2000));
  }
  await page.close();
}
await navigateur.close();
writeFileSync(
  SORTIE,
  JSON.stringify(
    {
      source: {
        nom: "Simulateur du RSA et de la prime d'activité (mesdroitssociaux.gouv.fr)",
        editeur: "Caisse centrale de la MSA (portail mesdroitssociaux.gouv.fr)",
        url: ADRESSE,
        script: "outils/references_prestations/generer.mjs",
      },
      cas: cas.map((c) => resultats.get(c.id)).filter(Boolean),
    },
    null,
    2,
  ) + "\n",
);
process.exit(echecs ? 1 : 0);
