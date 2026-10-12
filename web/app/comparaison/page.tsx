import { texte } from "../../lib/textes";
import {
  lire,
  type CatalogueCreditsMissions,
  type CatalogueDepensesFiscales,
  type Version,
} from "../../lib/donnees";
import { Comparaison } from "./comparaison";

export default function PageComparaison() {
  return (
    <>
      <h1>{texte("comparaison.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("simulateur.bandeau")}
      </p>
      <p>{texte("comparaison.intro")}</p>
      <Comparaison
        catalogue={lire<CatalogueDepensesFiscales>("depenses-fiscales.json")}
        missions={lire<CatalogueCreditsMissions>("credits-missions.json")}
        version={lire<Version>("version.json")}
      />
      <p className="source">{texte("partage.explication")}</p>
    </>
  );
}
