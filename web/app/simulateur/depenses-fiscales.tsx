"use client";
// Réglages des dépenses fiscales : un curseur par impôt, et des dépenses choisies une à une
// dans le catalogue. Une dépense ne peut pas être réglée deux fois (moteur :
// ``verifier_double_compte``) : le curseur d'un impôt est bloqué tant qu'une de ses dépenses
// est choisie, et une dépense d'un impôt dont le curseur n'est pas à zéro ne peut être ajoutée.
import { useId, useState } from "react";
import { texte } from "../../lib/textes";
import type { CatalogueDepensesFiscales, ReponsesUnitaires } from "../../lib/donnees";
import { lignesFiche, rechercher } from "../../lib/depenses-fiscales";
import type { FicheDepense } from "../../lib/donnees";

const PAS = 5;
const RESULTATS_MAX = 20;
const milliards = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 });
const millions = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });

// Fiche descriptive d'une dépense fiscale (tome II de Voies et moyens), dépliable.
function Fiche({ fiche }: { fiche: FicheDepense | null | undefined }) {
  const lignes = lignesFiche(fiche);
  if (lignes.length === 0) return null;
  return (
    <details className="explication">
      <summary>{texte("simulateur.depenses_fiscales.fiche.titre")}</summary>
      <dl>
        {lignes.map(([cle, v]) => (
          <div key={cle}>
            <dt>{texte(`simulateur.depenses_fiscales.fiche.${cle}`)}</dt>
            <dd>{v || texte("simulateur.depenses_fiscales.fiche.finalite_absente")}</dd>
          </div>
        ))}
      </dl>
      <p className="source">{texte("simulateur.depenses_fiscales.fiche.source")}</p>
    </details>
  );
}

export function ReglagesDepensesFiscales({
  catalogue,
  leviers,
  parImpot,
  setParImpot,
  parDepense,
  setParDepense,
}: {
  catalogue: CatalogueDepensesFiscales;
  leviers: ReponsesUnitaires["leviers"];
  parImpot: Record<string, number>;
  setParImpot: (v: Record<string, number>) => void;
  parDepense: Record<string, number>;
  setParDepense: (v: Record<string, number>) => void;
}) {
  const idBase = useId();
  const [requete, setRequete] = useState("");
  const annee = catalogue.annee_cout;
  const choisies = catalogue.depenses.filter((d) => d.code in parDepense);
  const impotsChoisis = new Set(choisies.map((d) => d.impot));
  const resultats = rechercher(catalogue.depenses, requete, RESULTATS_MAX).filter(
    (d) => !(d.code in parDepense),
  );
  const statut = leviers.depense_fiscale?.statut;
  const cout = (d: (typeof catalogue.depenses)[number]) =>
    texte(
      d.annee_chiffrage === annee
        ? "simulateur.depenses_fiscales.cout"
        : "simulateur.depenses_fiscales.cout_repris",
      {
        cout: millions.format(d.cout * 1000),
        annee,
        annee_chiffrage: d.annee_chiffrage,
        fiabilite: d.fiabilite || texte("simulateur.depenses_fiscales.fiabilite_inconnue"),
      },
    );

  return (
    <fieldset className="reglages">
      <legend>
        {texte("simulateur.depenses_fiscales.titre")}
        {statut && statut !== "valide" && (
          <span className="etiquette">{texte(`validation.statuts.${statut}`)}</span>
        )}
      </legend>
      <details className="explication">
        <summary>{texte("simulateur.depenses_fiscales.qu_est_ce")}</summary>
        <p>{texte("simulateur.depenses_fiscales.explication")}</p>
      </details>
      <p>{texte("simulateur.depenses_fiscales.intro", { annee })}</p>
      <h3>{texte("simulateur.depenses_fiscales.par_impot")}</h3>
      {catalogue.ordre_impots.map((impot) => {
        const total = catalogue.impots[impot].cout;
        const id = `${idBase}-${impot}`;
        const bloque = impotsChoisis.has(impot);
        return (
          <div key={impot} className="reglage">
            <label htmlFor={id}>
              {texte("simulateur.depenses_fiscales.impot", {
                impot: texte(`simulateur.depenses_fiscales.impots.${impot}`),
                cout: milliards.format(total),
                annee,
              })}
              {" : "}
              <strong>
                {texte("simulateur.depenses_fiscales.valeur", { valeur: parImpot[impot] ?? 0 })}
              </strong>
            </label>
            <input
              id={id}
              type="range"
              min={0}
              max={100}
              step={PAS}
              disabled={bloque}
              value={parImpot[impot] ?? 0}
              onChange={(e) => setParImpot({ ...parImpot, [impot]: Number(e.target.value) })}
            />
            {bloque && (
              <span className="source">{texte("simulateur.depenses_fiscales.impot_bloque")}</span>
            )}
          </div>
        );
      })}
      <h3>
        {texte("simulateur.depenses_fiscales.une_depense", {
          nombre: catalogue.depenses.length,
        })}
      </h3>
      {choisies.map((d) => {
        const id = `${idBase}-${d.code}`;
        return (
          <div key={d.code} className="reglage">
            <label htmlFor={id}>
              {d.code} : {d.libelle}
              {" : "}
              <strong>
                {texte("simulateur.depenses_fiscales.valeur", { valeur: parDepense[d.code] })}
              </strong>
            </label>
            <span className="source">{cout(d)}</span>
            {d.fiche?.finalite && (
              <span className="source">
                {texte("simulateur.depenses_fiscales.fiche.finalite")} : {d.fiche.finalite}
              </span>
            )}
            <Fiche fiche={d.fiche} />
            <input
              id={id}
              type="range"
              min={0}
              max={100}
              step={PAS}
              value={parDepense[d.code]}
              onChange={(e) => setParDepense({ ...parDepense, [d.code]: Number(e.target.value) })}
            />
            <button
              type="button"
              onClick={() => {
                const reste = { ...parDepense };
                delete reste[d.code];
                setParDepense(reste);
              }}
            >
              {texte("simulateur.depenses_fiscales.retirer")}
            </button>
          </div>
        );
      })}
      <label htmlFor={`${idBase}-recherche`}>
        {texte("simulateur.depenses_fiscales.recherche")}
      </label>
      <input
        id={`${idBase}-recherche`}
        type="search"
        value={requete}
        onChange={(e) => setRequete(e.target.value)}
      />
      {requete.trim() !== "" && resultats.length === 0 && (
        <p>{texte("simulateur.depenses_fiscales.aucun_resultat")}</p>
      )}
      {resultats.length > 0 && (
        <ul className="resultats">
          {resultats.map((d) => {
            const couverte = (parImpot[d.impot] ?? 0) !== 0;
            return (
              <li key={d.code}>
                <button
                  type="button"
                  disabled={couverte}
                  onClick={() => {
                    setParDepense({ ...parDepense, [d.code]: 0 });
                    setRequete("");
                  }}
                >
                  {texte("simulateur.depenses_fiscales.ajouter")}
                </button>{" "}
                {d.code} : {d.libelle} <span className="source">({cout(d)})</span>
                {d.fiche?.finalite && (
                  <span className="source">
                    {" "}
                    {texte("simulateur.depenses_fiscales.fiche.finalite")} : {d.fiche.finalite}
                  </span>
                )}
                {couverte && (
                  <span className="source">
                    {" "}
                    {texte("simulateur.depenses_fiscales.deja_par_impot")}
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </fieldset>
  );
}
