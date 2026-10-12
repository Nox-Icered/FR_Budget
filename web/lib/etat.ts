// État d'un scénario du simulateur, partageable par lien : tout tient dans l'adresse de la
// page (paramètres d'URL), rien n'est envoyé ni enregistré sur un serveur. Le lien porte aussi
// la version du modèle, des registres et des données, pour signaler un résultat qui pourrait
// différer après une mise à jour du site.
import type {
  CatalogueCreditsMissions,
  CatalogueDepensesFiscales,
  ReponsesUnitaires,
  Version,
} from "./donnees";
import type { LigneScenario, MesureSite } from "./scenario";
import { mesuresDepensesFiscales } from "./depenses-fiscales.ts";
import { mesuresCreditsMissions } from "./credits-missions.ts";

export type EtatScenario = {
  annee: number;
  leviers: Record<string, number>;
  parImpot: Record<string, number>;
  parDepense: Record<string, number>;
  parMission: Record<string, number>;
  // Effet sur l'activité (multiplicateur), désactivé par défaut ; paramètre c=1 du lien.
  croissance?: boolean;
  version?: string;
};

// Leviers dont le moteur refuse la combinaison avec des missions (scenario.verifier_double_compte).
export const LEVIERS_REMUNERATIONS = ["remunerations_point_indice", "remunerations_effectifs"];
export const LEVIERS_SOLIDARITE = ["indexation_pensions_prestations", "prime_activite_pente"];
export const MISSION_SOLIDARITE = "solidarite_insertion_et_egalite_des_chances";

// Leviers proposés sur le site, dans l'ordre d'affichage, avec le pas de leur curseur (en
// points ou en centimes par litre). Les autres réponses exportées (leviers génériques des
// dépenses fiscales et des missions, leviers par impôt) ne servent qu'au calcul : un lien qui
// les nomme est refusé.
export const LEVIERS_PUBLICS: { id: string; pas: number }[] = [
  { id: "tva_taux_normal", pas: 0.5 },
  { id: "accise_gazole", pas: 1 },
  { id: "accise_essences", pas: 1 },
  { id: "is_taux_normal", pas: 0.5 },
  { id: "is_surtaxe_grandes_entreprises", pas: 1 },
  { id: "dotations_dgf", pas: 1 },
  { id: "dotations_compensations", pas: 1 },
  { id: "remunerations_point_indice", pas: 0.5 },
  { id: "remunerations_effectifs", pas: 0.5 },
  { id: "indexation_pensions_prestations", pas: 0.1 },
  { id: "csg_activite", pas: 0.1 },
  { id: "csg_retraites", pas: 0.1 },
  { id: "csg_capital", pas: 0.1 },
  { id: "cotisations_patronales_taux", pas: 0.1 },
  { id: "allegements_generaux", pas: 1 },
  { id: "ir_seuils_bareme", pas: 0.1 },
  { id: "prime_activite_pente", pas: 0.1 },
  { id: "retraites_age_depart", pas: 0.25 },
];
const PUBLICS = new Set(LEVIERS_PUBLICS.map((l) => l.id));

// Les identifiants viennent de l'adresse : seules les propriétés propres comptent (pas
// « constructor » ni « toString », hérités de Object).
const possede = (objet: object, cle: string) => Object.hasOwn(objet, cle);

const LONGUEUR_EMPREINTE = 12;

export function empreinteVersion(version: Version): string {
  return [version.moteur, version.registres, version.donnees]
    .map((v) => v.slice(0, LONGUEUR_EMPREINTE))
    .join(".");
}

function encoderListe(valeurs: Record<string, number>): string {
  return Object.entries(valeurs)
    .filter(([, v]) => v !== 0)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([cle, v]) => `${cle}:${v}`)
    .join(",");
}

function decoderListe(texte: string | null): Record<string, number> | null {
  const resultat: Record<string, number> = {};
  if (!texte) return resultat;
  for (const element of texte.split(",")) {
    const separateur = element.lastIndexOf(":");
    if (separateur <= 0) return null;
    // « __proto__ » changerait le prototype de l'objet au lieu d'y ajouter une clé.
    if (element.slice(0, separateur) === "__proto__") return null;
    const valeur = Number(element.slice(separateur + 1));
    if (!Number.isFinite(valeur)) return null;
    resultat[element.slice(0, separateur)] = valeur;
  }
  return resultat;
}

// Paramètres : a (année d'entrée), v (version), c (effet sur l'activité, 1 s'il est inclus),
// l (leviers), i (dépenses fiscales par impôt),
// d (dépenses fiscales choisies), m (missions). Les réglages à zéro sont omis.
export function encoder(etat: EtatScenario): string {
  const p = new URLSearchParams();
  p.set("a", String(etat.annee));
  if (etat.version) p.set("v", etat.version);
  if (etat.croissance) p.set("c", "1");
  const listes: [string, Record<string, number>][] = [
    ["l", etat.leviers],
    ["i", etat.parImpot],
    ["d", etat.parDepense],
    ["m", etat.parMission],
  ];
  for (const [cle, valeurs] of listes) {
    const texte = encoderListe(valeurs);
    if (texte) p.set(cle, texte);
  }
  return p.toString();
}

// Accepte une adresse complète ou sa seule partie « ?… » ; null si le texte est illisible.
export function decoder(texte: string): EtatScenario | null {
  const debut = texte.indexOf("?");
  const p = new URLSearchParams(debut >= 0 ? texte.slice(debut + 1) : texte);
  const brute = p.get("a");
  const annee = Number(brute);
  if (!brute || !Number.isInteger(annee)) return null;
  const leviers = decoderListe(p.get("l"));
  const parImpot = decoderListe(p.get("i"));
  const parDepense = decoderListe(p.get("d"));
  const parMission = decoderListe(p.get("m"));
  if (!leviers || !parImpot || !parDepense || !parMission) return null;
  const c = p.get("c");
  if (c !== null && c !== "1") return null;
  return {
    annee,
    leviers,
    parImpot,
    parDepense,
    parMission,
    ...(c === "1" ? { croissance: true } : {}),
    version: p.get("v") ?? undefined,
  };
}

export type Probleme =
  | "annee"
  | "levier_inconnu"
  | "hors_bornes"
  | "impot_inconnu"
  | "depense_inconnue"
  | "mission_inconnue"
  | "double_compte";

const dans = (v: number, [bas, haut]: [number, number]) => v >= bas && v <= haut;

// Contrôles repris du moteur (bornes des leviers, combinaisons refusées) ; liste vide si l'état
// est calculable.
export function problemes(
  etat: EtatScenario,
  donnees: ReponsesUnitaires,
  catalogue: CatalogueDepensesFiscales,
  missions: CatalogueCreditsMissions,
): Probleme[] {
  const liste: Probleme[] = [];
  const premier = Object.values(donnees.leviers)[0];
  if (!premier || !possede(premier.reponses, String(etat.annee))) liste.push("annee");
  for (const [id, v] of Object.entries(etat.leviers)) {
    if (!PUBLICS.has(id) || !possede(donnees.leviers, id)) liste.push("levier_inconnu");
    else if (!dans(v, donnees.leviers[id].bornes)) liste.push("hors_bornes");
  }
  for (const [impot, v] of Object.entries(etat.parImpot)) {
    if (!possede(catalogue.impots, impot)) liste.push("impot_inconnu");
    else if (!dans(v, [0, 100])) liste.push("hors_bornes");
  }
  const codes = new Set(catalogue.depenses.map((d) => d.code));
  for (const [code, v] of Object.entries(etat.parDepense)) {
    if (!codes.has(code)) liste.push("depense_inconnue");
    else if (!dans(v, [0, 100])) liste.push("hors_bornes");
  }
  const identifiants = new Set(missions.missions.map((m) => m.identifiant));
  for (const [id, v] of Object.entries(etat.parMission)) {
    if (!identifiants.has(id)) liste.push("mission_inconnue");
    else if (!dans(v, missions.bornes)) liste.push("hors_bornes");
  }
  const regle = (ids: string[]) => ids.some((id) => (etat.leviers[id] ?? 0) !== 0);
  const missionsReglees = Object.values(etat.parMission).some((v) => v !== 0);
  const depenseChoisieDansImpot = catalogue.depenses.some(
    (d) => (etat.parDepense[d.code] ?? 0) !== 0 && (etat.parImpot[d.impot] ?? 0) !== 0,
  );
  if (
    (regle(LEVIERS_REMUNERATIONS) && missionsReglees) ||
    (regle(LEVIERS_SOLIDARITE) && (etat.parMission[MISSION_SOLIDARITE] ?? 0) !== 0) ||
    depenseChoisieDansImpot
  ) {
    liste.push("double_compte");
  }
  return [...new Set(liste)];
}

export function mesures(
  etat: EtatScenario,
  catalogue: CatalogueDepensesFiscales,
  missions: CatalogueCreditsMissions,
): MesureSite[] {
  return [
    ...Object.entries(etat.leviers)
      .filter(([, v]) => v !== 0)
      .map(([levier, valeur]) => ({ levier, valeur })),
    ...mesuresDepensesFiscales(catalogue, etat.parImpot, etat.parDepense),
    ...mesuresCreditsMissions(missions, etat.parMission),
  ];
}

// Export : une ligne par année et par scénario, fourchettes en points de PIB.
const COLONNES = [
  "scenario",
  "annee",
  "ecart_solde_primaire_bas",
  "ecart_solde_primaire_central",
  "ecart_solde_primaire_haut",
  "ecart_dette_bas",
  "ecart_dette_central",
  "ecart_dette_haut",
  "dette_bas",
  "dette_central",
  "dette_haut",
] as const;

export type ScenarioExporte = { nom: string; etat: EtatScenario; lignes: LigneScenario[] };

export function versCsv(scenarios: ScenarioExporte[]): string {
  const lignes = scenarios.flatMap(({ nom, lignes: l }) =>
    l.map((x) =>
      [
        nom,
        x.annee,
        x.ecart_solde_primaire.bas,
        x.ecart_solde_primaire.central,
        x.ecart_solde_primaire.haut,
        x.ecart_dette.bas,
        x.ecart_dette.central,
        x.ecart_dette.haut,
        x.dette.bas,
        x.dette.central,
        x.dette.haut,
      ].join(";"),
    ),
  );
  return [COLONNES.join(";"), ...lignes].join("\n") + "\n";
}

export function versJson(scenarios: ScenarioExporte[], version: Version): string {
  return (
    JSON.stringify(
      {
        unite: "points de PIB",
        version,
        scenarios: scenarios.map(({ nom, etat, lignes }) => ({
          nom,
          lien: `?${encoder(etat)}`,
          reglages: etat,
          resultats: lignes,
        })),
      },
      null,
      1,
    ) + "\n"
  );
}
