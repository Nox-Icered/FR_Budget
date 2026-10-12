// Lecture, au moment de la construction, des fichiers exportés par l'API (web/donnees/).
import { readFileSync } from "node:fs";
import { join } from "node:path";

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
};
export type Comparaison = {
  reference: string;
  modele: number;
  valeur_reference: number;
  ecart: number;
  tolerance: number;
  dans_la_tolerance: boolean;
  unite: string;
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
  leviers: Record<
    string,
    {
      statut: "valide" | "beta" | "non_publie";
      rendement_unitaire: number;
      effet_unitaire: number;
      taux_reference: number;
      effet_etat_unitaire?: number;
      effet_brut_unitaire?: number;
      bornes: [number, number];
      reponses: Record<string, { unite_dette: number[][]; unite_solde: number[][] }>;
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
  missions: { identifiant: string; libelle: string; credits: number; rendement_pourcent: number }[];
};
