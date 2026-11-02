"use client";
// Réglages des dépenses fiscales : un curseur par impôt, et des dépenses choisies une à une
// dans le catalogue. Une dépense ne peut pas être réglée deux fois (moteur :
// ``verifier_double_compte``) : le curseur d'un impôt est bloqué tant qu'une de ses dépenses
// est choisie, et une dépense d'un impôt dont le curseur n'est pas à zéro ne peut être ajoutée.
import { useId, useState } from "react";
import { texte } from "../../lib/textes";
import type { CatalogueDepensesFiscales, ReponsesUnitaires } from "../../lib/donnees";
import { equivalentImpot, lignesFiche, rechercher } from "../../lib/depenses-fiscales";
import { auPas } from "../../lib/credits-missions";
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

const NICHES_LISTEES = 10;
const pourcent = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 });
type Niche = CatalogueDepensesFiscales["depenses"][number];

// Aide au chiffrage des niches d'un impôt : les plus coûteuses, puis, pour une niche et un
// pourcentage de réduction, son coût et l'équivalent pour toutes les niches de l'impôt.
function AideNiches({
  niches,
  total,
  annee,
  impotRegle,
  nichesChoisies,
  reglerNiche,
  reglerImpot,
}: {
  niches: Niche[];
  total: number;
  annee: number;
  impotRegle: boolean;
  nichesChoisies: boolean;
  reglerNiche: (code: string, valeur: number) => void;
  reglerImpot: (valeur: number) => void;
}) {
  const idBase = useId();
  const [code, setCode] = useState(niches[0]?.code ?? "");
  const [reduction, setReduction] = useState(50);
  if (niches.length === 0) return null;
  const niche = niches.find((d) => d.code === code) ?? niches[0];
  const equivalent = equivalentImpot(niche.cout, total, reduction);
  const appliqueNiche = auPas(reduction, PAS, [0, 100]);
  const appliqueImpot = auPas(equivalent, PAS, [0, 100]);
  return (
    <details className="explication">
      <summary>{texte("simulateur.depenses_fiscales.aide_titre")}</summary>
      <p>
        {texte("simulateur.depenses_fiscales.aide_intro", {
          annee,
          nombre: Math.min(NICHES_LISTEES, niches.length),
          total: niches.length,
        })}
      </p>
      <ul className="liste-niches">
        {niches.slice(0, NICHES_LISTEES).map((d) => (
          <li key={d.code}>
            <strong>
              {texte("simulateur.depenses_fiscales.aide_niche", {
                code: d.code,
                libelle: d.libelle,
                cout: millions.format(d.cout * 1000),
                part: pourcent.format((100 * d.cout) / total),
              })}
            </strong>
            {d.fiche?.finalite && (
              <span className="source">
                {" "}
                {texte("simulateur.depenses_fiscales.fiche.finalite")} : {d.fiche.finalite}
              </span>
            )}
          </li>
        ))}
      </ul>
      <label htmlFor={`${idBase}-niche`}>{texte("simulateur.depenses_fiscales.aide_choix")}</label>
      <select id={`${idBase}-niche`} value={niche.code} onChange={(e) => setCode(e.target.value)}>
        {niches.map((d) => (
          <option key={d.code} value={d.code}>
            {d.code} – {d.libelle}
          </option>
        ))}
      </select>
      <label htmlFor={`${idBase}-reduction`}>
        {texte("simulateur.depenses_fiscales.aide_reduction")}
      </label>
      <input
        id={`${idBase}-reduction`}
        type="number"
        min={0}
        max={100}
        step="any"
        value={reduction}
        onChange={(e) => setReduction(Math.min(100, Math.max(0, Number(e.target.value) || 0)))}
      />
      <p aria-live="polite">
        {texte("simulateur.depenses_fiscales.aide_resultat", {
          montant: millions.format((niche.cout * 1000 * reduction) / 100),
          annee,
          equivalent: pourcent.format(equivalent),
        })}
      </p>
      <div className="actions">
        <button
          type="button"
          disabled={impotRegle}
          onClick={() => reglerNiche(niche.code, appliqueNiche)}
        >
          {texte("simulateur.depenses_fiscales.aide_regler_niche", { valeur: appliqueNiche })}
        </button>
        <button
          type="button"
          disabled={nichesChoisies}
          onClick={() => reglerImpot(appliqueImpot)}
        >
          {texte("simulateur.depenses_fiscales.aide_regler_impot", { valeur: appliqueImpot })}
        </button>
      </div>
      {impotRegle && (
        <p className="source">{texte("simulateur.depenses_fiscales.deja_par_impot")}</p>
      )}
      <p className="source">{texte("simulateur.depenses_fiscales.aide_limite")}</p>
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
  const [ouverts, setOuverts] = useState<Record<string, boolean>>({});
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
      {catalogue.ordre_impots.map((impot) => {
        const total = catalogue.impots[impot].cout;
        const id = `${idBase}-${impot}`;
        const bloque = impotsChoisis.has(impot);
        const niches = catalogue.depenses
          .filter((d) => d.impot === impot)
          .sort((a, b) => b.cout - a.cout);
        const choisiesImpot = choisies.filter((d) => d.impot === impot);
        const valeurImpot = parImpot[impot] ?? 0;
        const nReglees = (valeurImpot !== 0 ? 1 : 0) + choisiesImpot.length;
        return (
          <details
            key={impot}
            className="groupe-impot"
            open={ouverts[impot] ?? nReglees > 0}
            onToggle={(e) => {
              const ouvert = e.currentTarget.open;
              setOuverts((o) => ({ ...o, [impot]: ouvert }));
            }}
          >
            <summary>
              <span className="section-titre">
                {texte(`simulateur.depenses_fiscales.impots.${impot}`)}
              </span>
              <span className="section-description">
                {texte("simulateur.depenses_fiscales.resume_impot", {
                  cout: milliards.format(total),
                  annee,
                  nombre: niches.length,
                })}
              </span>
              {nReglees > 0 && (
                <span className="pastille">
                  {texte("simulateur.reglees", { nombre: nReglees })}
                </span>
              )}
            </summary>
            <div className="reglage">
              <label htmlFor={id}>
                {texte("simulateur.depenses_fiscales.toutes_niches")}
                {" : "}
                <strong>{texte("simulateur.depenses_fiscales.valeur", { valeur: valeurImpot })}</strong>
              </label>
              <input
                id={id}
                type="range"
                min={0}
                max={100}
                step={PAS}
                disabled={bloque}
                value={valeurImpot}
                onChange={(e) => setParImpot({ ...parImpot, [impot]: Number(e.target.value) })}
              />
              {bloque && (
                <span className="source">{texte("simulateur.depenses_fiscales.impot_bloque")}</span>
              )}
            </div>
            <AideNiches
              niches={niches}
              total={total}
              annee={annee}
              impotRegle={valeurImpot !== 0}
              nichesChoisies={choisiesImpot.length > 0}
              reglerNiche={(code, valeur) => setParDepense({ ...parDepense, [code]: valeur })}
              reglerImpot={(valeur) => setParImpot({ ...parImpot, [impot]: valeur })}
            />
            {choisiesImpot.map((d) => {
              const idNiche = `${idBase}-${d.code}`;
              return (
                <div key={d.code} className="reglage">
                  <label htmlFor={idNiche}>
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
                    id={idNiche}
                    type="range"
                    min={0}
                    max={100}
                    step={PAS}
                    value={parDepense[d.code]}
                    onChange={(e) =>
                      setParDepense({ ...parDepense, [d.code]: Number(e.target.value) })
                    }
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
          </details>
        );
      })}
      <h3>
        {texte("simulateur.depenses_fiscales.une_depense", {
          nombre: catalogue.depenses.length,
        })}
      </h3>
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
