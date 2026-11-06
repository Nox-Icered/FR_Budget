// Répartition de l'effet des mesures par décile de niveau de vie, même calcul que le moteur
// (moteur/src/fr_budget/menages/deciles.py) : effet national d'une unité du levier réparti selon
// la part de chaque décile dans l'assiette (comptes nationaux distribués de l'Insee).
// Variation du revenu = moins l'effet sur le solde public. Bornes : extrêmes du produit des
// bornes de l'effet national par les parts de chaque variante ; plusieurs mesures : sommes.
import type { Deciles } from "./donnees.ts";
import type { Fourchette, MesureSite } from "./scenario.ts";

export type RepartitionDeciles = {
  milliards: Fourchette[];
  eurosParUc: Fourchette[];
  pourcentRevenu: Fourchette[];
  nonRepartis: string[];
};

const EUROS_PAR_MILLIARD = 1e9;
const UNITES_PAR_MILLION = 1e6;
const POURCENT = 100;

function avecTermesCroises(d: Deciles, mesures: MesureSite[]): MesureSite[] {
  const reglees = new Map(mesures.filter((m) => m.valeur !== 0).map((m) => [m.levier, m.valeur]));
  const croises: MesureSite[] = [];
  for (const [levier, l] of Object.entries(d.leviers)) {
    if (!l.interaction) continue;
    const [a, b] = l.interaction;
    const va = reglees.get(a);
    const vb = reglees.get(b);
    if (va !== undefined && vb !== undefined) croises.push({ levier, valeur: va * vb });
  }
  return [...mesures, ...croises];
}

// null si aucune mesure n'est réglée.
export function repartitionDeciles(d: Deciles, mesures: MesureSite[]): RepartitionDeciles | null {
  const reglees = mesures.filter((m) => m.valeur !== 0);
  if (reglees.length === 0) return null;
  const n = d.unites_consommation_millions.length;
  const total = Array.from({ length: n }, () => ({ bas: 0, central: 0, haut: 0 }));
  const nonRepartis: string[] = [];
  for (const m of avecTermesCroises(d, reglees)) {
    const l = d.leviers[m.levier];
    if (!l) {
      if (!nonRepartis.includes(m.levier)) nonRepartis.push(m.levier);
      continue;
    }
    const r = l.rendement;
    const effets = [r.bas, r.central, r.haut].map((v) => -m.valeur * v);
    for (let i = 0; i < n; i++) {
      const central = -m.valeur * r.central * l.centrale[i];
      const candidats = effets.flatMap((e) => l.variantes.map((p) => e * p[i]));
      total[i].bas += Math.min(central, ...candidats);
      total[i].central += central;
      total[i].haut += Math.max(central, ...candidats);
    }
  }
  const echelle = (f: Fourchette, k: number): Fourchette => ({
    bas: f.bas * k,
    central: f.central * k,
    haut: f.haut * k,
  });
  return {
    milliards: total,
    eurosParUc: total.map((f, i) =>
      echelle(f, EUROS_PAR_MILLIARD / (d.unites_consommation_millions[i] * UNITES_PAR_MILLION)),
    ),
    pourcentRevenu: total.map((f, i) => echelle(f, POURCENT / d.revenu_disponible_milliards[i])),
    nonRepartis,
  };
}
