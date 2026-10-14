// Effet d'un scénario du simulateur sur la charge des entreprises : chaque mesure multiplie
// l'effet d'une unité de son levier (entreprises.json), réparti entre les classes d'entreprises
// selon leur part de l'assiette (fr_budget.entreprises.repartition). Les leviers qui partagent
// une nomenclature s'additionnent ; les bornes des fourchettes s'additionnent aussi.
import type { ClasseEntreprises, Entreprises, FourchetteDonnee } from "./donnees.ts";

export type Groupe = { leviers: string[]; nomenclature: "taille" | "secteur" };

// Cotisations et allègements : données de l'Urssaf ; impôt sur les sociétés : données de la DGFiP.
export const GROUPES: Record<string, string[]> = {
  cotisations: ["cotisations_patronales_taux", "allegements_generaux"],
  impot_societes: ["is_taux_normal", "is_surtaxe_grandes_entreprises"],
};

function multiplier(f: FourchetteDonnee, v: number): FourchetteDonnee {
  const a = f.bas * v;
  const b = f.haut * v;
  return { bas: Math.min(a, b), central: f.central * v, haut: Math.max(a, b) };
}

export function effetScenario(
  donnees: Entreprises,
  leviers: string[],
  nomenclature: "taille" | "secteur",
  valeurs: Record<string, number>,
): { classe: ClasseEntreprises; effet: FourchetteDonnee }[] | null {
  const actifs = donnees.leviers.filter((l) => leviers.includes(l.id) && (valeurs[l.id] ?? 0) !== 0);
  if (actifs.length === 0) return null;
  const classes = actifs.find((l) => l.nomenclatures[nomenclature].length > 0)?.nomenclatures[
    nomenclature
  ];
  if (!classes) return null;
  return classes.map((classe) => {
    const effet = { bas: 0, central: 0, haut: 0 };
    for (const l of actifs) {
      const c = l.nomenclatures[nomenclature].find((x) => x.id === classe.id);
      if (!c) continue;
      const e = multiplier(c.effet, valeurs[l.id]);
      effet.bas += e.bas;
      effet.central += e.central;
      effet.haut += e.haut;
    }
    return { classe, effet };
  });
}
