"use client";
// Formulaire du ménage saisi. Règle 5 : la saisie reste dans la mémoire de la page ; elle n'est
// ni stockée dans le navigateur ni mise dans l'adresse, et n'est envoyée qu'au service de calcul.
import { useId, useState } from "react";
import { texte } from "../../lib/textes";
import { lignesCascade } from "../../lib/cascade";
import { region } from "../../lib/region";
import {
  STATUTS,
  adresseService,
  calculer,
  preparer,
  type AdulteFormulaire,
  type Bornes,
  type MenageFormulaire,
  type Probleme,
  type ResultatMonMenage,
} from "../../lib/mon-menage";

const MOIS_PAR_AN = 12;
const euros = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const ADRESSE = adresseService(process.env.NEXT_PUBLIC_API_URL);

const adulteVide = (): AdulteFormulaire => ({
  statut: "salarie",
  montant: "",
  naissance: "",
  cadre: false,
});

export function Formulaire({ bornes }: { bornes: Bornes }) {
  const idBase = useId();
  const [menage, setMenage] = useState<MenageFormulaire>({ adultes: [adulteVide()], enfants: [] });
  const [problemes, setProblemes] = useState<Probleme[]>([]);
  const [resultat, setResultat] = useState<ResultatMonMenage | null>(null);
  const [erreur, setErreur] = useState(false);
  const [enCours, setEnCours] = useState(false);

  if (ADRESSE === null) {
    return (
      <p className="avertissement" role="note">
        {texte("mon_menage.hors_ligne")}
      </p>
    );
  }
  const adresse = ADRESSE;

  const changerAdulte = (i: number, champ: Partial<AdulteFormulaire>) => {
    setMenage({
      ...menage,
      adultes: menage.adultes.map((a, k) => (k === i ? { ...a, ...champ } : a)),
    });
    setResultat(null);
  };
  const changerEnfants = (enfants: string[]) => {
    setMenage({ ...menage, enfants });
    setResultat(null);
  };

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
    try {
      setResultat(await calculer(adresse, r.corps));
    } catch {
      setErreur(true);
    } finally {
      setEnCours(false);
    }
  };

  return (
    <>
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
              onClick={() => setMenage({ ...menage, adultes: [...menage.adultes, adulteVide()] })}
            >
              {texte("mon_menage.ajouter_adulte")}
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setMenage({ ...menage, adultes: menage.adultes.slice(0, 1) })}
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
  return (
    <section>
      <h2>{titre}</h2>
      <div className="defilement" {...region(titre)}>
        <table>
          <thead>
            <tr>
              <th scope="col">{texte("menages.ligne")}</th>
              <th scope="col">{texte("menages.an")}</th>
              <th scope="col">{texte("menages.mois")}</th>
            </tr>
          </thead>
          <tbody>
            {lignesCascade(r).map(([libelle, v]) => (
              <tr key={libelle}>
                <th scope="row">{libelle}</th>
                <td className="nombre">{euros.format(v)}</td>
                <td className="nombre">{euros.format(v / MOIS_PAR_AN)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
