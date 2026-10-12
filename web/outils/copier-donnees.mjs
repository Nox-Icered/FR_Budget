// Copie les réponses unitaires du simulateur dans public/donnees/ : le navigateur les charge
// une fois (fichier statique, mis en cache) au lieu de les recevoir dans le HTML de chaque page.
import { copyFile, mkdir } from "node:fs/promises";

const FICHIER = "scenario-unitaire.json";
const source = new URL(`../donnees/${FICHIER}`, import.meta.url);
const dossier = new URL("../public/donnees/", import.meta.url);
await mkdir(dossier, { recursive: true });
await copyFile(source, new URL(FICHIER, dossier));
