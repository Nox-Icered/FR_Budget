// Dépense supplémentaire des ménages à consommation inchangée pour un scénario du simulateur :
// chaque mesure de TVA ou d'accise multiplie l'effet d'une unité de son levier
// (depense-menages.json, fr_budget.menages.depense) ; les mesures s'additionnent, bornes
// comprises. Les effets croisés (TVA sur la hausse d'accise) sont négligés.
import type { ClasseDepense, DepenseMenages, FourchetteDonnee } from "./donnees.ts";

export type LigneDepense = {
  classe: ClasseDepense;
  effet: FourchetteDonnee;
  part: FourchetteDonnee;
};

export function effetDepense(
  donnees: DepenseMenages,
  nomenclature: "decile" | "type_menage",
  valeurs: Record<string, number>,
): LigneDepense[] | null {
  const actifs = donnees.leviers.filter((l) => (valeurs[l] ?? 0) !== 0);
  if (actifs.length === 0) return null;
  return donnees.nomenclatures[nomenclature].map((classe) => {
    const effet = { bas: 0, central: 0, haut: 0 };
    for (const l of actifs) {
      const f = classe.effets[l];
      const v = valeurs[l];
      const a = f.bas * v;
      const b = f.haut * v;
      effet.bas += Math.min(a, b);
      effet.central += f.central * v;
      effet.haut += Math.max(a, b);
    }
    const part = {
      bas: effet.bas / classe.consommation,
      central: effet.central / classe.consommation,
      haut: effet.haut / classe.consommation,
    };
    return { classe, effet, part };
  });
}
