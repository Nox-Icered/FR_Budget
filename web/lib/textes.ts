// Tous les textes affichés viennent de messages/fr.json (préparation de la version anglaise).
import fr from "../messages/fr.json" with { type: "json" };

type Arbre = { [cle: string]: string | Arbre };

export function texte(
  cle: string,
  variables: Record<string, string | number> = {},
  messages: Arbre = fr as Arbre,
): string {
  let noeud: string | Arbre | undefined = messages;
  for (const partie of cle.split(".")) {
    noeud = typeof noeud === "object" ? noeud[partie] : undefined;
  }
  if (typeof noeud !== "string") {
    throw new Error(`texte manquant : ${cle}`);
  }
  return noeud.replace(/\{(\w+)\}/g, (_, nom: string) => {
    if (!(nom in variables)) throw new Error(`variable manquante « ${nom} » pour ${cle}`);
    return String(variables[nom]);
  });
}

const FORMAT = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1, minimumFractionDigits: 1 });

export function nombre(valeur: number): string {
  return FORMAT.format(valeur);
}
