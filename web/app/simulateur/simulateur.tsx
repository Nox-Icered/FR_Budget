"use client";
// Simulateur : le calcul se fait dans le navigateur ; rien n'est envoyé ni enregistré.
import { useId, useState } from "react";
import { texte, nombre } from "../../lib/textes";
import type { ReponsesUnitaires } from "../../lib/donnees";
import { calculer } from "../../lib/scenario";
import { GraphiqueDette } from "../baseline/graphique";

const LEVIER = "tva_taux_normal";
const PAS = 0.5;
const ANNEES_AFFICHEES = [2027, 2030, 2035, 2040, 2046];

export function Simulateur({
  donnees,
  raccord,
}: {
  donnees: ReponsesUnitaires;
  raccord: number;
}) {
  const levier = donnees.leviers[LEVIER];
  const annees = Object.keys(levier.reponses).map(Number);
  const [valeur, setValeur] = useState(1);
  const [annee, setAnnee] = useState(annees[0]);
  const idValeur = useId();
  const idAnnee = useId();
  const lignes = calculer(donnees, LEVIER, valeur, annee);
  const signe = (v: number) => (v > 0 ? `+${nombre(v)}` : nombre(v));

  return (
    <>
      <fieldset className="reglages">
        <legend>
          {texte("simulateur.levier_tva", {
            taux: new Intl.NumberFormat("fr-FR").format(levier.taux_reference),
            annee: donnees.annee_reference,
          })}
        </legend>
        <label htmlFor={idValeur}>
          {texte("simulateur.points", { valeur: signe(valeur) })}
        </label>
        <input
          id={idValeur}
          type="range"
          min={levier.bornes[0]}
          max={levier.bornes[1]}
          step={PAS}
          value={valeur}
          onChange={(e) => setValeur(Number(e.target.value))}
        />
        <label htmlFor={idAnnee}>{texte("simulateur.annee_entree")}</label>
        <select id={idAnnee} value={annee} onChange={(e) => setAnnee(Number(e.target.value))}>
          {annees.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </fieldset>
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
                      central: signe(l.ecart_solde_primaire.central),
                      bas: signe(l.ecart_solde_primaire.bas),
                      haut: signe(l.ecart_solde_primaire.haut),
                    })}
                  </td>
                  <td className="nombre">
                    {texte("simulateur.fourchette", {
                      central: signe(l.ecart_dette.central),
                      bas: signe(l.ecart_dette.bas),
                      haut: signe(l.ecart_dette.haut),
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
