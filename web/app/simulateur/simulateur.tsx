"use client";
// Simulateur : le calcul se fait dans le navigateur ; rien n'est envoyé ni enregistré.
import { useId, useState } from "react";
import { texte, nombre } from "../../lib/textes";
import type {
  CatalogueCreditsMissions,
  CatalogueDepensesFiscales,
  ReponsesUnitaires,
} from "../../lib/donnees";
import { calculer } from "../../lib/scenario";
import { mesuresDepensesFiscales } from "../../lib/depenses-fiscales";
import { ReglagesDepensesFiscales } from "./depenses-fiscales";
import { mesuresCreditsMissions } from "../../lib/credits-missions";
import { ReglagesCreditsMissions } from "./credits-missions";
import { GraphiqueDette } from "../baseline/graphique";

// Ordre d'affichage et pas de réglage de chaque levier (en points ou en centimes par litre).
// Les bornes du curseur sont arrondies vers l'intérieur au pas, pour que 0 reste sur la grille.
const LEVIERS: { id: string; pas: number }[] = [
  { id: "tva_taux_normal", pas: 0.5 },
  { id: "accise_gazole", pas: 1 },
  { id: "accise_essences", pas: 1 },
  { id: "is_taux_normal", pas: 0.5 },
  { id: "is_surtaxe_grandes_entreprises", pas: 1 },
];
const ANNEES_AFFICHEES = [2027, 2030, 2035, 2040, 2046];

export function Simulateur({
  donnees,
  catalogue,
  missions,
  raccord,
}: {
  donnees: ReponsesUnitaires;
  catalogue: CatalogueDepensesFiscales;
  missions: CatalogueCreditsMissions;
  raccord: number;
}) {
  const leviers = LEVIERS.filter((l) => l.id in donnees.leviers);
  const annees = Object.keys(donnees.leviers[leviers[0].id].reponses).map(Number);
  const [valeurs, setValeurs] = useState<Record<string, number>>(
    Object.fromEntries(leviers.map((l) => [l.id, 0])),
  );
  const [parImpot, setParImpot] = useState<Record<string, number>>({});
  const [parDepense, setParDepense] = useState<Record<string, number>>({});
  const [parMission, setParMission] = useState<Record<string, number>>({});
  const [annee, setAnnee] = useState(annees[0]);
  const idBase = useId();
  const lignes = calculer(
    donnees,
    [
      ...leviers.map((l) => ({ levier: l.id, valeur: valeurs[l.id] })),
      ...mesuresDepensesFiscales(catalogue, parImpot, parDepense),
      ...mesuresCreditsMissions(missions, parMission),
    ],
    annee,
  );
  const signe = (v: number) => (v > 0 ? `+${nombre(v)}` : nombre(v));
  // Écarts au centième de point : les effets des accises sont de l'ordre de 0,01 point de PIB.
  const centieme = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    signDisplay: "exceptZero",
  });
  const ecart = (v: number) => centieme.format(Math.abs(v) < 0.005 ? 0 : v);
  const format = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2 });

  return (
    <>
      <fieldset className="reglages">
        <legend>{texte("simulateur.mesures")}</legend>
        {leviers.map((l) => {
          const levier = donnees.leviers[l.id];
          const id = `${idBase}-${l.id}`;
          return (
            <div key={l.id} className="reglage">
              <label htmlFor={id}>
                {texte(`simulateur.leviers.${l.id}.libelle`, {
                  reference: format.format(levier.taux_reference),
                  annee: donnees.annee_reference,
                })}
                {" : "}
                <strong>
                  {texte(`simulateur.leviers.${l.id}.valeur`, { valeur: signe(valeurs[l.id]) })}
                </strong>
                {levier.statut !== "valide" && (
                  <span className="etiquette">{texte(`validation.statuts.${levier.statut}`)}</span>
                )}
              </label>
              <input
                id={id}
                type="range"
                min={Math.ceil(levier.bornes[0] / l.pas) * l.pas}
                max={Math.floor(levier.bornes[1] / l.pas) * l.pas}
                step={l.pas}
                value={valeurs[l.id]}
                onChange={(e) => setValeurs({ ...valeurs, [l.id]: Number(e.target.value) })}
              />
            </div>
          );
        })}
        <label htmlFor={`${idBase}-annee`}>{texte("simulateur.annee_entree")}</label>
        <select
          id={`${idBase}-annee`}
          value={annee}
          onChange={(e) => setAnnee(Number(e.target.value))}
        >
          {annees.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </fieldset>
      <ReglagesDepensesFiscales
        catalogue={catalogue}
        leviers={donnees.leviers}
        parImpot={parImpot}
        setParImpot={setParImpot}
        parDepense={parDepense}
        setParDepense={setParDepense}
      />
      <ReglagesCreditsMissions
        catalogue={missions}
        leviers={donnees.leviers}
        reglages={parMission}
        setReglages={setParMission}
      />
      <GraphiqueDette
        points={lignes.map((l) => ({ annee: l.annee, ...l.dette }))}
        raccord={raccord}
        reference={{
          libelle: texte("simulateur.sans_mesure"),
          valeurs: donnees.base_dette[0],
        }}
        libelles={{
          titre: texte("simulateur.graphique_titre"),
          bas: texte("baseline.bas"),
          central: texte("baseline.central"),
          haut: texte("baseline.haut"),
          raccord: texte("baseline.graphique_raccord"),
          unite: texte("simulateur.graphique_lecture"),
        }}
      />
      <div className="defilement">
        <table>
          <thead>
            <tr>
              <th scope="col">{texte("baseline.annee")}</th>
              <th scope="col">{texte("simulateur.ecart_solde")}</th>
              <th scope="col">{texte("simulateur.ecart_dette")}</th>
              <th scope="col">{texte("simulateur.dette")}</th>
            </tr>
          </thead>
          <tbody>
            {lignes
              .filter((l) => ANNEES_AFFICHEES.includes(l.annee))
              .map((l) => (
                <tr key={l.annee}>
                  <th scope="row">{l.annee}</th>
                  <td className="nombre">
                    {texte("simulateur.fourchette", {
                      central: ecart(l.ecart_solde_primaire.central),
                      bas: ecart(l.ecart_solde_primaire.bas),
                      haut: ecart(l.ecart_solde_primaire.haut),
                    })}
                  </td>
                  <td className="nombre">
                    {texte("simulateur.fourchette", {
                      central: ecart(l.ecart_dette.central),
                      bas: ecart(l.ecart_dette.bas),
                      haut: ecart(l.ecart_dette.haut),
                    })}
                  </td>
                  <td className="nombre">
                    {texte("simulateur.fourchette", {
                      central: nombre(l.dette.central),
                      bas: nombre(l.dette.bas),
                      haut: nombre(l.dette.haut),
                    })}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
      <p className="source">{texte("simulateur.unite")}</p>
    </>
  );
}
