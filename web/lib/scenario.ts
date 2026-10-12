// Calcul du scénario dans le navigateur, sans serveur ni stockage : le modèle est linéaire
// dans la valeur du levier (moteur/src/fr_budget/scenario.py, ``reponse_lineaire``).
// Niveau = base + x * unité, sur chaque trajectoire ; bornes = extrêmes.
import type { ReponsesUnitaires } from "./donnees";

export type Fourchette = { bas: number; central: number; haut: number };
export type LigneScenario = {
  annee: number;
  dette: Fourchette;
  solde_primaire: Fourchette;
  ecart_dette: Fourchette;
  ecart_solde_primaire: Fourchette;
};

// « + 0 » ramène -0 (produit d'une valeur négative par zéro) à 0, pour l'affichage.
function encadrer(central: number, valeurs: number[]): Fourchette {
  return {
    bas: Math.min(central, ...valeurs) + 0,
    central: central + 0,
    haut: Math.max(central, ...valeurs) + 0,
  };
}

export type MesureSite = { levier: string; valeur: number };

// Plusieurs leviers s'additionnent (même année d'entrée), comme dans le moteur. Avec
// ``croissance`` (interrupteur, désactivé par défaut), chaque réponse reçoit m fois son
// supplément de croissance ; le multiplicateur m est central sur toutes les trajectoires, et
// les coins (effet bas ou haut, multiplicateur bas ou haut, commun à toutes les mesures)
// élargissent la fourchette, comme dans fr_budget.scenario.
export function calculer(
  donnees: ReponsesUnitaires,
  mesures: MesureSite[],
  annee: number,
  croissance = false,
): LigneScenario[] {
  const reponses = mesures.map((m) => {
    const levier = donnees.leviers[m.levier];
    return { valeur: m.valeur, r: levier.reponses[String(annee)], mult: levier.multiplicateur };
  });
  // Trajectoires des bornes de l'effet (indices_effet[1] : effet bas, [2] : effet haut). Comme
  // dans le moteur, la borne basse additionne la réponse basse des mesures positives et la
  // réponse haute des mesures négatives (et inversement pour la borne haute).
  const [, kBas, kHaut] = donnees.indices_effet;
  const indice = (k: number, valeur: number) => {
    if (valeur >= 0) return k;
    if (k === kBas) return kHaut;
    if (k === kHaut) return kBas;
    return k;
  };
  type Borne = "bas" | "central" | "haut";
  const somme = (k: number, i: number, cle: "dette" | "solde", borne: Borne | null) =>
    reponses.reduce((total, { valeur, r, mult }) => {
      const kk = indice(k, valeur);
      const unite = r[`unite_${cle}`][kk][i];
      const supplement = borne && mult ? mult[borne] * (r[`croissance_${cle}`]?.[kk][i] ?? 0) : 0;
      return total + valeur * (unite + supplement);
    }, 0);
  const central: Borne | null = croissance ? "central" : null;
  const coins: [number, Borne][] = croissance
    ? [
        [kBas, "bas"],
        [kHaut, "bas"],
        [kBas, "haut"],
        [kHaut, "haut"],
      ]
    : [];
  return donnees.annees.map((a, i) => {
    const niveaux = (cle: "dette" | "solde") => {
      const base = cle === "dette" ? donnees.base_dette : donnees.base_solde;
      return [
        ...base.map((b, k) => b[i] + somme(k, i, cle, central)),
        ...coins.map(([k, j]) => base[k][i] + somme(k, i, cle, j)),
      ];
    };
    const ecarts = (cle: "dette" | "solde") => [
      ...donnees.indices_effet.map((k) => somme(k, i, cle, central)),
      ...coins.map(([k, j]) => somme(k, i, cle, j)),
    ];
    const [dette, solde, ecartsDette, ecartsSolde] = [
      niveaux("dette"),
      niveaux("solde"),
      ecarts("dette"),
      ecarts("solde"),
    ];
    return {
      annee: a,
      dette: encadrer(dette[0], dette),
      solde_primaire: encadrer(solde[0], solde),
      ecart_dette: encadrer(ecartsDette[0], ecartsDette),
      ecart_solde_primaire: encadrer(ecartsSolde[0], ecartsSolde),
    };
  });
}
