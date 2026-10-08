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
export type ComptesApu = Record<string, Record<string, Serie>>;
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
export type Version = { moteur: string; registres: string; donnees: string };
