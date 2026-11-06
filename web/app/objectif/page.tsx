import { texte } from "../../lib/textes";
import { lire, type Version } from "../../lib/donnees";
import { Objectif } from "./objectif";

export default function PageObjectif() {
  return (
    <>
      <h1>{texte("objectif.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("simulateur.bandeau")}
      </p>
      <p>{texte("objectif.intro")}</p>
      <Objectif version={lire<Version>("version.json")} />
      <p className="source">{texte("objectif.methode")}</p>
    </>
  );
}
