// Copie les réponses unitaires du simulateur dans public/donnees/ : le navigateur les charge
// une fois (fichier statique, mis en cache) au lieu de les recevoir dans le HTML de chaque page.
// Le nom du fichier porte l'empreinte de la version (moteur, registres, données), comme les
// liens partagés (lib/etat.ts, empreinteVersion) : après une mise à jour du site, un cache ne
// peut pas servir les réponses d'une version précédente.
import { copyFile, mkdir, readFile, rm, writeFile } from "node:fs/promises";

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
// Effet des scénarios sur les ménages types (simulateur, page « Mon ménage ») : grille des
// cascades exactes, cascades de référence et contrôle de l'approximation, sans les textes déjà
// présents dans les pages.
const effets = JSON.parse(await readFile(new URL("menages-effets.json", donnees), "utf8"));
const types = JSON.parse(await readFile(new URL("menages-types.json", donnees), "utf8"));
const scenarioMenages = {
  annee_revenus: types.annee_revenus,
  menages: types.menages,
  sources: effets.sources,
  leviers: effets.leviers,
  leviers_incidence: effets.leviers_incidence,
  sans_effet: effets.sans_effet,
  grille: effets.grille,
  grille_variantes: Object.fromEntries(
    Object.entries(effets.variantes).map(([v, e]) => [v, e.grille]),
  ),
  ecart_max_un_levier: effets.controle.ecart_max_un_levier,
  ecart_max_combinaison: effets.controle.ecart_max_combinaison,
  ecart_max_salaire_un_levier: effets.controle.ecart_max_salaire_un_levier,
  ecart_max_salaire_combinaison: effets.controle.ecart_max_salaire_combinaison,
};
await writeFile(
  new URL(`menages-scenario.${empreinte}.json`, dossier),
  JSON.stringify(scenarioMenages),
);
