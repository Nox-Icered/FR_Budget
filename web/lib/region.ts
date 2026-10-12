// Attributs d'un tableau défilant : atteignable au clavier pour le faire défiler (RGAA,
// critère 7.3) et annoncé comme une région nommée.
import { texte } from "./textes.ts";

export const REGION = {
  tabIndex: 0,
  role: "region",
  "aria-label": texte("site.tableau_defilant"),
};
