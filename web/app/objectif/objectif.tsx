"use client";
// Mode « atteindre un objectif » : l'utilisateur choisit l'indicateur, l'année, la cible et le
// levier ; la page donne la valeur du levier qui atteint la cible (lib/objectif.ts). Aucun levier
// n'est proposé ni classé.
import { useId, useState } from "react";
import Link from "next/link";
import { texte } from "../../lib/textes";
import type { ReponsesUnitaires, Version } from "../../lib/donnees";
import { useReponses } from "../../lib/chargement";
import { empreinteVersion, encoder, LEVIERS_PUBLICS } from "../../lib/etat";
import { fourchetteValeur, reglageAuPas, resoudre, type Indicateur } from "../../lib/objectif";

const chiffre = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2 });
const signe = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2, signDisplay: "exceptZero" });

function ObjectifCharge({ donnees, version }: { donnees: ReponsesUnitaires; version: Version }) {
  const idBase = useId();
  const leviers = LEVIERS_PUBLICS.filter(
    (l) => l.id in donnees.leviers && donnees.leviers[l.id].statut !== "non_publie",
  );
  const entrees = Object.keys(donnees.leviers[leviers[0].id].reponses).map(Number);
  const [indicateur, setIndicateur] = useState<Indicateur>("dette");
  const [entree, setEntree] = useState(entrees[0]);
  const [annee, setAnnee] = useState(2040);
  const [cible, setCible] = useState<number>(NaN);
  const [levier, setLevier] = useState(leviers[0].id);
  const annees = donnees.annees.filter((a) => a >= entree);
  const libelle = (id: string) =>
    texte(`simulateur.leviers.${id}.libelle`, {
      reference: chiffre.format(donnees.leviers[id].taux_reference),
      annee: donnees.annee_reference,
    });
  const objectif = { indicateur, annee, cible };
  const valide = Number.isFinite(cible) && annees.includes(annee);
  const solution = valide ? resoudre(donnees, levier, entree, objectif) : null;
  const fourchette = solution ? fourchetteValeur(solution) : null;
  const pas = leviers.find((l) => l.id === levier)?.pas ?? 1;
  const unite = (v: number) => texte(`simulateur.leviers.${levier}.valeur`, { valeur: signe.format(v) });
  const reglage = fourchette
    ? reglageAuPas(donnees, levier, pas, entree, objectif, fourchette.central)
    : null;
  const lien =
    reglage !== null &&
    encoder({
      annee: entree,
      leviers: { [levier]: reglage },
      parImpot: {},
      parDepense: {},
      parMission: {},
      version: empreinteVersion(version),
    });
  const sansMesure = (() => {
    try {
      return resoudre(donnees, levier, entree, { ...objectif, cible: 0 }).sansMesure;
    } catch {
      return null;
    }
  })();

  return (
    <section className="objectif">
      <div className="formulaire-objectif">
        <label htmlFor={`${idBase}-ind`}>{texte("objectif.indicateur")}</label>
        <select id={`${idBase}-ind`} value={indicateur} onChange={(e) => setIndicateur(e.target.value as Indicateur)}>
          <option value="dette">{texte("objectif.dette")}</option>
          <option value="solde_primaire">{texte("objectif.solde_primaire")}</option>
        </select>
        <label htmlFor={`${idBase}-annee`}>{texte("objectif.annee")}</label>
        <select id={`${idBase}-annee`} value={annee} onChange={(e) => setAnnee(Number(e.target.value))}>
          {annees.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
        <label htmlFor={`${idBase}-cible`}>{texte("objectif.cible")}</label>
        <input
          id={`${idBase}-cible`}
          type="number"
          step={0.1}
          value={Number.isFinite(cible) ? cible : ""}
          onChange={(e) => setCible(e.target.value === "" ? NaN : Number(e.target.value))}
        />
        {sansMesure !== null && (
          <p className="source">
            {texte("objectif.sans_mesure", { annee, valeur: chiffre.format(sansMesure) })}
          </p>
        )}
        <label htmlFor={`${idBase}-levier`}>{texte("objectif.levier")}</label>
        <select id={`${idBase}-levier`} value={levier} onChange={(e) => setLevier(e.target.value)}>
          {leviers.map((l) => (
            <option key={l.id} value={l.id}>
              {libelle(l.id)}
            </option>
          ))}
        </select>
        <label htmlFor={`${idBase}-entree`}>{texte("objectif.entree")}</label>
        <select
          id={`${idBase}-entree`}
          value={entree}
          onChange={(e) => {
            const nouvelle = Number(e.target.value);
            setEntree(nouvelle);
            // L'année de l'objectif ne peut pas précéder l'entrée en vigueur.
            if (annee < nouvelle) setAnnee(nouvelle);
          }}
        >
          {entrees.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </div>
      <div aria-live="polite" className="resultat-objectif">
        {!valide ? (
          <p>{texte("objectif.saisir")}</p>
        ) : fourchette === null ? (
          <p>{texte("objectif.hors_portee")}</p>
        ) : (
          <>
            <p>
              {texte("objectif.resultat", {
                levier: libelle(levier),
                valeur: unite(fourchette.central),
              })}
            </p>
            <p className="source">
              {texte("objectif.fourchette", { bas: unite(fourchette.bas), haut: unite(fourchette.haut) })}
              {(solution?.parBorne.bas === null || solution?.parBorne.haut === null) &&
                ` ${texte("objectif.fourchette_partielle")}`}
            </p>
            <p>
              {lien && reglage !== null ? (
                <Link href={`/simulateur/?${lien}`}>
                  {texte("objectif.ouvrir", { valeur: unite(reglage) })}
                </Link>
              ) : (
                texte("objectif.pas_de_reglage")
              )}
            </p>
          </>
        )}
      </div>
    </section>
  );
}

export function Objectif({ version }: { version: Version }) {
  const chargement = useReponses(empreinteVersion(version));
  if (chargement.etat === "en_cours") return <p role="status">{texte("site.chargement")}</p>;
  if (chargement.etat === "erreur")
    return (
      <p className="avertissement" role="alert">
        {texte("site.chargement_erreur")}
      </p>
    );
  return <ObjectifCharge donnees={chargement.donnees} version={version} />;
}
