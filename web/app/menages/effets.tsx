"use client";
// Effet d'une mesure sur un ménage type : cascade avant et après, écart ligne par ligne.
// Données exportées par l'API (menages-effets.json) ; rien n'est saisi ni envoyé.
import { useId, useState } from "react";
import { texte } from "../../lib/textes";
import { lignesComparees } from "../../lib/cascade";
import { region } from "../../lib/region";
import type { EffetsMenages, Incidence, MenageType } from "../../lib/donnees";

const euros = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const ecartSigne = new Intl.NumberFormat("fr-FR", {
  maximumFractionDigits: 0,
  signDisplay: "exceptZero",
});
type Sens = "hausse" | "baisse";

export function EffetsLeviers({
  effets,
  menages,
}: {
  effets: EffetsMenages;
  menages: MenageType[];
}) {
  const id = useId();
  const options = effets.leviers.flatMap((l) =>
    (["hausse", "baisse"] as Sens[]).map((sens) => ({ levier: l.id, sens })),
  );
  const [choix, setChoix] = useState(0);
  const [menageId, setMenageId] = useState(menages[0].id);
  const [incidence, setIncidence] = useState<Incidence>(effets.incidence_par_defaut);
  const { levier, sens } = options[choix];
  const menage = menages.find((m) => m.id === menageId) ?? menages[0];
  const avecIncidence = effets.leviers_incidence.includes(levier);
  const lecture = (i: Incidence) =>
    (i === "salaire" ? effets.effets_salaire : effets.effets)[levier][sens][menage.id];
  const apres = lecture(avecIncidence ? incidence : "comptable");
  // Fourchette : les deux lectures de l'incidence bornent l'écart.
  const lectures = avecIncidence
    ? (["comptable", "salaire"] as Incidence[]).map(lecture).filter((c) => c !== null)
    : [];
  const ecarts = (cle: "net_apres_impot" | "cout_employeur") =>
    lectures.map((c) => Math.round(c[cle] - menage[cle]));
  const mesure = texte(`menages.effets.leviers.${levier}.${sens}`);
  const lignes = apres ? lignesComparees(menage, apres) : [];
  const aucun = apres !== null && lignes.every((l) => Math.round(l.ecart) === 0);
  const legende = texte("menages.effets.legende", { menage: menage.libelle, mesure });

  return (
    <section>
      <h2>{texte("menages.effets.titre")}</h2>
      <p>{texte("menages.effets.intro", { annee: effets.annee_revenus })}</p>
      <div className="reglages">
        <label htmlFor={`${id}-mesure`}>{texte("menages.effets.mesure")}</label>
        <select id={`${id}-mesure`} value={choix} onChange={(e) => setChoix(Number(e.target.value))}>
          {options.map((o, i) => (
            <option key={`${o.levier}-${o.sens}`} value={i}>
              {texte(`menages.effets.leviers.${o.levier}.${o.sens}`)}
            </option>
          ))}
        </select>
        <label htmlFor={`${id}-menage`}>{texte("menages.effets.menage")}</label>
        <select id={`${id}-menage`} value={menage.id} onChange={(e) => setMenageId(e.target.value)}>
          {menages.map((m) => (
            <option key={m.id} value={m.id}>
              {m.libelle}
            </option>
          ))}
        </select>
      </div>
      {avecIncidence && (
        <fieldset className="reglages">
          <legend>{texte("menages.effets.incidence.legende")}</legend>
          {(["comptable", "salaire"] as Incidence[]).map((i) => (
            <div key={i} className="interrupteur">
              <input
                id={`${id}-incidence-${i}`}
                type="radio"
                name={`${id}-incidence`}
                checked={incidence === i}
                onChange={() => setIncidence(i)}
              />
              <label htmlFor={`${id}-incidence-${i}`}>{texte(`menages.effets.incidence.${i}`)}</label>
            </div>
          ))}
          <span className="source">{texte("menages.effets.incidence.aide")}</span>
        </fieldset>
      )}
      <div aria-live="polite">
        {apres === null ? (
          <p className="avertissement">{texte("menages.effets.non_chiffre")}</p>
        ) : (
          <>
            {aucun && <p>{texte("menages.effets.aucun")}</p>}
            {lectures.length === 2 && (
              <p>
                {texte("menages.effets.incidence.fourchette", {
                  bas: ecartSigne.format(Math.min(...ecarts("net_apres_impot"))),
                  haut: ecartSigne.format(Math.max(...ecarts("net_apres_impot"))),
                  cout_bas: ecartSigne.format(Math.min(...ecarts("cout_employeur"))),
                  cout_haut: ecartSigne.format(Math.max(...ecarts("cout_employeur"))),
                })}
              </p>
            )}
            <div className="defilement" {...region(legende)}>
              <table>
                <caption>{legende}</caption>
                <thead>
                  <tr>
                    <th scope="col">{texte("menages.ligne")}</th>
                    <th scope="col">{texte("menages.effets.avant")}</th>
                    <th scope="col">{texte("menages.effets.apres")}</th>
                    <th scope="col">{texte("menages.effets.ecart")}</th>
                  </tr>
                </thead>
                <tbody>
                  {lignes.map((l) => (
                    <tr key={l.libelle}>
                      <th scope="row">{l.libelle}</th>
                      <td className="nombre">{euros.format(l.avant)}</td>
                      <td className="nombre">{euros.format(l.apres)}</td>
                      <td className="nombre">{ecartSigne.format(Math.round(l.ecart))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
      <p className="source">
        {texte("menages.sources")}{" "}
        {[
          ...new Set([
            ...(effets.leviers.find((l) => l.id === levier)?.sources ?? []),
            ...effets.sources,
          ]),
        ].map((s, i) => (
          <span key={s}>
            {i > 0 && ", "}
            <a href={`/sources/#${s}`}>{s}</a>
          </span>
        ))}
      </p>

      <h3>{texte("menages.effets.sans_effet_titre")}</h3>
      <p>{texte("menages.effets.sans_effet_intro")}</p>
      <ul>
        {[...new Set(Object.values(effets.sans_effet))].map((raison) => (
          <li key={raison}>{texte(`menages.effets.raisons.${raison}`)}</li>
        ))}
      </ul>
    </section>
  );
}
