"use client";
// Simulateur : le calcul se fait dans le navigateur ; rien n'est envoyé ni enregistré.
import { useEffect, useId, useRef, useState, type SyntheticEvent } from "react";
import { texte, nombre } from "../../lib/textes";
import type {
  Baseline,
  CatalogueCreditsMissions,
  CatalogueDepensesFiscales,
  DepenseMenages,
  Entreprises,
  ReponsesUnitaires,
  Version,
} from "../../lib/donnees";
import { avecInteractions, calculer, interactionsNonChiffrees } from "../../lib/scenario";
import { mesuresDepensesFiscales } from "../../lib/depenses-fiscales";
import { ReglagesDepensesFiscales } from "./depenses-fiscales";
import { mesuresCreditsMissions } from "../../lib/credits-missions";
import { ReglagesCreditsMissions } from "./credits-missions";
import { GraphiqueDette } from "../baseline/graphique";
import {
  LEVIERS_PUBLICS,
  LEVIERS_REMUNERATIONS,
  LEVIERS_RETRAITES,
  LEVIER_IR_SEUILS,
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
import { correspond, reglees, SECTIONS } from "../../lib/sections";
import { egal, mesureBareme, type Bareme, type DonneesBareme } from "../../lib/bareme-ir";
import { EditeurBareme } from "./bareme-ir";
import { useReponses } from "../../lib/chargement";
import Link from "next/link";


const ANNEES_AFFICHEES = [2027, 2030, 2035, 2040, 2046];

function SimulateurCharge({
  donnees,
  catalogue,
  missions,
  raccord,
  commission,
  version,
  entreprises,
  depense,
  bareme: donneesBareme,
}: {
  donnees: ReponsesUnitaires;
  bareme: DonneesBareme;
  commission: Baseline["commission"];
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
  const [bareme, setBareme] = useState<Bareme>(donneesBareme.bareme_reference);
  const baremeModifie = !egal(bareme, donneesBareme.bareme_reference);
  const [annee, setAnnee] = useState(annees[0]);
  const [croissance, setCroissance] = useState(false);
  const [recherche, setRecherche] = useState("");
  const [ouvertes, setOuvertes] = useState<Record<string, boolean>>({});
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
    ...(baremeModifie ? { bareme } : {}),
    version: empreinte,
  };
  useEffect(() => {
    const recherche = window.location.search;
    if (recherche) {
      const lien = decoder(recherche);
      if (!lien) {
        setAlerte(texte("partage.lien_illisible"));
        garderAdresse.current = true;
      } else if (problemes(lien, donnees, catalogue, missions, donneesBareme).length > 0) {
        setAlerte(texte("partage.lien_invalide"));
        garderAdresse.current = true;
      } else {
        setValeurs((v) => ({ ...Object.fromEntries(Object.keys(v).map((k) => [k, 0])), ...lien.leviers }));
        setParImpot(lien.parImpot);
        setParDepense(lien.parDepense);
        setParMission(lien.parMission);
        if (lien.bareme) setBareme(lien.bareme);
        setAnnee(lien.annee);
        setCroissance(lien.croissance === true);
        if (lien.version && lien.version !== empreinte) {
          setAlerte(texte("partage.autre_version"));
          garderAdresse.current = true;
        }
      }
    }
    setLu(true);
  }, [donnees, catalogue, missions, empreinte, donneesBareme]);
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
  const mesuresSite = [
    ...leviers.map((l) => ({ levier: l.id, valeur: valeurs[l.id] })),
    ...mesuresDepensesFiscales(catalogue, parImpot, parDepense),
    ...mesuresCreditsMissions(missions, parMission),
    ...mesureBareme(donneesBareme, bareme),
  ];
  const lignes = calculer(donnees, mesuresSite, annee, croissance);
  // Termes croisés ajoutés au calcul, et interactions connues mais non chiffrées.
  const croises = avecInteractions(donnees, mesuresSite)
    .slice(mesuresSite.length)
    .map((m) => m.levier);
  const nonChiffrees = interactionsNonChiffrees(donnees, mesuresSite);
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

  const leviersParId = new Map(leviers.map((l) => [l.id, l]));
  const libelle = (id: string) =>
    texte(`simulateur.leviers.${id}.libelle`, {
      reference: format.format(donnees.leviers[id].taux_reference),
      annee: donnees.annee_reference,
    });
  const sections = SECTIONS.map((section) => ({
    ...section,
    leviers: section.leviers
      .map((id) => leviersParId.get(id))
      .filter((l): l is (typeof leviers)[number] => l !== undefined)
      .filter((l) => correspond(libelle(l.id), recherche)),
  })).filter((section) => section.leviers.length > 0);
  const nombreReglees =
    reglees(Object.keys(valeurs), valeurs) +
    Object.values(parImpot).filter((v) => v !== 0).length +
    Object.values(parDepense).filter((v) => v !== 0).length +
    Object.values(parMission).filter((v) => v !== 0).length +
    (baremeModifie ? 1 : 0);
  const reglagesDepenses =
    Object.values(parImpot).filter((v) => v !== 0).length +
    Object.values(parDepense).filter((v) => v !== 0).length;
  const reglagesMissions = Object.values(parMission).filter((v) => v !== 0).length;
  const remettreAZero = () => {
    setValeurs(Object.fromEntries(Object.keys(valeurs).map((k) => [k, 0])));
    setParImpot({});
    setParDepense({});
    setParMission({});
    setBareme(donneesBareme.bareme_reference);
  };
  // Section ouverte : choix de l'utilisateur, sinon ouverte si une mesure y est réglée (la
  // première l'est par défaut) ; toutes ouvertes pendant une recherche.
  const ouverte = (id: string, rang: number, nReglees: number) =>
    recherche.trim() !== "" || (ouvertes[id] ?? (nReglees > 0 || rang === 0));
  const basculer = (id: string) => (e: SyntheticEvent<HTMLDetailsElement>) => {
    const ouvert = e.currentTarget.open;
    if (recherche.trim() === "") setOuvertes((o) => ({ ...o, [id]: ouvert }));
  };
  const derniere = lignes[lignes.length - 1];
  const sansMesure = donnees.base_dette[0][donnees.base_dette[0].length - 1];

  const reglage = (l: (typeof leviers)[number]) => {
    const levier = donnees.leviers[l.id];
    const id = `${idBase}-${l.id}`;
    const bloqueRemunerations = missionsReglees && LEVIERS_REMUNERATIONS.includes(l.id);
    const bloqueIndexation = solidariteReglee && LEVIERS_SOLIDARITE.includes(l.id);
    // L'autre levier de départ à la retraite est déjà réglé.
    const bloqueRetraites =
      LEVIERS_RETRAITES.includes(l.id) &&
      LEVIERS_RETRAITES.some((id) => id !== l.id && (valeurs[id] ?? 0) !== 0);
    const bloqueBareme = l.id === LEVIER_IR_SEUILS && baremeModifie;
    const bloque = bloqueRemunerations || bloqueIndexation || bloqueRetraites || bloqueBareme;
    return (
      <div key={l.id} className="reglage">
        <div className="reglage-tete">
          <label htmlFor={id}>{libelle(l.id)}</label>
          <strong className={valeurs[l.id] !== 0 ? "valeur valeur-reglee" : "valeur"}>
            {texte(`simulateur.leviers.${l.id}.valeur`, { valeur: signe(valeurs[l.id], l.pas) })}
          </strong>
        </div>
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
        {bloqueIndexation && <span className="source">{texte("simulateur.bloque_indexation")}</span>}
        {bloqueRetraites && <span className="source">{texte("simulateur.bloque_retraites")}</span>}
        {bloqueBareme && <span className="source">{texte("simulateur.bloque_bareme")}</span>}
      </div>
    );
  };

  const titreSection = (id: string, nReglees: number, total?: number) => (
    <summary>
      <span className="section-titre">{texte(`simulateur.sections.${id}.titre`)}</span>
      <span className="section-description">
        {texte(`simulateur.sections.${id}.description`)}
        {total !== undefined && ` · ${texte("simulateur.nombre_mesures", { nombre: total })}`}
      </span>
      {nReglees > 0 && (
        <span className="pastille">{texte("simulateur.reglees", { nombre: nReglees })}</span>
      )}
    </summary>
  );

  return (
    <>
      {alerte && (
        <p className="avertissement" role="alert">
          {alerte}
        </p>
      )}
      <div className="simulateur">
        <div className="simulateur-reglages">
          <div className="barre-outils">
            <label className="recherche">
              <span className="visuellement-cache">{texte("simulateur.recherche_libelle")}</span>
              <input
                type="search"
                placeholder={texte("simulateur.recherche")}
                value={recherche}
                onChange={(e) => setRecherche(e.target.value)}
              />
            </label>
            <span className="source">
              {texte("simulateur.mesures_reglees", { nombre: nombreReglees })}
            </span>
            <button
              type="button"
              onClick={remettreAZero}
              disabled={nombreReglees === 0 && Object.keys(parDepense).length === 0}
            >
              {texte("simulateur.remise_a_zero")}
            </button>
          </div>
          {sections.length === 0 && <p>{texte("simulateur.recherche_vide")}</p>}
          {sections.map((section, rang) => {
            const nReglees = reglees(
              section.leviers.map((l) => l.id),
              valeurs,
            );
            return (
              <details
                key={section.id}
                className="section"
                open={ouverte(section.id, rang, nReglees)}
                onToggle={basculer(section.id)}
              >
                {titreSection(section.id, nReglees, section.leviers.length)}
                <div className="section-contenu">{section.leviers.map(reglage)}</div>
              </details>
            );
          })}
          {recherche.trim() === "" && (
            <>
              <details
                className="section"
                open={ouvertes.depenses_fiscales ?? reglagesDepenses > 0}
                onToggle={basculer("depenses_fiscales")}
              >
                {titreSection("depenses_fiscales", reglagesDepenses)}
                <div className="section-contenu">
                  <ReglagesDepensesFiscales
                    catalogue={catalogue}
                    leviers={donnees.leviers}
                    parImpot={parImpot}
                    setParImpot={setParImpot}
                    parDepense={parDepense}
                    setParDepense={setParDepense}
                  />
                </div>
              </details>
              <details
                className="section"
                open={ouvertes.bareme_ir ?? baremeModifie}
                onToggle={basculer("bareme_ir")}
              >
                {titreSection("bareme_ir", baremeModifie ? 1 : 0)}
                <div className="section-contenu">
                  <EditeurBareme
                    donnees={donneesBareme}
                    bareme={bareme}
                    setBareme={setBareme}
                    bloque={(valeurs[LEVIER_IR_SEUILS] ?? 0) !== 0}
                    statut={donnees.leviers[donneesBareme.levier]?.statut}
                  />
                </div>
              </details>
              <details
                className="section"
                open={ouvertes.credits_missions ?? reglagesMissions > 0}
                onToggle={basculer("credits_missions")}
              >
                {titreSection("credits_missions", reglagesMissions)}
                <div className="section-contenu">
                  <ReglagesCreditsMissions
                    catalogue={missions}
                    leviers={donnees.leviers}
                    reglages={parMission}
                    bloque={remunerationsReglees}
                    missionsBloquees={indexationReglee ? [MISSION_SOLIDARITE] : []}
                    setReglages={setParMission}
                  />
                </div>
              </details>
            </>
          )}
        </div>

        <aside id="resultat" className="simulateur-resultat" aria-labelledby={`${idBase}-resultat`}>
          <div className="resultat-tete">
            <h2 id={`${idBase}-resultat`}>{texte("simulateur.resultat")}</h2>
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
          </div>
          {(croises.length > 0 || nonChiffrees.length > 0) && (
            <div className="interactions" role="note">
              {croises.map((id) => (
                <p key={id} className="source">
                  {texte(`simulateur.interactions.chiffrees.${id}`)}
                </p>
              ))}
              {nonChiffrees.map((m) => (
                <p key={m} className="avertissement">
                  {texte("simulateur.interactions.non_chiffree", {
                    mecanisme: texte(`simulateur.interactions.mecanismes.${m}`),
                  })}
                </p>
              ))}
            </div>
          )}
          <dl className="chiffres-cles">
            <div>
              <dt>{texte("simulateur.resume_solde", { annee: derniere.annee })}</dt>
              <dd>{ecart(derniere.ecart_solde_primaire.central)}</dd>
              <dd className="secondaire">
                {texte("simulateur.resume_solde_detail", {
                  bas: ecart(derniere.ecart_solde_primaire.bas),
                  haut: ecart(derniere.ecart_solde_primaire.haut),
                })}
              </dd>
            </div>
            <div>
              <dt>{texte("simulateur.resume_dette", { annee: derniere.annee })}</dt>
              <dd>{nombre(derniere.dette.central)}</dd>
              <dd className="secondaire">
                {texte("simulateur.resume_dette_detail", {
                  bas: nombre(derniere.dette.bas),
                  haut: nombre(derniere.dette.haut),
                  sans: nombre(sansMesure),
                })}
              </dd>
            </div>
          </dl>
          <GraphiqueDette
            points={lignes.map((l) => ({ annee: l.annee, ...l.dette }))}
            raccord={raccord}
            reference={{
              libelle: texte("simulateur.sans_mesure"),
              valeurs: donnees.base_dette[0],
            }}
            legende={texte("simulateur.legende_avec")}
            comparaison={{
              libelle: texte("baseline.commission"),
              prolongement: texte("baseline.commission_prolongement", {
                annee: commission.derniere_annee_publiee,
              }),
              points: commission.valeurs.map((v) => ({
                annee: v.annee,
                publiee: v.publiee,
                ...v.dette,
              })),
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
          <div className="actions">
            <CopierLien />
            <Exports
              scenarios={[{ nom: texte("partage.scenario"), etat, lignes }]}
              version={version}
              nomFichier="scenario"
            />
            <Link href="/comparaison/">{texte("partage.lien_comparaison")}</Link>
          </div>
          <a href="#detail">{texte("simulateur.lien_detail")}</a>
        </aside>
      </div>

      <div className="resume-mobile" aria-hidden="true">
        <div>
          <span>{texte("simulateur.resume_solde", { annee: derniere.annee })}</span>
          <strong>
            {texte("simulateur.resume_mobile_solde", {
              central: ecart(derniere.ecart_solde_primaire.central),
              bas: ecart(derniere.ecart_solde_primaire.bas),
              haut: ecart(derniere.ecart_solde_primaire.haut),
            })}
          </strong>
        </div>
        <div>
          <span>{texte("simulateur.resume_dette", { annee: derniere.annee })}</span>
          <strong>
            {texte("simulateur.resume_mobile_dette", {
              central: nombre(derniere.dette.central),
              bas: nombre(derniere.dette.bas),
              haut: nombre(derniere.dette.haut),
            })}
          </strong>
        </div>
        <a href="#resultat" tabIndex={-1}>
          {texte("simulateur.voir_resultat")}
        </a>
      </div>

      <h2 id="detail">{texte("simulateur.detail_titre")}</h2>
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
      <p className="source">{texte("partage.explication")}</p>
      <EffetsMenagesScenario
        valeurs={valeurs}
        empreinte={empreinte}
        autresReglees={autresReglees}
        bareme={
          mesureBareme(donneesBareme, bareme).length > 0
            ? { donnees: donneesBareme, bareme }
            : undefined
        }
      />
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
  commission: Baseline["commission"];
  version: Version;
  entreprises: Entreprises;
  depense: DepenseMenages;
  bareme: DonneesBareme;
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
