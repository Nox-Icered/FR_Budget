// Éditeur de barème de l'impôt sur le revenu : même calcul que le moteur
// (moteur/src/fr_budget/agrege/bareme_ir.py, ``effet_site``), fait dans le navigateur à partir
// des données exportées (donnees/bareme-ir.json). L'effet devient une mesure sur le levier
// générique « ir_bareme » (1 Md€ de 2025 de recettes en plus).
import type { MesureSite } from "./scenario";

export type Decote = { seuil_celibataire: number; seuil_couple: number; taux: number };
export type Bareme = { seuils: number[]; taux: number[]; decote: Decote | null };
export type SegmentBareme = {
  nom: string;
  foyers: number;
  parts: number;
  calage: number;
  calage_couples_uniforme: number;
  couples: number;
  quotients: number[];
};
export type DonneesBareme = {
  annee_bareme: number;
  annee_revenus: number;
  revalorisation: number;
  vers_euros_reference: number;
  bareme_reference: Bareme;
  calage_global: number;
  couples_uniforme: number;
  segments: SegmentBareme[];
  controles: { nom: string; bareme: Bareme; effet: Fourchette }[];
  levier: string;
  sources: string[];
  hypotheses: string[];
};
export type Fourchette = { bas: number; central: number; haut: number };

export const TRANCHES_MAX = 8;
// Au-delà, le barème s'éloigne des réformes chiffrées qui ont servi à valider le moteur : le
// site l'écrit (fiche bareme_ir, § 7).
export const TAUX_SIGNALE = 0.6;
const MILLIARD = 1e9;

export function impotParPart(b: Bareme, q: number): number {
  let total = 0;
  for (let i = 0; i < b.seuils.length; i++) {
    const haut = i + 1 < b.seuils.length ? b.seuils[i + 1] : Infinity;
    total += b.taux[i] * Math.max(0, Math.min(q, haut) - b.seuils[i]);
  }
  return total;
}

function decote(d: Decote, impot: number, couple: boolean): number {
  const seuil = couple ? d.seuil_couple : d.seuil_celibataire;
  return Math.min(impot, Math.max(0, seuil - d.taux * impot));
}

function impotFoyer(b: Bareme, q: number, parts: number, couple: boolean): number {
  let impot = parts * impotParPart(b, q);
  if (b.decote) impot -= decote(b.decote, impot, couple);
  return impot;
}

function impotMoyen(b: Bareme, s: SegmentBareme, couples: number): number {
  let total = 0;
  for (const q of s.quotients) {
    total += couples * impotFoyer(b, q, s.parts, true) + (1 - couples) * impotFoyer(b, q, s.parts, false);
  }
  return total / (s.parts * s.quotients.length);
}

function indexe(b: Bareme, facteur: number): Bareme {
  return {
    seuils: b.seuils.map((s) => s * facteur),
    taux: b.taux,
    decote: b.decote && {
      seuil_celibataire: b.decote.seuil_celibataire * facteur,
      seuil_couple: b.decote.seuil_couple * facteur,
      taux: b.decote.taux,
    },
  };
}

// Effet d'un barème saisi (sur la base du barème de référence), en Md€ de l'année de
// référence ; positif : recettes en hausse. Valeur centrale : calage par segment, part des
// couples par quantile ; fourchette : calage unique, part des couples uniforme.
export function effetBareme(d: DonneesBareme, reforme: Bareme): Fourchette {
  const r = 1 / d.revalorisation;
  const avant = indexe(d.bareme_reference, r);
  const apres = indexe(reforme, r);
  const total = (couples: (s: SegmentBareme) => number, calage: (s: SegmentBareme) => number) =>
    (d.segments.reduce((somme, s) => {
      const c = couples(s);
      return somme + s.foyers * s.parts * calage(s) * (impotMoyen(apres, s, c) - impotMoyen(avant, s, c));
    }, 0) /
      MILLIARD) *
    d.vers_euros_reference;
  const central = total((s) => s.couples, (s) => s.calage);
  const variantes = [
    total((s) => s.couples, () => d.calage_global),
    total(() => d.couples_uniforme, (s) => s.calage_couples_uniforme),
  ];
  return {
    bas: Math.min(central, ...variantes),
    central,
    haut: Math.max(central, ...variantes),
  };
}

export type ProblemeBareme = "tranches" | "seuils" | "taux" | "decote";

export function problemesBareme(b: Bareme): ProblemeBareme[] {
  const liste: ProblemeBareme[] = [];
  if (b.seuils.length === 0 || b.seuils.length !== b.taux.length || b.seuils.length > TRANCHES_MAX)
    liste.push("tranches");
  if (b.seuils[0] !== 0 || b.seuils.some((s, i) => !Number.isFinite(s) || (i > 0 && s <= b.seuils[i - 1])))
    liste.push("seuils");
  if (b.taux.some((t) => !Number.isFinite(t) || t < 0 || t > 1)) liste.push("taux");
  const dc = b.decote;
  if (dc && [dc.seuil_celibataire, dc.seuil_couple, dc.taux].some((v) => !Number.isFinite(v) || v < 0))
    liste.push("decote");
  return liste;
}

export function signale(b: Bareme): boolean {
  return b.taux.some((t) => t > TAUX_SIGNALE);
}

export function egal(a: Bareme, b: Bareme): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

// Lien : « b=seuil:taux,seuil:taux…;celibataire,couple,taux » (taux en %, sans décote : « ;- »).
export function encoderBareme(b: Bareme): string {
  const tranches = b.seuils.map((s, i) => `${s}:${Math.round(b.taux[i] * 10000) / 100}`).join(",");
  const d = b.decote;
  return `${tranches};${d ? `${d.seuil_celibataire},${d.seuil_couple},${d.taux}` : "-"}`;
}

export function decoderBareme(texte: string): Bareme | null {
  const [tranches, dec] = texte.split(";");
  if (tranches === undefined || dec === undefined) return null;
  const paires = tranches.split(",").map((p) => p.split(":").map(Number));
  if (paires.some((p) => p.length !== 2 || p.some((v) => !Number.isFinite(v)))) return null;
  let decote: Decote | null = null;
  if (dec !== "-") {
    const v = dec.split(",").map(Number);
    if (v.length !== 3 || v.some((x) => !Number.isFinite(x))) return null;
    decote = { seuil_celibataire: v[0], seuil_couple: v[1], taux: v[2] };
  }
  return { seuils: paires.map((p) => p[0]), taux: paires.map((p) => p[1] / 100), decote };
}

export function mesureBareme(d: DonneesBareme, b: Bareme | undefined): MesureSite[] {
  if (!b || egal(b, d.bareme_reference) || problemesBareme(b).length > 0) return [];
  const effet = effetBareme(d, b).central;
  return effet === 0 ? [] : [{ levier: d.levier, valeur: effet }];
}
