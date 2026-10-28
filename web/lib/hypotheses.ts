// Hypothèse dont la plage est nulle (une seule source) : son incertitude n'entre pas dans les
// fourchettes publiées, ce que la page Hypothèses signale (docs/validation/plages_nulles.md).
export function plageNulle(plage: { basse: number; haute: number }): boolean {
  return plage.basse === plage.haute;
}
