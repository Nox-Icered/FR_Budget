// Chargement, dans le navigateur, des réponses unitaires du simulateur (fichier statique copié
// par outils/copier-donnees.mjs). Une seule requête par visite : la promesse est partagée par
// le simulateur et la comparaison ; en cas d'échec, la tentative suivante relance la requête.
import { useEffect, useState } from "react";
import type { ReponsesUnitaires } from "./donnees";

export const ADRESSE_REPONSES = "/donnees/scenario-unitaire.json";

let promesse: Promise<ReponsesUnitaires> | null = null;

export function chargerReponses(): Promise<ReponsesUnitaires> {
  promesse ??= fetch(ADRESSE_REPONSES).then((r) => {
    if (!r.ok) throw new Error(`${ADRESSE_REPONSES} : ${r.status}`);
    return r.json() as Promise<ReponsesUnitaires>;
  });
  promesse.catch(() => {
    promesse = null;
  });
  return promesse;
}

export type EtatChargement =
  | { etat: "en_cours" }
  | { etat: "pret"; donnees: ReponsesUnitaires }
  | { etat: "erreur" };

export function useReponses(): EtatChargement {
  const [resultat, setResultat] = useState<EtatChargement>({ etat: "en_cours" });
  useEffect(() => {
    let actif = true;
    chargerReponses().then(
      (donnees) => actif && setResultat({ etat: "pret", donnees }),
      () => actif && setResultat({ etat: "erreur" }),
    );
    return () => {
      actif = false;
    };
  }, []);
  return resultat;
}
