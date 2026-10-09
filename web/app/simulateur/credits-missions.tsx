"use client";
// Réglages des crédits par mission : un curseur par mission du budget général, repliés par
// défaut (29 missions). Le calcul se fait dans le navigateur ; rien n'est envoyé.
import { useId } from "react";
import { texte } from "../../lib/textes";
import type { CatalogueCreditsMissions, ReponsesUnitaires } from "../../lib/donnees";

const PAS = 1;
const milliards = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 });
const signe = new Intl.NumberFormat("fr-FR", { signDisplay: "exceptZero" });

export function ReglagesCreditsMissions({
  catalogue,
  leviers,
  reglages,
  setReglages,
}: {
  catalogue: CatalogueCreditsMissions;
  leviers: ReponsesUnitaires["leviers"];
  reglages: Record<string, number>;
  setReglages: (v: Record<string, number>) => void;
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
      <p>{texte("simulateur.credits_missions.intro", { annee: catalogue.annee_credits })}</p>
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
                onChange={(e) =>
                  setReglages({ ...reglages, [m.identifiant]: Number(e.target.value) })
                }
              />
            </div>
          );
        })}
      </details>
    </fieldset>
  );
}
