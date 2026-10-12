// Copie les réponses unitaires du simulateur dans public/donnees/ : le navigateur les charge
// une fois (fichier statique, mis en cache) au lieu de les recevoir dans le HTML de chaque page.
// Le nom du fichier porte l'empreinte de la version (moteur, registres, données), comme les
// liens partagés (lib/etat.ts, empreinteVersion) : après une mise à jour du site, un cache ne
// peut pas servir les réponses d'une version précédente.
import { copyFile, mkdir, readFile, rm } from "node:fs/promises";

const LONGUEUR_EMPREINTE = 12;
const donnees = new URL("../donnees/", import.meta.url);
const dossier = new URL("../public/donnees/", import.meta.url);
const version = JSON.parse(await readFile(new URL("version.json", donnees), "utf8"));
const empreinte = [version.moteur, version.registres, version.donnees]
  .map((v) => v.slice(0, LONGUEUR_EMPREINTE))
  .join(".");
await rm(dossier, { recursive: true, force: true });
await mkdir(dossier, { recursive: true });
await copyFile(
  new URL("scenario-unitaire.json", donnees),
  new URL(`scenario-unitaire.${empreinte}.json`, dossier),
);
