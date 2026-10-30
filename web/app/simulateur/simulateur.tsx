"use client";
// Simulateur : le calcul se fait dans le navigateur ; rien n'est envoyé ni enregistré.
import { useEffect, useId, useRef, useState } from "react";
import { texte, nombre } from "../../lib/textes";
import type {
  CatalogueCreditsMissions,
  CatalogueDepensesFiscales,
  DepenseMenages,
  Entreprises,
  ReponsesUnitaires,
  Version,
} from "../../lib/donnees";
import { calculer } from "../../lib/scenario";
import { mesuresDepensesFiscales } from "../../lib/depenses-fiscales";
import { ReglagesDepensesFiscales } from "./depenses-fiscales";
import { mesuresCreditsMissions } from "../../lib/credits-missions";
import { ReglagesCreditsMissions } from "./credits-missions";
import { GraphiqueDette } from "../baseline/graphique";
import {
  LEVIERS_PUBLICS,
  LEVIERS_REMUNERATIONS,
  LEVIERS_RETRAITES,
  LEVIERS_SOLIDARITE,
  MISSION_SOLIDARITE,
  decoder,
  empreinteVersion,
  encoder,
  problemes,
  type EtatScenario,
} from "../../lib/etat";
import { CopierLien, Exports } from "../partage/actions";
import { EffetsMenagesScenario } from "./menages";
import { EffetsEntreprisesScenario } from "./entreprises";
import { DepenseMenagesScenario } from "./depense";
import { region } from "../../lib/region";
import { useReponses } from "../../lib/chargement";
import Link from "next/link";


const ANNEES_AFFICHEES = [2027, 2030, 2035, 2040, 2046];

function SimulateurCharge({
  donnees,
  catalogue,
  missions,
  raccord,
  version,
  entreprises,
  depense,
}: {
  donnees: ReponsesUnitaires;
  catalogue: CatalogueDepensesFiscales;
  missions: CatalogueCreditsMissions;
  raccord: number;
  version: Version;
  entreprises: Entreprises;
  depense: DepenseMenages;
}) {
  // Un levier « non publié » reste hors du site (règle de publication, CLAUDE.md).
  const leviers = LEVIERS_PUBLICS.filter(
    (l) => l.id in donnees.leviers && donnees.leviers[l.id].statut !== "non_publie",
  );
  const annees = Object.keys(donnees.leviers[leviers[0].id].reponses).map(Number);
  const [valeurs, setValeurs] = useState<Record<string, number>>(
    Object.fromEntries(leviers.map((l) => [l.id, 0])),
  );
  const [parImpot, setParImpot] = useState<Record<string, number>>({});
  const [parDepense, setParDepense] = useState<Record<string, number>>({});
  const [parMission, setParMission] = useState<Record<string, number>>({});
  const [annee, setAnnee] = useState(annees[0]);
  const [croissance, setCroissance] = useState(false);
  const idBase = useId();
  // Lecture du lien partagé au chargement, puis l'adresse suit les réglages (sans historique).
  const [lu, setLu] = useState(false);
  const [alerte, setAlerte] = useState("");
  // Lien refusé ou d'une autre version : l'adresse reçue est gardée telle quelle (copiable,
  // signalable) tant que l'utilisateur n'a rien réglé.
  const garderAdresse = useRef(false);
  const empreinte = empreinteVersion(version);
  const etat: EtatScenario = {
    annee,
    leviers: valeurs,
    parImpot,
    parDepense,
    parMission,
    ...(croissance ? { croissance: true } : {}),
    version: empreinte,
  };
  useEffect(() => {
    const recherche = window.location.search;
    if (recherche) {
      const lien = decoder(recherche);
      if (!lien) {
        setAlerte(texte("partage.lien_illisible"));
        garderAdresse.current = true;
      } else if (problemes(lien, donnees, catalogue, missions).length > 0) {
        setAlerte(texte("partage.lien_invalide"));
        garderAdresse.current = true;
      } else {
        setValeurs((v) => ({ ...Object.fromEntries(Object.keys(v).map((k) => [k, 0])), ...lien.leviers }));
        setParImpot(lien.parImpot);
        setParDepense(lien.parDepense);
        setParMission(lien.parMission);
        setAnnee(lien.annee);
        setCroissance(lien.croissance === true);
        if (lien.version && lien.version !== empreinte) {
          setAlerte(texte("partage.autre_version"));
          garderAdresse.current = true;
        }
      }
    }
    setLu(true);
  }, [donnees, catalogue, missions, empreinte]);
  const adresse = encoder(etat);
  useEffect(() => {
    if (!lu) return;
    // Premier passage après la lecture du lien : rien n'a encore été réglé par l'utilisateur.
    if (garderAdresse.current) {
      garderAdresse.current = false;
      return;
    }
    window.history.replaceState(null, "", `?${adresse}`);
  }, [lu, adresse]);
  const remunerationsReglees = LEVIERS_REMUNERATIONS.some((id) => (valeurs[id] ?? 0) !== 0);
  const missionsReglees = Object.values(parMission).some((v) => v !== 0);
  // Dépenses fiscales et crédits des missions : sans effet calculé sur les ménages types et par
  // taille d'entreprise ; les blocs correspondants le disent au lieu de « aucune mesure ».
  const autresReglees =
    missionsReglees ||
    Object.values(parImpot).some((v) => v !== 0) ||
    Object.values(parDepense).some((v) => v !== 0);
  const indexationReglee = LEVIERS_SOLIDARITE.some((id) => (valeurs[id] ?? 0) !== 0);
  const solidariteReglee = (parMission[MISSION_SOLIDARITE] ?? 0) !== 0;
  const lignes = calculer(
    donnees,
    [
      ...leviers.map((l) => ({ levier: l.id, valeur: valeurs[l.id] })),
      ...mesuresDepensesFiscales(catalogue, parImpot, parDepense),
      ...mesuresCreditsMissions(missions, parMission),
    ],
    annee,
    croissance,
  );
  // Valeur d'un levier avec autant de décimales que son pas (0,25 an pour l'âge légal).
  const signe = (v: number, pas: number) =>
    new Intl.NumberFormat("fr-FR", {
      maximumFractionDigits: (String(pas).split(".")[1] ?? "").length,
      signDisplay: "exceptZero",
    }).format(v);
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
      {alerte && (
        <p className="avertissement" role="alert">
          {alerte}
        </p>
      )}
      <fieldset className="reglages">
        <legend>{texte("simulateur.mesures")}</legend>
        {leviers.map((l) => {
          const levier = donnees.leviers[l.id];
          const id = `${idBase}-${l.id}`;
          const bloqueRemunerations = missionsReglees && LEVIERS_REMUNERATIONS.includes(l.id);
          const bloqueIndexation = solidariteReglee && LEVIERS_SOLIDARITE.includes(l.id);
          // L'autre levier de départ à la retraite est déjà réglé.
          const bloqueRetraites =
            LEVIERS_RETRAITES.includes(l.id) &&
            LEVIERS_RETRAITES.some((id) => id !== l.id && (valeurs[id] ?? 0) !== 0);
          const bloque = bloqueRemunerations || bloqueIndexation || bloqueRetraites;
          return (
            <div key={l.id} className="reglage">
              <label htmlFor={id}>
                {texte(`simulateur.leviers.${l.id}.libelle`, {
                  reference: format.format(levier.taux_reference),
                  annee: donnees.annee_reference,
                })}
                {" : "}
                <strong>
                  {texte(`simulateur.leviers.${l.id}.valeur`, { valeur: signe(valeurs[l.id], l.pas) })}
                </strong>
                {levier.statut !== "valide" && (
                  <span className="etiquette">{texte(`validation.statuts.${levier.statut}`)}</span>
                )}
              </label>
              {/* Bornes arrondies vers l'intérieur au pas, pour que 0 reste sur la grille. */}
              <input
                id={id}
                type="range"
                min={Math.ceil(levier.bornes[0] / l.pas) * l.pas}
                max={Math.floor(levier.bornes[1] / l.pas) * l.pas}
                step={l.pas}
                value={valeurs[l.id]}
                disabled={bloque}
                onChange={(e) => setValeurs({ ...valeurs, [l.id]: Number(e.target.value) })}
              />
              <details className="explication">
                <summary>{texte("simulateur.en_savoir_plus")}</summary>
                <p>{texte(`simulateur.leviers.${l.id}.explication`)}</p>
              </details>
              {bloqueRemunerations && (
                <span className="source">{texte("simulateur.bloque_remunerations")}</span>
              )}
              {bloqueIndexation && (
                <span className="source">{texte("simulateur.bloque_indexation")}</span>
              )}
              {bloqueRetraites && (
                <span className="source">{texte("simulateur.bloque_retraites")}</span>
              )}
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
        <div className="interrupteur">
          <input
            id={`${idBase}-croissance`}
            type="checkbox"
            checked={croissance}
            onChange={(e) => setCroissance(e.target.checked)}
          />
          <label htmlFor={`${idBase}-croissance`}>{texte("simulateur.croissance")}</label>
          <span className="etiquette">{texte("validation.statuts.beta")}</span>
        </div>
        <span className="source">{texte("simulateur.croissance_aide")}</span>
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
        bloque={remunerationsReglees}
        missionsBloquees={indexationReglee ? [MISSION_SOLIDARITE] : []}
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
      <div className="defilement" {...region(texte("simulateur.titre"))}>
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
      <div className="actions">
        <CopierLien />
        <Exports
          scenarios={[{ nom: texte("partage.scenario"), etat, lignes }]}
          version={version}
          nomFichier="scenario"
        />
        <Link href="/comparaison/">{texte("partage.lien_comparaison")}</Link>
      </div>
      <p className="source">{texte("partage.explication")}</p>
      <EffetsMenagesScenario valeurs={valeurs} empreinte={empreinte} autresReglees={autresReglees} />
      <DepenseMenagesScenario donnees={depense} valeurs={valeurs} />
      <EffetsEntreprisesScenario donnees={entreprises} valeurs={valeurs} autresReglees={autresReglees} />
    </>
  );
}

// Les réponses unitaires (plusieurs mégaoctets) sont chargées par le navigateur, pas
// incluses dans la page (lib/chargement.ts).
export function Simulateur(props: {
  catalogue: CatalogueDepensesFiscales;
  missions: CatalogueCreditsMissions;
  raccord: number;
  version: Version;
  entreprises: Entreprises;
  depense: DepenseMenages;
}) {
  const chargement = useReponses(empreinteVersion(props.version));
  if (chargement.etat === "en_cours") return <p role="status">{texte("site.chargement")}</p>;
  if (chargement.etat === "erreur")
    return (
      <p className="avertissement" role="alert">
        {texte("site.chargement_erreur")}
      </p>
    );
  return <SimulateurCharge donnees={chargement.donnees} {...props} />;
}
