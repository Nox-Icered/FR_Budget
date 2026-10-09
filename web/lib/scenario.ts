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

// Plusieurs leviers s'additionnent (même année d'entrée), comme dans le moteur.
export function calculer(
  donnees: ReponsesUnitaires,
  mesures: MesureSite[],
  annee: number,
): LigneScenario[] {
  const reponses = mesures.map((m) => ({
    valeur: m.valeur,
    r: donnees.leviers[m.levier].reponses[String(annee)],
  }));
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
  const somme = (k: number, i: number, cle: "unite_dette" | "unite_solde") =>
    reponses.reduce((total, { valeur, r }) => total + valeur * r[cle][indice(k, valeur)][i], 0);
  return donnees.annees.map((a, i) => {
    const dette = donnees.base_dette.map((b, k) => b[i] + somme(k, i, "unite_dette"));
    const solde = donnees.base_solde.map((b, k) => b[i] + somme(k, i, "unite_solde"));
    const ecartsDette = donnees.indices_effet.map((k) => somme(k, i, "unite_dette"));
    const ecartsSolde = donnees.indices_effet.map((k) => somme(k, i, "unite_solde"));
    return {
      annee: a,
      dette: encadrer(dette[0], dette),
      solde_primaire: encadrer(solde[0], solde),
      ecart_dette: encadrer(ecartsDette[0], ecartsDette),
      ecart_solde_primaire: encadrer(ecartsSolde[0], ecartsSolde),
    };
  });
}
