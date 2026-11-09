// Sections du simulateur : les curseurs regroupés par thème (maquette du 2 novembre 2026).
// Chaque levier publié appartient à une seule section (tests/sections.test.ts).
export const SECTIONS: { id: string; leviers: string[] }[] = [
  { id: "consommation", leviers: ["tva_taux_normal", "accise_gazole", "accise_essences"] },
  {
    id: "entreprises",
    leviers: [
      "is_taux_normal",
      "is_surtaxe_grandes_entreprises",
      "cotisations_patronales_taux",
      "allegements_generaux",
    ],
  },
  {
    id: "prelevements_menages",
    leviers: [
      "csg_activite",
      "csg_retraites",
      "csg_capital",
      "ir_seuils_bareme",
      "ir_plafond_quotient_familial",
      "ir_quotient_familial_effet",
      "ir_quotient_conjugal_effet",
    ],
  },
  { id: "prestations", leviers: ["indexation_pensions_prestations", "prime_activite_pente"] },
  { id: "retraites", leviers: ["retraites_age_depart", "retraites_age_legal"] },
  {
    id: "assurance_chomage",
    leviers: [
      "chomage_contribution_patronale",
      "chomage_revalorisation",
      "chomage_duree_indemnisation",
      "chomage_affiliation_mois",
      "chomage_degressivite_points",
    ],
  },
  { id: "assurance_maladie", leviers: ["ondam_progression", "franchises_participations", "ij_plafond_smic"] },
  {
    id: "fonction_publique_collectivites",
    leviers: [
      "remunerations_point_indice",
      "remunerations_effectifs",
      "dotations_dgf",
      "dotations_compensations",
    ],
  },
];

// Recherche sans accents ni casse : tous les mots doivent apparaître dans le texte.
const normaliser = (s: string) =>
  s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export function correspond(texteLevier: string, requete: string): boolean {
  const cible = normaliser(texteLevier);
  return normaliser(requete)
    .split(/\s+/)
    .filter(Boolean)
    .every((mot) => cible.includes(mot));
}

// Nombre de leviers réglés (valeur non nulle) d'une section.
export function reglees(leviers: string[], valeurs: Record<string, number>): number {
  return leviers.filter((id) => (valeurs[id] ?? 0) !== 0).length;
}
