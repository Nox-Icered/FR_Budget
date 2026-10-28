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
// les extrêmes du multiplicateur de chaque mesure, choisis année par année indépendamment des
// autres mesures (effet bas ou haut), élargissent la fourchette, comme dans fr_budget.scenario.
// Les extrêmes sont pris aux deux bornes de alpha (effet de l'écart de production sur le solde) :
// le supplément vaut alors supplément central + (alpha - alpha central) * variation par point.
export function calculer(
  donnees: ReponsesUnitaires,
  mesures: MesureSite[],
  annee: number,
  croissance = false,
): LigneScenario[] {
  const reponses = mesures.map((m) => {
    const levier = donnees.leviers[m.levier];
    // Levier non linéaire : réponse exacte du cran choisi, déjà ordonnée par borne ; elle compte
    // une fois (valeur 1) et ses bornes ne s'échangent pas.
    const cran = levier.grille?.[String(m.valeur)]?.[String(annee)];
    if (cran) return { valeur: 1, r: cran, mult: levier.multiplicateur, grille: true };
    return {
      valeur: m.valeur,
      r: levier.reponses[String(annee)],
      mult: levier.multiplicateur,
      grille: false,
    };
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
  type Reponse = (typeof reponses)[number]["r"];
  const alphaCentral = donnees.croissance?.effet_solde ?? 0;
  const plageAlpha = donnees.croissance?.effet_solde_plage;
  const alphas = plageAlpha ? [...new Set([plageAlpha.bas, plageAlpha.haut])] : [alphaCentral];
  const supplement = (r: Reponse, kk: number, i: number, cle: "dette" | "solde", alpha: number) =>
    (r[`croissance_${cle}`]?.[kk][i] ?? 0) +
    (alpha - alphaCentral) * (r[`croissance_alpha_${cle}`]?.[kk][i] ?? 0);
  const somme = (
    k: number,
    i: number,
    cle: "dette" | "solde",
    borne: Borne | null,
    alpha = alphaCentral,
  ) =>
    reponses.reduce((total, { valeur, r, mult, grille }) => {
      const kk = grille ? k : indice(k, valeur);
      const unite = r[`unite_${cle}`][kk][i];
      const plus = borne && mult ? mult[borne] * supplement(r, kk, i, cle, alpha) : 0;
      return total + valeur * (unite + plus);
    }, 0);
  const central: Borne | null = croissance ? "central" : null;
  // Écart à la trajectoire au multiplicateur central quand le multiplicateur de chaque mesure
  // prend, pour l'année, la borne qui donne l'écart le plus bas (ou le plus haut) : la réponse
  // est linéaire dans chaque multiplicateur.
  const extreme = (
    k: number,
    i: number,
    cle: "dette" | "solde",
    choisir: (...v: number[]) => number,
    alpha: number,
  ) =>
    reponses.reduce((total, { valeur, r, mult, grille }) => {
      if (!mult) return total;
      const kk = grille ? k : indice(k, valeur);
      const c = supplement(r, kk, i, cle, alpha);
      return total + choisir(0, valeur * (mult.bas - mult.central) * c, valeur * (mult.haut - mult.central) * c);
    }, 0);
  // Extrême d'un coin : le plus extrême, sur les bornes de alpha, de la trajectoire au
  // multiplicateur central plus les extrêmes des multiplicateurs.
  const coin = (k: number, i: number, cle: "dette" | "solde", choisir: (...v: number[]) => number) =>
    choisir(...alphas.map((a) => somme(k, i, cle, central, a) + extreme(k, i, cle, choisir, a)));
  const coins: [number, (...v: number[]) => number][] = croissance
    ? [
        [kBas, Math.min],
        [kBas, Math.max],
        [kHaut, Math.min],
        [kHaut, Math.max],
      ]
    : [];
  return donnees.annees.map((a, i) => {
    const niveaux = (cle: "dette" | "solde") => {
      const base = cle === "dette" ? donnees.base_dette : donnees.base_solde;
      return [
        ...base.map((b, k) => b[i] + somme(k, i, cle, central)),
        ...coins.map(([k, choisir]) => base[k][i] + coin(k, i, cle, choisir)),
      ];
    };
    const ecarts = (cle: "dette" | "solde") => [
      ...donnees.indices_effet.map((k) => somme(k, i, cle, central)),
      ...coins.map(([k, choisir]) => coin(k, i, cle, choisir)),
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
