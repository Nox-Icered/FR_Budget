"use client";
// Variation du revenu des ménages par dixième de niveau de vie sous les mesures du scénario
// (lib/deciles.ts).
import { texte } from "../../lib/textes";
import { region } from "../../lib/region";
import { repartitionDeciles } from "../../lib/deciles";
import type { Deciles } from "../../lib/donnees";
import type { Fourchette, MesureSite } from "../../lib/scenario";

const entier = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0, signDisplay: "exceptZero" });
const pourcent = new Intl.NumberFormat("fr-FR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  signDisplay: "exceptZero",
});

function fourchette(f: Fourchette, format: (v: number) => string): string {
  const [b, c, h] = [f.bas, f.central, f.haut].map(format);
  return b === h ? c : texte("entreprises.fourchette", { central: c, bas: b, haut: h });
}

export function DecilesScenario({ donnees, mesures }: { donnees: Deciles; mesures: MesureSite[] }) {
  const r = repartitionDeciles(donnees, mesures);
  const legende = texte("simulateur.deciles.legende");
  return (
    <section>
      <h2>{texte("simulateur.deciles.titre")}</h2>
      <p className="avertissement" role="note">
        {texte("simulateur.deciles.bandeau")}
      </p>
      {r === null ? (
        <p>{texte("simulateur.deciles.aucune")}</p>
      ) : (
        <>
          <p>{texte("simulateur.deciles.intro", { annee: donnees.annee_effets })}</p>
          <div className="defilement" {...region(legende)}>
            <table>
              <caption>{legende}</caption>
              <thead>
                <tr>
                  <th scope="col">{texte("simulateur.deciles.dixieme")}</th>
                  <th scope="col">{texte("simulateur.deciles.euros")}</th>
                  <th scope="col">{texte("simulateur.deciles.part")}</th>
                </tr>
              </thead>
              <tbody>
                {r.eurosParUc.map((f, i) => (
                  <tr key={i}>
                    <th scope="row">{texte(`simulateur.deciles.noms.${i + 1}`)}</th>
                    <td className="nombre">{fourchette(f, (v) => entier.format(Math.round(v)))}</td>
                    <td className="nombre">
                      {fourchette(r.pourcentRevenu[i], (v) => `${pourcent.format(v)} %`)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {r.nonRepartis.length > 0 && (
            <p className="source">{texte("simulateur.deciles.non_repartis", { nombre: r.nonRepartis.length })}</p>
          )}
        </>
      )}
      <p className="source">
        {texte("simulateur.deciles.methode", {
          annee: donnees.annee_comptes,
          premiere: donnees.annees_variantes[0],
        })}
      </p>
    </section>
  );
}
