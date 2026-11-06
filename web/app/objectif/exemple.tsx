"use client";
// Exemple de scénario construit par la règle écrite sur la page (lib/exemple.ts) à partir des
// mesures cochées par l'utilisateur et de la part de l'effort qu'il donne aux recettes. Aucune
// mesure n'est cochée par défaut ; l'exemple n'est ni classé ni qualifié.
import { useId, useState } from "react";
import Link from "next/link";
import { texte } from "../../lib/textes";
import type { ReponsesUnitaires, Version } from "../../lib/donnees";
import { empreinteVersion, encoder, LEVIERS_PUBLICS, LEVIERS_RETRAITES } from "../../lib/etat";
import {
  construireExemple,
  COTES,
  PART_RECETTES_DEFAUT,
  PAS_PART_RECETTES,
  type Cote,
} from "../../lib/exemple";
import type { Objectif } from "../../lib/objectif";

const chiffre = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2 });
const signe = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2, signDisplay: "exceptZero" });
const POURCENT = 100;

export function ExempleScenario({
  donnees,
  version,
  objectif,
  entree,
  valide,
  libelle,
}: {
  donnees: ReponsesUnitaires;
  version: Version;
  objectif: Objectif;
  entree: number;
  valide: boolean;
  libelle: (id: string) => string;
}) {
  const idBase = useId();
  const [coches, setCoches] = useState<string[]>([]);
  const [partRecettes, setPartRecettes] = useState(PART_RECETTES_DEFAUT);
  const leviers = LEVIERS_PUBLICS.filter(
    (l) => l.id in donnees.leviers && donnees.leviers[l.id].statut !== "non_publie",
  );
  const pas = Object.fromEntries(leviers.map((l) => [l.id, l.pas]));
  const unite = (id: string, v: number) => texte(`simulateur.leviers.${id}.valeur`, { valeur: signe.format(v) });
  const basculer = (id: string, coche: boolean) =>
    setCoches((c) => (coche ? [...c, id] : c.filter((x) => x !== id)));
  // Âge effectif et âge légal de départ ne se cumulent pas (comme dans le simulateur).
  const exclu = (id: string) =>
    LEVIERS_RETRAITES.includes(id) && LEVIERS_RETRAITES.some((l) => l !== id && coches.includes(l));
  const exemple =
    valide && coches.length > 0
      ? construireExemple(donnees, { leviers: coches, partRecettes, entree, objectif, pas })
      : null;
  const lien =
    exemple?.atteint &&
    encoder({
      annee: entree,
      leviers: Object.fromEntries(exemple.mesures.map((m) => [m.levier, m.valeur])),
      parImpot: {},
      parDepense: {},
      parMission: {},
      version: empreinteVersion(version),
    });
  const pourcent = Math.round(partRecettes * POURCENT);

  return (
    <section className="exemple-objectif" aria-labelledby={`${idBase}-titre`}>
      <h2 id={`${idBase}-titre`}>{texte("objectif.exemple.titre")}</h2>
      <p>{texte("objectif.exemple.intro")}</p>
      <p className="avertissement" role="note">
        {texte("objectif.exemple.mention")}
      </p>
      {(["recettes", "depenses"] as Cote[]).map((cote) => (
        <fieldset key={cote} className="mesures-exemple">
          <legend>{texte(`objectif.exemple.${cote}`)}</legend>
          {leviers
            .filter((l) => COTES[l.id] === cote)
            .map((l) => (
              <label key={l.id}>
                <input
                  type="checkbox"
                  checked={coches.includes(l.id)}
                  disabled={exclu(l.id)}
                  onChange={(e) => basculer(l.id, e.target.checked)}
                />{" "}
                {libelle(l.id)}
              </label>
            ))}
        </fieldset>
      ))}
      <label htmlFor={`${idBase}-part`}>
        {texte("objectif.exemple.part", { recettes: pourcent, depenses: POURCENT - pourcent })}
      </label>
      <input
        id={`${idBase}-part`}
        type="range"
        min={0}
        max={1}
        step={PAS_PART_RECETTES}
        value={partRecettes}
        onChange={(e) => setPartRecettes(Number(e.target.value))}
      />
      <p className="source">{texte("objectif.exemple.part_defaut")}</p>
      <div aria-live="polite" className="resultat-objectif">
        {!valide ? (
          <p>{texte("objectif.saisir")}</p>
        ) : exemple === null ? (
          <p>{texte("objectif.exemple.cocher")}</p>
        ) : exemple.problemes.length > 0 ? (
          exemple.problemes.map((p) => <p key={p}>{texte(`objectif.exemple.problemes.${p}`)}</p>)
        ) : (
          <>
            <div className="defilement">
              <table>
                <caption>{texte("objectif.exemple.tableau")}</caption>
                <thead>
                  <tr>
                    <th scope="col">{texte("objectif.exemple.mesure")}</th>
                    <th scope="col">{texte("objectif.exemple.part_attribuee")}</th>
                    <th scope="col">{texte("objectif.exemple.reglage")}</th>
                    <th scope="col">{texte("objectif.exemple.contribution")}</th>
                  </tr>
                </thead>
                <tbody>
                  {exemple.mesures.map((m) => (
                    <tr key={m.levier}>
                      <th scope="row">{libelle(m.levier)}</th>
                      <td>{signe.format(m.part)}</td>
                      <td>
                        {unite(m.levier, m.valeur)}
                        {m.aLaLimite && ` ${texte("objectif.exemple.a_la_limite")}`}
                      </td>
                      <td>{signe.format(m.contribution)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {exemple.atteint && (
              <p>
                {texte("objectif.exemple.resultat", {
                  annee: objectif.annee,
                  central: chiffre.format(exemple.atteint.central),
                  bas: chiffre.format(exemple.atteint.bas),
                  haut: chiffre.format(exemple.atteint.haut),
                })}
              </p>
            )}
            {lien && (
              <p>
                <Link href={`/simulateur/?${lien}`}>{texte("objectif.exemple.ouvrir")}</Link>
              </p>
            )}
          </>
        )}
      </div>
      <details className="explication">
        <summary>{texte("objectif.exemple.regle_titre")}</summary>
        <p>{texte("objectif.exemple.regle")}</p>
        <p>{texte("objectif.exemple.cotes")}</p>
        <p>{texte("objectif.exemple.limites")}</p>
      </details>
    </section>
  );
}
