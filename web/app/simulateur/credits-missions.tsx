"use client";
// Réglages des crédits par mission : un curseur par mission du budget général, repliés par
// défaut (29 missions). Le calcul se fait dans le navigateur ; rien n'est envoyé.
import { useId, useState } from "react";
import { texte } from "../../lib/textes";
import type { CatalogueCreditsMissions, ReponsesUnitaires } from "../../lib/donnees";
import { auPas, equivalentMission } from "../../lib/credits-missions";

const PAS = 1;
const milliards = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 });
const signe = new Intl.NumberFormat("fr-FR", { signDisplay: "exceptZero" });

const pourcent = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 });
const pourcentSigne = new Intl.NumberFormat("fr-FR", {
  maximumFractionDigits: 2,
  signDisplay: "exceptZero",
});

type Mission = CatalogueCreditsMissions["missions"][number];

// Aide au chiffrage d'une mission : ses programmes, et l'équivalent pour la mission d'une
// variation d'un seul programme, à appliquer au curseur.
function AideChiffrage({
  mission,
  annee,
  bornes,
  desactive,
  appliquer,
}: {
  mission: Mission;
  annee: number;
  bornes: [number, number];
  desactive: boolean;
  appliquer: (valeur: number) => void;
}) {
  const idBase = useId();
  const programmes = mission.programmes ?? [];
  const [numero, setNumero] = useState(programmes[0]?.numero ?? "");
  const [variation, setVariation] = useState(0);
  if (programmes.length === 0) return null;
  const programme = programmes.find((p) => p.numero === numero) ?? programmes[0];
  const equivalent = equivalentMission(programme.credits, mission.credits, variation);
  const applique = auPas(equivalent, PAS, bornes);
  return (
    <details className="explication">
      <summary>{texte("simulateur.credits_missions.aide_titre")}</summary>
      <p>{texte("simulateur.credits_missions.aide_intro", { annee })}</p>
      <ul>
        {programmes.map((p) => (
          <li key={p.numero}>
            {texte("simulateur.credits_missions.aide_programme", {
              numero: p.numero,
              libelle: p.libelle,
              credits: milliards.format(p.credits),
              part: pourcent.format((100 * p.credits) / mission.credits),
            })}
          </li>
        ))}
      </ul>
      <label htmlFor={`${idBase}-programme`}>{texte("simulateur.credits_missions.aide_choix")}</label>
      <select
        id={`${idBase}-programme`}
        value={programme.numero}
        onChange={(e) => setNumero(e.target.value)}
      >
        {programmes.map((p) => (
          <option key={p.numero} value={p.numero}>
            {p.numero} – {p.libelle}
          </option>
        ))}
      </select>
      <label htmlFor={`${idBase}-variation`}>
        {texte("simulateur.credits_missions.aide_pourcent")}
      </label>
      <input
        id={`${idBase}-variation`}
        type="number"
        step="any"
        value={variation}
        onChange={(e) => setVariation(Number(e.target.value) || 0)}
      />
      <p aria-live="polite">
        {texte("simulateur.credits_missions.aide_resultat", {
          equivalent: pourcentSigne.format(equivalent),
          montant: pourcentSigne.format((equivalent * mission.credits) / 100),
        })}{" "}
        {applique !== equivalent &&
          texte("simulateur.credits_missions.aide_arrondi", {
            pas: PAS,
            applique: signe.format(applique),
          })}
      </p>
      <button type="button" disabled={desactive} onClick={() => appliquer(applique)}>
        {texte("simulateur.credits_missions.aide_appliquer")}
      </button>
      <p className="source">{texte("simulateur.credits_missions.aide_limite")}</p>
    </details>
  );
}

export function ReglagesCreditsMissions({
  catalogue,
  leviers,
  reglages,
  setReglages,
  bloque,
  missionsBloquees,
}: {
  catalogue: CatalogueCreditsMissions;
  leviers: ReponsesUnitaires["leviers"];
  reglages: Record<string, number>;
  setReglages: (v: Record<string, number>) => void;
  bloque: boolean;
  missionsBloquees: string[];
}) {
  const idBase = useId();
  const statut = leviers.credits_missions?.statut;
  const [basse, haute] = catalogue.bornes;
  const reglees = catalogue.missions.filter((m) => (reglages[m.identifiant] ?? 0) !== 0).length;
  return (
    <fieldset className="reglages">
      <legend>
        {texte("simulateur.credits_missions.titre")}
        {statut && statut !== "valide" && (
          <span className="etiquette">{texte(`validation.statuts.${statut}`)}</span>
        )}
      </legend>
      <details className="explication">
        <summary>{texte("simulateur.credits_missions.qu_est_ce")}</summary>
        <p>{texte("simulateur.credits_missions.explication")}</p>
      </details>
      <p>{texte("simulateur.credits_missions.intro", { annee: catalogue.annee_credits })}</p>
      {bloque && <p className="source">{texte("simulateur.credits_missions.bloque")}</p>}
      <details>
        <summary>
          {texte("simulateur.credits_missions.liste", {
            nombre: catalogue.missions.length,
            reglees,
          })}
        </summary>
        {catalogue.missions.map((m) => {
          const id = `${idBase}-${m.identifiant}`;
          const valeur = reglages[m.identifiant] ?? 0;
          const bloqueeSeule = missionsBloquees.includes(m.identifiant);
          return (
            <div key={m.identifiant} className="reglage">
              <label htmlFor={id}>
                {texte("simulateur.credits_missions.mission", {
                  mission: m.libelle,
                  credits: milliards.format(m.credits),
                  annee: catalogue.annee_credits,
                })}
                {" : "}
                <strong>
                  {texte("simulateur.credits_missions.valeur", { valeur: signe.format(valeur) })}
                </strong>
              </label>
              <input
                id={id}
                type="range"
                min={Math.ceil(basse / PAS) * PAS}
                max={Math.floor(haute / PAS) * PAS}
                step={PAS}
                value={valeur}
                disabled={bloque || bloqueeSeule}
                onChange={(e) =>
                  setReglages({ ...reglages, [m.identifiant]: Number(e.target.value) })
                }
              />
              {bloqueeSeule && (
                <span className="source">{texte("simulateur.credits_missions.bloque_indexation")}</span>
              )}
              <AideChiffrage
                mission={m}
                annee={catalogue.annee_credits}
                bornes={catalogue.bornes}
                desactive={bloque || bloqueeSeule}
                appliquer={(v) => setReglages({ ...reglages, [m.identifiant]: v })}
              />
            </div>
          );
        })}
      </details>
    </fieldset>
  );
}
