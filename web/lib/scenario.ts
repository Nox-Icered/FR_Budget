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

export function calculer(
  donnees: ReponsesUnitaires,
  levier: string,
  valeur: number,
  annee: number,
): LigneScenario[] {
  const reponse = donnees.leviers[levier].reponses[String(annee)];
  return donnees.annees.map((a, i) => {
    const dette = donnees.base_dette.map((b, k) => b[i] + valeur * reponse.unite_dette[k][i]);
    const solde = donnees.base_solde.map((b, k) => b[i] + valeur * reponse.unite_solde[k][i]);
    const ecartsDette = donnees.indices_effet.map((k) => valeur * reponse.unite_dette[k][i]);
    const ecartsSolde = donnees.indices_effet.map((k) => valeur * reponse.unite_solde[k][i]);
    return {
      annee: a,
      dette: encadrer(dette[0], dette),
      solde_primaire: encadrer(solde[0], solde),
      ecart_dette: encadrer(ecartsDette[0], ecartsDette),
      ecart_solde_primaire: encadrer(ecartsSolde[0], ecartsSolde),
    };
  });
}
