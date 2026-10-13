"use client";
// Effet du scénario sur les ménages types, approché à partir de la grille de cascades exactes
// (lib/effets-menages.ts) ; l'écart au calcul complet, mesuré sur des scénarios de contrôle, est
// affiché avec le résultat.
import { useId, useState } from "react";
import Link from "next/link";
import { texte } from "../../lib/textes";
import { region } from "../../lib/region";
import { useMenagesScenario } from "../../lib/chargement";
import { approcher, type Incidence } from "../../lib/effets-menages";
import { encoderScenarioMenage } from "../../lib/mon-menage";

const euros = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0, signDisplay: "exceptZero" });
const entier = (v: number) => euros.format(Math.round(v));

export function EffetsMenagesScenario({
  valeurs,
  empreinte,
}: {
  valeurs: Record<string, number>;
  empreinte: string;
}) {
  const id = useId();
  const [incidence, setIncidence] = useState<Incidence>("comptable");
  const chargement = useMenagesScenario(empreinte);
  if (chargement.etat === "en_cours") return <p>{texte("simulateur.menages.chargement")}</p>;
  if (chargement.etat === "erreur")
    return <p className="avertissement">{texte("simulateur.menages.erreur")}</p>;
  const d = chargement.donnees;
  const mesures = Object.entries(valeurs).filter(
    ([k, v]) => v !== 0 && k in d.grille,
  ) as [string, number][];
  const ecartees = Object.entries(valeurs)
    .filter(([k, v]) => v !== 0 && k in d.sans_effet)
    .map(([k]) => texte(`menages.effets.raisons.${d.sans_effet[k]}`));
  const avecIncidence = mesures.some(([k]) => d.leviers_incidence.includes(k));
  const lecture = avecIncidence ? incidence : "comptable";
  const titre = texte("simulateur.menages.titre");
  const lien = encoderScenarioMenage({ mesures: Object.fromEntries(mesures), incidence: lecture });

  return (
    <section>
      <h2>{titre}</h2>
      <p>{texte("simulateur.menages.intro", { annee: d.annee_revenus })}</p>
      {mesures.length === 0 ? (
        <p>{texte("simulateur.menages.aucune")}</p>
      ) : (
        <>
          {avecIncidence && (
            <fieldset className="reglages">
              <legend>{texte("menages.effets.incidence.legende")}</legend>
              {(["comptable", "salaire"] as Incidence[]).map((i) => (
                <div key={i} className="interrupteur">
                  <input
                    id={`${id}-${i}`}
                    type="radio"
                    name={`${id}-incidence`}
                    checked={incidence === i}
                    onChange={() => setIncidence(i)}
                  />
                  <label htmlFor={`${id}-${i}`}>{texte(`menages.effets.incidence.${i}`)}</label>
                </div>
              ))}
            </fieldset>
          )}
          <div className="defilement" {...region(titre)}>
            <table>
              <thead>
                <tr>
                  <th scope="col">{texte("simulateur.menages.menage")}</th>
                  <th scope="col">{texte("simulateur.menages.net")}</th>
                  <th scope="col">{texte("simulateur.menages.cout")}</th>
                  {avecIncidence && <th scope="col">{texte("simulateur.menages.fourchette")}</th>}
                </tr>
              </thead>
              <tbody>
                {d.menages.map((m) => {
                  const calcul = (i: Incidence) =>
                    approcher(m, m.id, mesures, d.grille, d.leviers_incidence, i);
                  const r = calcul(lecture);
                  const lectures = avecIncidence
                    ? (["comptable", "salaire"] as Incidence[]).map(calcul)
                    : [];
                  const nets = lectures.flatMap((c) => (c ? [c.net_apres_impot - m.net_apres_impot] : []));
                  return (
                    <tr key={m.id}>
                      <th scope="row">{m.libelle}</th>
                      {r === null ? (
                        <td colSpan={avecIncidence ? 3 : 2}>{texte("simulateur.menages.non_chiffre")}</td>
                      ) : (
                        <>
                          <td className="nombre">{entier(r.net_apres_impot - m.net_apres_impot)}</td>
                          <td className="nombre">{entier(r.cout_employeur - m.cout_employeur)}</td>
                          {avecIncidence && (
                            <td className="nombre">
                              {texte("simulateur.menages.de_a", {
                                bas: entier(Math.min(...nets)),
                                haut: entier(Math.max(...nets)),
                              })}
                            </td>
                          )}
                        </>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="source">
            {texte("simulateur.menages.approximation", {
              un_levier: entier(d.ecart_max_un_levier).replace("+", ""),
              combinaison: entier(d.ecart_max_combinaison).replace("+", ""),
            })}
            {lecture === "salaire" &&
              ` ${texte("simulateur.menages.approximation_salaire", {
                un_levier: entier(d.ecart_max_salaire_un_levier).replace("+", ""),
                combinaison: entier(d.ecart_max_salaire_combinaison).replace("+", ""),
              })}`}
          </p>
          <p>
            <Link href={`/mon-menage/?${lien}`}>{texte("simulateur.menages.mon_menage")}</Link>
            {" · "}
            <Link href="/menages/">{texte("simulateur.menages.detail")}</Link>
          </p>
        </>
      )}
      {ecartees.length > 0 && (
        <>
          <p>{texte("simulateur.menages.ecartees")}</p>
          <ul>
            {[...new Set(ecartees)].map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
