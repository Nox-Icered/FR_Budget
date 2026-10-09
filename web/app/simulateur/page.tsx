import { texte, nombre } from "../../lib/textes";
import {
  lire,
  type Baseline,
  type CatalogueDepensesFiscales,
  type ReponsesUnitaires,
} from "../../lib/donnees";
import { Simulateur } from "./simulateur";

const deuxDecimales = (v: number) =>
  new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2, minimumFractionDigits: 2 }).format(v);

export default function PageSimulateur() {
  const donnees = lire<ReponsesUnitaires>("scenario-unitaire.json");
  const baseline = lire<Baseline>("baseline.json");
  const catalogue = lire<CatalogueDepensesFiscales>("depenses-fiscales.json");
  return (
    <>
      <h1>{texte("simulateur.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("simulateur.bandeau")}
      </p>
      <p>{texte("simulateur.intro")}</p>
      <Simulateur donnees={donnees} catalogue={catalogue} raccord={baseline.annee_raccord} />
      <h2>{texte("simulateur.methode_titre")}</h2>
      <p>
        {texte("simulateur.methode", {
          rendement_tva: nombre(donnees.leviers.tva_taux_normal.rendement_unitaire),
          rendement_gazole: deuxDecimales(donnees.leviers.accise_gazole.rendement_unitaire),
          rendement_essences: deuxDecimales(donnees.leviers.accise_essences.rendement_unitaire),
          rendement_is: nombre(donnees.leviers.is_taux_normal.rendement_unitaire),
          rendement_surtaxe: deuxDecimales(
            donnees.leviers.is_surtaxe_grandes_entreprises.rendement_unitaire,
          ),
        })}
      </p>
      <p>{texte("simulateur.methode_depenses_fiscales", { annee: catalogue.annee_cout })}</p>
      <ul>
        <li>{texte("simulateur.limite_comportement")}</li>
        <li>{texte("simulateur.limite_croissance")}</li>
        <li>{texte("simulateur.limite_fourchette")}</li>
        <li>{texte("simulateur.limite_tva_accise")}</li>
        <li>{texte("simulateur.limite_is_calendrier")}</li>
        <li>{texte("simulateur.limite_depenses_fiscales")}</li>
      </ul>
      <p>
        <a href="/validation/">{texte("simulateur.lien_validation")}</a>
      </p>
    </>
  );
}
