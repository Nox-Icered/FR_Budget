import { texte, nombre } from "../../lib/textes";
import { lire, type Baseline, type ReponsesUnitaires } from "../../lib/donnees";
import { Simulateur } from "./simulateur";

export default function PageSimulateur() {
  const donnees = lire<ReponsesUnitaires>("scenario-unitaire.json");
  const baseline = lire<Baseline>("baseline.json");
  return (
    <>
      <h1>{texte("simulateur.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("simulateur.bandeau")}
      </p>
      <p>{texte("simulateur.intro")}</p>
      <Simulateur donnees={donnees} raccord={baseline.annee_raccord} />
      <h2>{texte("simulateur.methode_titre")}</h2>
      <p>
        {texte("simulateur.methode", {
          rendement: nombre(donnees.leviers.tva_taux_normal.rendement_unitaire),
          effet: new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2 }).format(
            donnees.leviers.tva_taux_normal.effet_unitaire,
          ),
        })}
      </p>
      <ul>
        <li>{texte("simulateur.limite_comportement")}</li>
        <li>{texte("simulateur.limite_croissance")}</li>
        <li>{texte("simulateur.limite_fourchette")}</li>
      </ul>
      <p>
        <a href="/validation/">{texte("simulateur.lien_validation")}</a>
      </p>
    </>
  );
}
