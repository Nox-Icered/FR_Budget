// Ménage saisi : préparation de la requête POST /mon-menage. Règle 5 : la saisie n'est gardée
// ni dans le navigateur (pas de stockage local) ni dans l'adresse de la page ; elle n'est
// envoyée qu'au service de calcul, dans le corps de la requête.
import type { LignesCascade } from "./cascade.ts";

export type Statut = "salarie" | "retraite" | "independant";
export const STATUTS: Statut[] = ["salarie", "retraite", "independant"];

export type Bornes = {
  annee: number;
  adultes_max: number;
  enfants_max: number;
  montant_mensuel_max: number;
  annee_naissance_adulte_min: number;
  annee_naissance_adulte_max: number;
  annee_naissance_enfant_min: number;
  annee_naissance_enfant_max: number;
};

// Champs du formulaire, tels que saisis (texte).
export type AdulteFormulaire = {
  statut: Statut;
  montant: string;
  naissance: string;
  cadre: boolean;
};
export type MenageFormulaire = { adultes: AdulteFormulaire[]; enfants: string[] };

export type CorpsRequete = {
  adultes: { statut: Statut; montant_mensuel: number; annee_naissance: number; cadre: boolean }[];
  annees_naissance_enfants: number[];
  scenario?: ScenarioMenage;
};

export type ResultatMonMenage = LignesCascade & {
  annee_revenus: number;
  sources: string[];
  scenario?: ScenarioMenage & { apres: LignesCascade | null };
};

// Problème de saisie : clé de texte (messages/fr.json, section mon_menage.erreurs).
export type Probleme = { cle: string; variables?: Record<string, number> };

function nombreSaisi(valeur: string): number {
  const v = valeur.trim().replace(/\s/g, "").replace(",", ".");
  return v === "" ? Number.NaN : Number(v);
}

function entier(valeur: string): number {
  const v = nombreSaisi(valeur);
  return Number.isInteger(v) ? v : Number.NaN;
}

export function preparer(
  f: MenageFormulaire,
  b: Bornes,
): { corps: CorpsRequete } | { problemes: Probleme[] } {
  const problemes: Probleme[] = [];
  if (f.adultes.length < 1 || f.adultes.length > b.adultes_max) {
    problemes.push({ cle: "adultes", variables: { max: b.adultes_max } });
  }
  if (f.enfants.length > b.enfants_max) {
    problemes.push({ cle: "enfants", variables: { max: b.enfants_max } });
  }
  const adultes = f.adultes.map((a, i) => {
    const montant = nombreSaisi(a.montant);
    const naissance = entier(a.naissance);
    if (!(montant >= 0 && montant <= b.montant_mensuel_max)) {
      problemes.push({ cle: "montant", variables: { n: i + 1, max: b.montant_mensuel_max } });
    }
    if (
      !(naissance >= b.annee_naissance_adulte_min && naissance <= b.annee_naissance_adulte_max)
    ) {
      problemes.push({
        cle: "naissance_adulte",
        variables: {
          n: i + 1,
          min: b.annee_naissance_adulte_min,
          max: b.annee_naissance_adulte_max,
        },
      });
    }
    return {
      statut: a.statut,
      montant_mensuel: montant,
      annee_naissance: naissance,
      cadre: a.statut === "salarie" && a.cadre,
    };
  });
  const enfants = f.enfants.map((e, i) => {
    const naissance = entier(e);
    if (
      !(naissance >= b.annee_naissance_enfant_min && naissance <= b.annee_naissance_enfant_max)
    ) {
      problemes.push({
        cle: "naissance_enfant",
        variables: {
          n: i + 1,
          min: b.annee_naissance_enfant_min,
          max: b.annee_naissance_enfant_max,
        },
      });
    }
    return naissance;
  });
  if (problemes.length > 0) return { problemes };
  return { corps: { adultes, annees_naissance_enfants: enfants } };
}

// Adresse du service de calcul, fixée à la construction du site (NEXT_PUBLIC_API_URL) ;
// vide tant que l'API n'est pas hébergée.
export function adresseService(base: string | undefined): string | null {
  const b = (base ?? "").trim().replace(/\/+$/, "");
  return b === "" ? null : `${b}/mon-menage`;
}

export async function calculer(
  adresse: string,
  corps: CorpsRequete,
  envoyer: typeof fetch = fetch,
): Promise<ResultatMonMenage> {
  const reponse = await envoyer(adresse, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corps),
    // Ni cache ni référent : la saisie ne laisse pas de trace hors de la requête.
    cache: "no-store",
    referrerPolicy: "no-referrer",
  });
  if (!reponse.ok) throw new Error(`service de calcul : ${reponse.status}`);
  return (await reponse.json()) as ResultatMonMenage;
}

// Scénario transmis du simulateur à la page « Mon ménage » par l'adresse : seulement les
// mesures (paramètre m=levier:valeur;…) et la lecture de l'incidence (i=salaire), jamais la
// saisie du ménage.
export type ScenarioMenage = { mesures: Record<string, number>; incidence: "comptable" | "salaire" };

export function encoderScenarioMenage(s: ScenarioMenage): string {
  const mesures = Object.entries(s.mesures)
    .filter(([, v]) => v !== 0)
    .map(([k, v]) => `${k}:${v}`)
    .join(";");
  if (!mesures) return "";
  const params = new URLSearchParams({ m: mesures });
  if (s.incidence === "salaire") params.set("i", "salaire");
  return params.toString();
}

export function decoderScenarioMenage(
  recherche: string,
  leviersConnus: string[],
): ScenarioMenage | null {
  const params = new URLSearchParams(recherche);
  const m = params.get("m");
  if (!m) return null;
  const mesures: Record<string, number> = {};
  for (const morceau of m.split(";")) {
    const [levier, valeur] = morceau.split(":");
    const v = Number(valeur);
    if (!leviersConnus.includes(levier) || !Number.isFinite(v)) return null;
    mesures[levier] = v;
  }
  return { mesures, incidence: params.get("i") === "salaire" ? "salaire" : "comptable" };
}
