"use client";
// Éditeur du barème de l'impôt sur le revenu : tranches (seuil et taux), décote. L'effet est
// calculé dans le navigateur (lib/bareme-ir.ts) et devient une mesure sur le levier générique
// « ir_bareme ». Barème de départ : celui des revenus de l'année de référence (OpenFisca).
import { useId } from "react";
import { texte } from "../../lib/textes";
import {
  effetBareme,
  egal,
  problemesBareme,
  signale,
  TAUX_SIGNALE,
  TRANCHES_MAX,
  type Bareme,
  type DonneesBareme,
} from "../../lib/bareme-ir";

const euros = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const milliards = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1, signDisplay: "exceptZero" });
const POURCENT = 100;
const ECART_NOUVELLE_TRANCHE = 10_000;

export function EditeurBareme({
  donnees,
  bareme,
  setBareme,
  bloque,
  statut,
}: {
  donnees: DonneesBareme;
  bareme: Bareme;
  setBareme: (b: Bareme) => void;
  bloque: boolean;
  statut?: string;
}) {
  const idBase = useId();
  const reference = donnees.bareme_reference;
  const problemes = problemesBareme(bareme);
  const modifie = !egal(bareme, reference);
  const effet = problemes.length === 0 && modifie ? effetBareme(donnees, bareme) : null;
  const n = bareme.seuils.length;

  const changerSeuil = (i: number, v: number) =>
    setBareme({ ...bareme, seuils: bareme.seuils.map((s, k) => (k === i ? v : s)) });
  const changerTaux = (i: number, v: number) =>
    setBareme({ ...bareme, taux: bareme.taux.map((t, k) => (k === i ? v / POURCENT : t)) });
  const ajouter = () =>
    setBareme({
      ...bareme,
      seuils: [...bareme.seuils, bareme.seuils[n - 1] + ECART_NOUVELLE_TRANCHE],
      taux: [...bareme.taux, bareme.taux[n - 1]],
    });
  const retirer = () =>
    setBareme({ ...bareme, seuils: bareme.seuils.slice(0, -1), taux: bareme.taux.slice(0, -1) });
  const changerDecote = (cle: "seuil_celibataire" | "seuil_couple" | "taux", v: number) =>
    bareme.decote && setBareme({ ...bareme, decote: { ...bareme.decote, [cle]: v } });

  return (
    <fieldset className="reglages bareme-ir" disabled={bloque}>
      <legend>
        {texte("simulateur.bareme_ir.titre", { annee: donnees.annee_bareme })}
        {statut && statut !== "valide" && (
          <span className="etiquette">{texte(`validation.statuts.${statut}`)}</span>
        )}
      </legend>
      <details className="explication">
        <summary>{texte("simulateur.bareme_ir.qu_est_ce")}</summary>
        <p>{texte("simulateur.bareme_ir.explication")}</p>
      </details>
      {bloque && <p className="source">{texte("simulateur.bareme_ir.bloque")}</p>}
      <div className="defilement">
        <table>
          <caption className="visuellement-cache">{texte("simulateur.bareme_ir.tableau")}</caption>
          <thead>
            <tr>
              <th scope="col">{texte("simulateur.bareme_ir.tranche")}</th>
              <th scope="col">{texte("simulateur.bareme_ir.seuil")}</th>
              <th scope="col">{texte("simulateur.bareme_ir.taux")}</th>
            </tr>
          </thead>
          <tbody>
            {bareme.seuils.map((s, i) => (
              <tr key={i}>
                <th scope="row">{i + 1}</th>
                <td>
                  <label className="visuellement-cache" htmlFor={`${idBase}-s${i}`}>
                    {texte("simulateur.bareme_ir.seuil_tranche", { numero: i + 1 })}
                  </label>
                  <input
                    id={`${idBase}-s${i}`}
                    type="number"
                    min={0}
                    step={100}
                    value={Number.isFinite(s) ? s : ""}
                    disabled={i === 0}
                    onChange={(e) => changerSeuil(i, e.target.value === "" ? NaN : Number(e.target.value))}
                  />
                </td>
                <td>
                  <label className="visuellement-cache" htmlFor={`${idBase}-t${i}`}>
                    {texte("simulateur.bareme_ir.taux_tranche", { numero: i + 1 })}
                  </label>
                  <input
                    id={`${idBase}-t${i}`}
                    type="number"
                    min={0}
                    max={100}
                    step={0.5}
                    value={Number.isFinite(bareme.taux[i]) ? Math.round(bareme.taux[i] * 10000) / 100 : ""}
                    onChange={(e) => changerTaux(i, e.target.value === "" ? NaN : Number(e.target.value))}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="actions">
        <button type="button" onClick={ajouter} disabled={n >= TRANCHES_MAX}>
          {texte("simulateur.bareme_ir.ajouter")}
        </button>
        <button type="button" onClick={retirer} disabled={n <= 2}>
          {texte("simulateur.bareme_ir.retirer")}
        </button>
        <button type="button" onClick={() => setBareme(reference)} disabled={!modifie}>
          {texte("simulateur.bareme_ir.revenir", { annee: donnees.annee_bareme })}
        </button>
      </div>
      <fieldset className="decote">
        <legend>{texte("simulateur.bareme_ir.decote")}</legend>
        <label>
          <input
            type="checkbox"
            checked={bareme.decote !== null}
            onChange={(e) => setBareme({ ...bareme, decote: e.target.checked ? reference.decote : null })}
          />{" "}
          {texte("simulateur.bareme_ir.decote_appliquer")}
        </label>
        {bareme.decote && (
          <div className="champs-decote">
            {(["seuil_celibataire", "seuil_couple", "taux"] as const).map((cle) => (
              <label key={cle}>
                {texte(`simulateur.bareme_ir.decote_${cle}`)}
                <input
                  type="number"
                  min={0}
                  step={cle === "taux" ? 0.0025 : 1}
                  value={Number.isFinite(bareme.decote?.[cle]) ? bareme.decote?.[cle] : ""}
                  onChange={(e) => changerDecote(cle, e.target.value === "" ? NaN : Number(e.target.value))}
                />
              </label>
            ))}
          </div>
        )}
      </fieldset>
      <p aria-live="polite">
        {problemes.length > 0
          ? texte("simulateur.bareme_ir.invalide")
          : effet
            ? texte("simulateur.bareme_ir.resultat", {
                central: milliards.format(effet.central),
                bas: milliards.format(effet.bas),
                haut: milliards.format(effet.haut),
                annee: donnees.annee_bareme,
              })
            : texte("simulateur.bareme_ir.inchange")}
      </p>
      {signale(bareme) && (
        <p className="avertissement" role="note">
          {texte("simulateur.bareme_ir.signale", { taux: euros.format(TAUX_SIGNALE * POURCENT) })}
        </p>
      )}
      <p className="source">{texte("simulateur.bareme_ir.limite")}</p>
    </fieldset>
  );
}
