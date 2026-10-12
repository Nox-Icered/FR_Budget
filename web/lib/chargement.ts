// Chargement, dans le navigateur, des réponses unitaires du simulateur (fichier statique copié
// par outils/copier-donnees.mjs, nommé d'après l'empreinte de la version de la page). Une seule
// requête par visite : la promesse est partagée par le simulateur et la comparaison, reliés par
// une navigation interne ; en cas d'échec, la tentative suivante relance la requête.
import { useEffect, useState } from "react";
import type { ReponsesUnitaires } from "./donnees";

export function adresseReponses(empreinte: string): string {
  return `/donnees/scenario-unitaire.${empreinte}.json`;
}

const promesses = new Map<string, Promise<ReponsesUnitaires>>();

export function chargerReponses(empreinte: string): Promise<ReponsesUnitaires> {
  const adresse = adresseReponses(empreinte);
  let promesse = promesses.get(adresse);
  if (!promesse) {
    promesse = fetch(adresse).then((r) => {
      if (!r.ok) throw new Error(`${adresse} : ${r.status}`);
      return r.json() as Promise<ReponsesUnitaires>;
    });
    promesse.catch(() => promesses.delete(adresse));
    promesses.set(adresse, promesse);
  }
  return promesse;
}

export type EtatChargement =
  | { etat: "en_cours" }
  | { etat: "pret"; donnees: ReponsesUnitaires }
  | { etat: "erreur" };

export function useReponses(empreinte: string): EtatChargement {
  const [resultat, setResultat] = useState<EtatChargement>({ etat: "en_cours" });
  useEffect(() => {
    let actif = true;
    chargerReponses(empreinte).then(
      (donnees) => actif && setResultat({ etat: "pret", donnees }),
      () => actif && setResultat({ etat: "erreur" }),
    );
    return () => {
      actif = false;
    };
  }, [empreinte]);
  return resultat;
}
