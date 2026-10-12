// Contrôle automatique d'accessibilité (axe-core, règles WCAG 2.0 A et AA, WCAG 2.1 AA) de
// chaque page du site exporté (out/), en largeur mobile. Échoue s'il reste une violation.
// Les contrôles automatiques ne couvrent qu'une partie du RGAA : un audit manuel reste à faire.
//
// Usage (après pnpm build) : pnpm accessibilite
// Navigateur : CHROMIUM=/chemin/vers/chrome, sinon celui installé par playwright-core.
import { createServer } from "node:http";
import { access, readFile, readdir } from "node:fs/promises";
import { createRequire } from "node:module";
import { extname, join, normalize } from "node:path";
import { chromium } from "playwright-core";

const SORTIE = new URL("../out/", import.meta.url).pathname;
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".txt": "text/plain" };
const REGLES = ["wcag2a", "wcag2aa", "wcag21aa"];
const LARGEUR_MOBILE = 390;
// Une comparaison remplie, pour contrôler aussi ses tableaux.
const COMPARAISON = "/comparaison/?s1=a%3D2027%26l%3Dtva_taux_normal%3A1&s2=a%3D2027%26c%3D1%26l%3Dcsg_activite%3A1";

const serveur = createServer(async (req, res) => {
  const chemin = normalize(decodeURIComponent(new URL(req.url, "http://x").pathname));
  const fichier = join(SORTIE, chemin.endsWith("/") ? `${chemin}index.html` : chemin);
  let contenu;
  try {
    contenu = await readFile(fichier);
  } catch {
    res.writeHead(404).end();
    return;
  }
  res.writeHead(200, { "content-type": TYPES[extname(fichier)] ?? "application/octet-stream" });
  res.end(contenu);
});
await new Promise((ok) => serveur.listen(0, ok));
const racine = `http://localhost:${serveur.address().port}`;

// Une page = un dossier qui contient index.html (les données, comme donnees/, n'en ont pas).
const estPage = (nom) => access(join(SORTIE, nom, "index.html")).then(() => true, () => false);
const dossiers = (await readdir(SORTIE, { withFileTypes: true })).filter(
  (e) => e.isDirectory() && !e.name.startsWith("_") && e.name !== "404",
);
const pages = [];
for (const e of dossiers) if (await estPage(e.name)) pages.push(`/${e.name}/`);
pages.unshift("/");
pages.push(COMPARAISON);

const axe = await readFile(createRequire(import.meta.url).resolve("axe-core/axe.min.js"), "utf8");
const navigateur = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
const page = await navigateur.newPage({ viewport: { width: LARGEUR_MOBILE, height: 900 } });
let total = 0;
for (const chemin of pages) {
  await page.goto(racine + chemin, { waitUntil: "networkidle" });
  await page.addScriptTag({ content: axe });
  const { violations } = await page.evaluate((regles) => window.axe.run(document, { runOnly: regles }), REGLES);
  total += violations.length;
  console.log(`${violations.length === 0 ? "ok " : "ÉCHEC"} ${chemin}`);
  for (const v of violations) console.log(`     ${v.impact} ${v.id} (${v.nodes.length}) : ${v.help}`);
}
await navigateur.close();
serveur.close();
if (total > 0) process.exit(1);
