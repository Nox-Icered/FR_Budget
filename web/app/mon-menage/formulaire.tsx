"use client";
// Formulaire du ménage saisi. Règle 5 : la saisie reste dans la mémoire de la page ; elle n'est
// ni stockée dans le navigateur ni mise dans l'adresse, et n'est envoyée qu'au service de calcul.
import { useEffect, useId, useRef, useState } from "react";
import { texte } from "../../lib/textes";
import { lignesCascade, lignesComparees } from "../../lib/cascade";
import { region } from "../../lib/region";
import {
  STATUTS,
  adresseService,
  calculer,
  decoderScenarioMenage,
  preparer,
  type AdulteFormulaire,
  type Bornes,
  type MenageFormulaire,
  type Probleme,
  type ResultatMonMenage,
  type ScenarioMenage,
} from "../../lib/mon-menage";
import { chemin } from "../../lib/chemin";

const MOIS_PAR_AN = 12;
const euros = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const ADRESSE = adresseService(process.env.NEXT_PUBLIC_API_URL);

const adulteVide = (): AdulteFormulaire => ({
  statut: "salarie",
  montant: "",
  naissance: "",
  cadre: false,
});

export function Formulaire({
  bornes,
  leviers,
  leviersIncidence,
}: {
  bornes: Bornes;
  leviers: { id: string; bornes: [number, number] }[];
  leviersIncidence: string[];
}) {
  const idBase = useId();
  // Mesures transmises par le simulateur dans l'adresse (jamais la saisie du ménage).
  const [scenario, setScenario] = useState<ScenarioMenage | null>(null);
  const [scenarioIllisible, setScenarioIllisible] = useState(false);
  useEffect(() => {
    const recherche = window.location.search;
    if (!recherche) return;
    const lu = decoderScenarioMenage(recherche, leviers, leviersIncidence);
    if (lu) setScenario(lu);
    else setScenarioIllisible(true);
  }, [leviers, leviersIncidence]);
  const [menage, setMenage] = useState<MenageFormulaire>({ adultes: [adulteVide()], enfants: [] });
  const [problemes, setProblemes] = useState<Probleme[]>([]);
  const [resultat, setResultat] = useState<ResultatMonMenage | null>(null);
  const [erreur, setErreur] = useState(false);
  const [enCours, setEnCours] = useState(false);
  // Révision de la saisie : une réponse arrivée après une modification est ignorée.
  const revision = useRef(0);

  if (ADRESSE === null) {
    return (
      <p className="avertissement" role="note">
        {texte("mon_menage.hors_ligne")}
      </p>
    );
  }
  const adresse = ADRESSE;

  // Toute modification efface le résultat affiché et périme la requête en cours.
  const modifier = (suivant: MenageFormulaire) => {
    revision.current += 1;
    setMenage(suivant);
    setResultat(null);
    setErreur(false);
    setEnCours(false);
  };
  const changerAdulte = (i: number, champ: Partial<AdulteFormulaire>) =>
    modifier({
      ...menage,
      adultes: menage.adultes.map((a, k) => (k === i ? { ...a, ...champ } : a)),
    });
  const changerEnfants = (enfants: string[]) => modifier({ ...menage, enfants });

  const envoyer = async (e: React.FormEvent) => {
    e.preventDefault();
    setErreur(false);
    setResultat(null);
    const r = preparer(menage, bornes);
    if ("problemes" in r) {
      setProblemes(r.problemes);
      return;
    }
    setProblemes([]);
    setEnCours(true);
    const envoi = revision.current;
    try {
      const corps = scenario ? { ...r.corps, scenario } : r.corps;
      const reponse = await calculer(adresse, corps);
      if (envoi === revision.current) setResultat(reponse);
    } catch {
      if (envoi === revision.current) setErreur(true);
    } finally {
      if (envoi === revision.current) setEnCours(false);
    }
  };

  return (
    <>
      {scenarioIllisible && <p className="avertissement">{texte("mon_menage.scenario.illisible")}</p>}
      {scenario && (
        <section>
          <h2>{texte("mon_menage.scenario.titre")}</h2>
          <p>{texte("mon_menage.scenario.intro")}</p>
          <ul>
            {Object.entries(scenario.mesures).map(([k, v]) => (
              <li key={k}>
                {texte(`mon_menage.scenario.mesures.${k}`, {
                  valeur: new Intl.NumberFormat("fr-FR", { signDisplay: "exceptZero" }).format(v),
                })}
              </li>
            ))}
          </ul>
          {scenario.incidence === "salaire" && <p>{texte("mon_menage.scenario.incidence_salaire")}</p>}
          <p>
            <a href={chemin("/mon-menage/")}>{texte("mon_menage.scenario.retirer")}</a>
          </p>
        </section>
      )}
      <form onSubmit={envoyer} autoComplete="off" noValidate>
        {menage.adultes.map((a, i) => {
          const id = `${idBase}-adulte-${i}`;
          return (
            <fieldset key={i} className="reglages">
              <legend>{texte("mon_menage.adulte", { n: i + 1 })}</legend>
              <label htmlFor={`${id}-statut`}>{texte("mon_menage.statut")}</label>
              <select
                id={`${id}-statut`}
                value={a.statut}
                onChange={(e) =>
                  changerAdulte(i, { statut: e.target.value as AdulteFormulaire["statut"] })
                }
              >
                {STATUTS.map((s) => (
                  <option key={s} value={s}>
                    {texte(`mon_menage.statuts.${s}`)}
                  </option>
                ))}
              </select>
              <label htmlFor={`${id}-montant`}>{texte(`mon_menage.montant.${a.statut}`)}</label>
              <input
                id={`${id}-montant`}
                type="text"
                inputMode="decimal"
                value={a.montant}
                onChange={(e) => changerAdulte(i, { montant: e.target.value })}
              />
              <label htmlFor={`${id}-naissance`}>{texte("mon_menage.naissance")}</label>
              <input
                id={`${id}-naissance`}
                type="text"
                inputMode="numeric"
                value={a.naissance}
                onChange={(e) => changerAdulte(i, { naissance: e.target.value })}
              />
              {a.statut === "salarie" && (
                <div className="interrupteur">
                  <input
                    id={`${id}-cadre`}
                    type="checkbox"
                    checked={a.cadre}
                    onChange={(e) => changerAdulte(i, { cadre: e.target.checked })}
                  />
                  <label htmlFor={`${id}-cadre`}>{texte("mon_menage.cadre")}</label>
                </div>
              )}
            </fieldset>
          );
        })}
        <div className="actions">
          {menage.adultes.length < bornes.adultes_max ? (
            <button
              type="button"
              onClick={() => modifier({ ...menage, adultes: [...menage.adultes, adulteVide()] })}
            >
              {texte("mon_menage.ajouter_adulte")}
            </button>
          ) : (
            <button
              type="button"
              onClick={() => modifier({ ...menage, adultes: menage.adultes.slice(0, 1) })}
            >
              {texte("mon_menage.retirer_adulte")}
            </button>
          )}
        </div>
        <fieldset className="reglages">
          <legend>{texte("mon_menage.enfants")}</legend>
          {menage.enfants.map((n, i) => (
            <div key={i} className="reglage">
              <label htmlFor={`${idBase}-enfant-${i}`}>
                {texte("mon_menage.naissance_enfant", { n: i + 1 })}
              </label>
              <input
                id={`${idBase}-enfant-${i}`}
                type="text"
                inputMode="numeric"
                value={n}
                onChange={(e) =>
                  changerEnfants(menage.enfants.map((x, k) => (k === i ? e.target.value : x)))
                }
              />
            </div>
          ))}
          <div className="actions">
            {menage.enfants.length < bornes.enfants_max && (
              <button type="button" onClick={() => changerEnfants([...menage.enfants, ""])}>
                {texte("mon_menage.ajouter_enfant")}
              </button>
            )}
            {menage.enfants.length > 0 && (
              <button type="button" onClick={() => changerEnfants(menage.enfants.slice(0, -1))}>
                {texte("mon_menage.retirer_enfant")}
              </button>
            )}
          </div>
        </fieldset>
        <div className="actions">
          <button type="submit" disabled={enCours}>
            {texte("mon_menage.calculer")}
          </button>
        </div>
      </form>
      <div aria-live="polite">
        {problemes.length > 0 && (
          <ul className="avertissement">
            {problemes.map((p, i) => (
              <li key={i}>{texte(`mon_menage.erreurs.${p.cle}`, p.variables)}</li>
            ))}
          </ul>
        )}
        {erreur && <p className="avertissement">{texte("mon_menage.erreur_service")}</p>}
        {enCours && <p>{texte("mon_menage.en_cours")}</p>}
        {resultat && <Resultat r={resultat} />}
      </div>
    </>
  );
}

function Resultat({ r }: { r: ResultatMonMenage }) {
  const titre = texte("mon_menage.resultat", { annee: r.annee_revenus });
  const apres = r.scenario?.apres;
  const signe = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0, signDisplay: "exceptZero" });
  return (
    <section>
      <h2>{titre}</h2>
      {r.scenario && apres === null && (
        <p className="avertissement">{texte("mon_menage.scenario.non_chiffre")}</p>
      )}
      <div className="defilement" {...region(titre)}>
        <table>
          <thead>
            <tr>
              <th scope="col">{texte("menages.ligne")}</th>
              {apres ? (
                <>
                  <th scope="col">{texte("menages.effets.avant")}</th>
                  <th scope="col">{texte("menages.effets.apres")}</th>
                  <th scope="col">{texte("menages.effets.ecart")}</th>
                </>
              ) : (
                <>
                  <th scope="col">{texte("menages.an")}</th>
                  <th scope="col">{texte("menages.mois")}</th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {apres
              ? lignesComparees(r, apres).map((l) => (
                  <tr key={l.libelle}>
                    <th scope="row">{l.libelle}</th>
                    <td className="nombre">{euros.format(l.avant)}</td>
                    <td className="nombre">{euros.format(l.apres)}</td>
                    <td className="nombre">{signe.format(Math.round(l.ecart))}</td>
                  </tr>
                ))
              : lignesCascade(r).map(([libelle, v]) => (
                  <tr key={libelle}>
                    <th scope="row">{libelle}</th>
                    <td className="nombre">{euros.format(v)}</td>
                    <td className="nombre">{euros.format(v / MOIS_PAR_AN)}</td>
                  </tr>
                ))}
          </tbody>
        </table>
      </div>
      <p className="source">
        {texte("menages.sources")}{" "}
        {r.sources.map((s, i) => (
          <span key={s}>
            {i > 0 && ", "}
            <a href={chemin(`/sources/#${s}`)}>{s}</a>
          </span>
        ))}
      </p>
    </section>
  );
}
