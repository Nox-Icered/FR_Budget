"use client";
// Effet d'une mesure sur un ménage type : cascade avant et après, écart ligne par ligne.
// Données exportées par l'API (menages-effets.json) ; rien n'est saisi ni envoyé.
import { useId, useState } from "react";
import { texte } from "../../lib/textes";
import { lignesComparees } from "../../lib/cascade";
import { region } from "../../lib/region";
import type { EffetsMenages, MenageType } from "../../lib/donnees";

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
  const { levier, sens } = options[choix];
  const menage = menages.find((m) => m.id === menageId) ?? menages[0];
  const apres = effets.effets[levier][sens][menage.id];
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
      <div aria-live="polite">
        {apres === null ? (
          <p className="avertissement">{texte("menages.effets.non_chiffre")}</p>
        ) : (
          <>
            {aucun && <p>{texte("menages.effets.aucun")}</p>}
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
      {levier === "cotisations_patronales_taux" && (
        <p className="source">{texte("menages.effets.incidence")}</p>
      )}
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
