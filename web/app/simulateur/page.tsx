import { texte, nombre } from "../../lib/textes";
import {
  lire,
  type Baseline,
  type CatalogueCreditsMissions,
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
  const missions = lire<CatalogueCreditsMissions>("credits-missions.json");
  return (
    <>
      <h1>{texte("simulateur.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("simulateur.bandeau")}
      </p>
      <p>{texte("simulateur.intro")}</p>
      <Simulateur
        donnees={donnees}
        catalogue={catalogue}
        missions={missions}
        raccord={baseline.annee_raccord}
      />
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
      <p>{texte("simulateur.methode_credits_missions", { annee: missions.annee_credits })}</p>
      <p>
        {texte("simulateur.methode_dotations", {
          etat_dgf: deuxDecimales(-(donnees.leviers.dotations_dgf.effet_etat_unitaire ?? 0)),
          apu_dgf: deuxDecimales(-donnees.leviers.dotations_dgf.rendement_unitaire),
        })}
      </p>
      <p>
        {texte("simulateur.methode_remunerations", {
          brut_point: deuxDecimales(
            -(donnees.leviers.remunerations_point_indice.effet_brut_unitaire ?? 0),
          ),
          net_point: deuxDecimales(-donnees.leviers.remunerations_point_indice.rendement_unitaire),
          brut_effectifs: deuxDecimales(
            -(donnees.leviers.remunerations_effectifs.effet_brut_unitaire ?? 0),
          ),
          net_effectifs: deuxDecimales(-donnees.leviers.remunerations_effectifs.rendement_unitaire),
        })}
      </p>
      <p>
        {texte("simulateur.methode_indexation", {
          brut: deuxDecimales(
            -(donnees.leviers.indexation_pensions_prestations.effet_brut_unitaire ?? 0),
          ),
          net: deuxDecimales(-donnees.leviers.indexation_pensions_prestations.rendement_unitaire),
        })}
      </p>
      <p>
        {texte("simulateur.methode_csg", {
          annee: donnees.annee_reference,
          activite: deuxDecimales(donnees.leviers.csg_activite.rendement_unitaire),
          retraites: deuxDecimales(donnees.leviers.csg_retraites.rendement_unitaire),
          capital: deuxDecimales(donnees.leviers.csg_capital.rendement_unitaire),
        })}
      </p>
      <ul>
        <li>{texte("simulateur.limite_comportement")}</li>
        <li>{texte("simulateur.limite_croissance")}</li>
        <li>{texte("simulateur.limite_fourchette")}</li>
        <li>{texte("simulateur.limite_tva_accise")}</li>
        <li>{texte("simulateur.limite_is_calendrier")}</li>
        <li>{texte("simulateur.limite_depenses_fiscales")}</li>
        <li>{texte("simulateur.limite_credits_missions")}</li>
        <li>{texte("simulateur.limite_dotations")}</li>
        <li>{texte("simulateur.limite_remunerations")}</li>
        <li>{texte("simulateur.limite_indexation")}</li>
        <li>{texte("simulateur.limite_csg")}</li>
      </ul>
      <p>
        <a href="/validation/">{texte("simulateur.lien_validation")}</a>
      </p>
    </>
  );
}
