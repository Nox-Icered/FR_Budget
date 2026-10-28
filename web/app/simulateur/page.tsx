import { texte, nombre } from "../../lib/textes";
import {
  lire,
  type Baseline,
  type CatalogueCreditsMissions,
  type CatalogueDepensesFiscales,
  type DepenseMenages,
  type Entreprises,
  type ReponsesUnitaires,
  type Version,
} from "../../lib/donnees";
import { Simulateur } from "./simulateur";
import { chemin } from "../../lib/chemin";

const deuxDecimales = (v: number) =>
  new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2, minimumFractionDigits: 2 }).format(v);

export default function PageSimulateur() {
  const donnees = lire<ReponsesUnitaires>("scenario-unitaire.json");
  const baseline = lire<Baseline>("baseline.json");
  const catalogue = lire<CatalogueDepensesFiscales>("depenses-fiscales.json");
  const missions = lire<CatalogueCreditsMissions>("credits-missions.json");
  const version = lire<Version>("version.json");
  const entreprises = lire<Entreprises>("entreprises.json");
  const depense = lire<DepenseMenages>("depense-menages.json");
  return (
    <>
      <h1>{texte("simulateur.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("simulateur.bandeau")}
      </p>
      <p>{texte("simulateur.intro")}</p>
      <Simulateur
        catalogue={catalogue}
        missions={missions}
        raccord={baseline.annee_raccord}
        version={version}
        entreprises={entreprises}
        depense={depense}
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
      <p>
        {texte("simulateur.methode_cotisations", {
          point: deuxDecimales(donnees.leviers.cotisations_patronales_taux.rendement_unitaire),
          allegements: deuxDecimales(-donnees.leviers.allegements_generaux.rendement_unitaire),
        })}
      </p>
      <p>
        {texte("simulateur.methode_ir", {
          rendement: deuxDecimales(-donnees.leviers.ir_seuils_bareme.rendement_unitaire),
        })}
      </p>
      <p>
        {texte("simulateur.methode_prime_activite", {
          pente: deuxDecimales(donnees.leviers.prime_activite_pente.taux_reference),
          cout: deuxDecimales(-donnees.leviers.prime_activite_pente.rendement_unitaire),
        })}
      </p>
      <p>
        {texte("simulateur.methode_retraites", {
          effet: deuxDecimales(donnees.leviers.retraites_age_depart.effet_plein ?? 0),
          duree: donnees.leviers.retraites_age_depart.duree_montee ?? 0,
          duree_bas: donnees.leviers.retraites_age_depart.duree_montee_plage?.bas ?? 0,
          duree_haut: donnees.leviers.retraites_age_depart.duree_montee_plage?.haut ?? 0,
        })}
      </p>
      <p>
        {texte("simulateur.methode_retraites_age_legal", {
          effet: deuxDecimales(donnees.leviers.retraites_age_legal.effet_plein ?? 0),
          duree: donnees.leviers.retraites_age_legal.duree_montee ?? 0,
        })}
      </p>
      {donnees.croissance && (
        <p>
          {texte("simulateur.methode_croissance", {
            persistance: Math.round(donnees.croissance.persistance * 100),
            alpha: deuxDecimales(donnees.croissance.effet_solde),
            tva_bas: deuxDecimales(donnees.leviers.tva_taux_normal.multiplicateur?.bas ?? 0),
            tva_haut: deuxDecimales(donnees.leviers.tva_taux_normal.multiplicateur?.haut ?? 0),
            depenses_bas: deuxDecimales(donnees.leviers.credits_missions.multiplicateur?.bas ?? 0),
            depenses_haut: deuxDecimales(donnees.leviers.credits_missions.multiplicateur?.haut ?? 0),
          })}
        </p>
      )}
      <ul>
        <li>{texte("simulateur.limite_comportement")}</li>
        <li>{texte("simulateur.limite_croissance")}</li>
        <li>{texte("simulateur.limite_croissance_module")}</li>
        <li>{texte("simulateur.limite_fourchette")}</li>
        <li>{texte("simulateur.limite_tva_accise")}</li>
        <li>{texte("simulateur.limite_is_calendrier")}</li>
        <li>{texte("simulateur.limite_depenses_fiscales")}</li>
        <li>{texte("simulateur.limite_credits_missions")}</li>
        <li>{texte("simulateur.limite_dotations")}</li>
        <li>{texte("simulateur.limite_remunerations")}</li>
        <li>{texte("simulateur.limite_indexation")}</li>
        <li>{texte("simulateur.limite_csg")}</li>
        <li>{texte("simulateur.limite_cotisations")}</li>
        <li>{texte("simulateur.limite_ir")}</li>
        <li>{texte("simulateur.limite_prime_activite")}</li>
        <li>{texte("simulateur.limite_retraites")}</li>
      </ul>
      <p>
        <a href={chemin("/validation/")}>{texte("simulateur.lien_validation")}</a>
      </p>
    </>
  );
}
