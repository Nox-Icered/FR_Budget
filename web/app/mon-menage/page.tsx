import { texte } from "../../lib/textes";
import { lire, type MenagesTypes } from "../../lib/donnees";
import { Formulaire } from "./formulaire";

export default function MonMenage() {
  const { saisie } = lire<MenagesTypes>("menages-types.json");
  return (
    <>
      <h1>{texte("mon_menage.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("menages.bandeau")}
      </p>
      <p>{texte("mon_menage.intro", { annee: saisie.annee })}</p>
      <p>{texte("mon_menage.confidentialite")}</p>
      <Formulaire bornes={saisie} />
      <p className="source">{texte("mon_menage.limites")}</p>
      <p className="source">{texte("menages.limites")}</p>
      <p className="source">{texte("menages.lien_fiche")}</p>
    </>
  );
}
