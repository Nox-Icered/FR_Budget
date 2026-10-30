// Lecture, au moment de la construction, des fichiers exportés par l'API (web/donnees/).
import { readFileSync } from "node:fs";
import { join } from "node:path";

import type { LignesCascade } from "./cascade";
import type { Grille } from "./effets-menages";
import type { Bornes } from "./mon-menage";

const DOSSIER = join(process.cwd(), "donnees");

export function lire<T>(fichier: string): T {
  return JSON.parse(readFileSync(join(DOSSIER, fichier), "utf-8")) as T;
}

export type Point = { annee: number; valeur: number; pourcent_pib?: number };
export type Serie = {
  source: string;
  unite: string;
  sous_secteur: string;
  indicateur: string;
  valeurs: Point[];
};
export type ComptesApu = {
  sous_secteurs: string[];
  indicateurs: string[];
  series: Record<string, Record<string, Serie>>;
};
export type Cofog = {
  source: string;
  unite: string;
  annee: number;
  sous_secteur: string;
  valeurs: { cofog: string; libelle: string; valeur: number }[];
};
export type Source = {
  id: string;
  nom: string;
  editeur: string;
  url: string;
  licence: string;
  millesime?: string;
  consulte_le: string;
};
export type Hypothese = {
  id: string;
  libelle: string;
  unite: string;
  valeur_centrale: number;
  plage: { basse: number; haute: number };
  sources: string[];
  justification: string;
};
export type Levier = { id: string; libelle: string; statut: "valide" | "beta" | "non_publie" };
export type Chiffrage = {
  id: string;
  levier?: string;
  module?: string;
  source: string;
  millesime: string;
  mesure: string;
  valeur: number;
  unite: string;
  localisation: string;
  relecture: "a_relire" | "relu";
  independante?: boolean;
};
export type Relecture = {
  id: string;
  date: string;
  relecteur: string;
  objet: string[];
  retour: string;
  reponse: string;
  lien?: string;
};
// Variantes de revenu des ménages types : bornes des hypothèses d'évolution des revenus.
export type VarianteRevenu = "bas" | "haut";
export type MenageType = LignesCascade & {
  id: string;
  libelle: string;
  annee: number;
  variantes: Record<VarianteRevenu, LignesCascade>;
};
type EffetsUnite = Record<string, Record<"hausse" | "baisse", Record<string, LignesCascade | null>>>;
export type MenagesTypes = {
  unite: string;
  annee_revenus: number;
  sources: string[];
  hypotheses: string[];
  menages: MenageType[];
  saisie: Bornes;
};
export type EffetsMenages = {
  unite: string;
  annee_revenus: number;
  sources: string[];
  leviers: { id: string; unite: string; sources: string[]; bornes: [number, number] }[];
  sans_effet: Record<string, string>;
  effets: EffetsUnite;
  effets_salaire: EffetsUnite;
  leviers_incidence: string[];
  incidence_par_defaut: Incidence;
  // Mêmes effets au revenu bas et haut (fourchette).
  variantes: Record<VarianteRevenu, { effets: EffetsUnite; effets_salaire: EffetsUnite }>;
};
export type Incidence = "comptable" | "salaire";
export type MenagesScenario = {
  annee_revenus: number;
  menages: MenageType[];
  sources: string[];
  leviers: { id: string; unite: string; sources: string[]; bornes: [number, number] }[];
  leviers_incidence: string[];
  sans_effet: Record<string, string>;
  grille: Grille;
  // Grille au revenu bas et haut (fourchette).
  grille_variantes: Record<VarianteRevenu, Grille>;
  ecart_max_un_levier: number;
  ecart_max_combinaison: number;
  ecart_max_salaire_un_levier: number;
  ecart_max_salaire_combinaison: number;
};
export type LigneJournal = {
  date: string;
  fiche: string;
  titre: string;
  changement: string;
  tests: string;
};
export type Comparaison = {
  reference: string;
  modele: number;
  valeur_reference: number;
  ecart: number;
  tolerance: number;
  dans_la_tolerance: boolean;
  unite: string;
  levier?: string;
  independante: boolean;
  variante?: string;
  reference_haute?: string;
  valeur_haute?: number | null;
};
export type Version = { moteur: string; registres: string; donnees: string };
export type FourchetteJson = { bas: number; central: number; haut: number };
export type Baseline = {
  sources: string[];
  unite: string;
  statut: "valide" | "beta" | "non_publie";
  annee_raccord: number;
  hypotheses: string[];
  valeurs: {
    annee: number;
    segment: "resf" | "projection";
    dette: FourchetteJson;
    solde_primaire: FourchetteJson;
  }[];
};
export type ReponsesUnitaires = {
  unite: string;
  annee_reference: number;
  annees: number[];
  base_dette: number[][];
  base_solde: number[][];
  indices_effet: number[];
  // Sources et hypothèses de l'effet de croissance (interrupteur, désactivé par défaut).
  // effet_solde_plage : plage de alpha (effet de l'écart de production sur le solde).
  croissance?: {
    sources: string[];
    hypotheses: string[];
    persistance: number;
    effet_solde: number;
    effet_solde_plage?: { bas: number; central: number; haut: number };
  };
  leviers: Record<
    string,
    {
      statut: "valide" | "beta" | "non_publie";
      rendement_unitaire: number;
      effet_unitaire: number;
      taux_reference: number;
      effet_etat_unitaire?: number;
      effet_brut_unitaire?: number;
      // Retraites : effet d'un an en points de PIB une fois en place, durée de montée en charge.
      effet_plein?: number;
      duree_montee?: number;
      duree_montee_plage?: { bas: number; central: number; haut: number };
      bornes: [number, number];
      // Levier non linéaire : réponse exacte (et non par unité) de chaque cran du curseur.
      grille?: Record<
        string,
        Record<
          string,
          {
            unite_dette: number[][];
            unite_solde: number[][];
            croissance_dette?: number[][];
            croissance_solde?: number[][];
            croissance_alpha_dette?: number[][];
            croissance_alpha_solde?: number[][];
          }
        >
      >;
      multiplicateur?: { bas: number; central: number; haut: number };
      // croissance_* : supplément d'une unité du levier pour un multiplicateur de 1 ;
      // croissance_alpha_* : variation de ce supplément pour un point de alpha.
      reponses: Record<
        string,
        {
          unite_dette: number[][];
          unite_solde: number[][];
          croissance_dette?: number[][];
          croissance_solde?: number[][];
          croissance_alpha_dette?: number[][];
          croissance_alpha_solde?: number[][];
        }
      >;
    }
  >;
};
export type DepenseFiscale = {
  code: string;
  impot: string;
  libelle: string;
  cout: number;
  annee_chiffrage: number;
  fiabilite: string;
  rendement_pourcent: number;
  // Fiche descriptive du tome II de Voies et moyens, telle que publiée (champ vide si absent).
  fiche?: FicheDepense | null;
};
export type FicheDepense = {
  finalite: string;
  beneficiaires: string;
  creation: string;
  modification: string;
  reference: string;
  mission: string;
};
export type CatalogueDepensesFiscales = {
  source: string;
  annee_cout: number;
  unite_cout: string;
  impots: Record<string, { levier: string; cout: number }>;
  ordre_impots: string[];
  impots_exclus: string[];
  depenses: DepenseFiscale[];
};
export type CatalogueCreditsMissions = {
  source: string;
  annee_credits: number;
  unite_credits: string;
  bornes: [number, number];
  missions: {
    identifiant: string;
    libelle: string;
    credits: number;
    rendement_pourcent: number;
    // Programmes de la mission (PLF), pour l'aide au chiffrage.
    programmes?: { numero: string; libelle: string; credits: number }[];
  }[];
};
export type FourchetteDonnee = { bas: number; central: number; haut: number };
export type ClasseEntreprises = {
  id: string;
  libelle: string;
  part: FourchetteDonnee;
  effet: FourchetteDonnee;
  effectifs: number | null;
  entreprises: number | null;
};
export type Entreprises = {
  unite: string;
  annee_urssaf: number;
  annees_is: number[];
  leviers: {
    id: string;
    effet_national: FourchetteDonnee;
    sources: string[];
    nomenclatures: Record<"taille" | "secteur", ClasseEntreprises[]>;
  }[];
  controles: {
    id: string;
    annee: number;
    urssaf: number;
    reference: number;
    source: string;
    ecart: number;
  }[];
};
export type ClasseDepense = {
  id: string;
  consommation: number;
  effets: Record<string, FourchetteDonnee>;
};
export type DepenseMenages = {
  annee: number;
  annee_enquete: number;
  unite: string;
  leviers: string[];
  sources: string[];
  nomenclatures: Record<"decile" | "type_menage", ClasseDepense[]>;
  controles: {
    annee: number;
    modele: FourchetteDonnee;
    reference: number;
    ecart: number;
    source: string;
  }[];
};
