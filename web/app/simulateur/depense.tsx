"use client";
// Dépense supplémentaire des ménages à consommation inchangée sous les mesures de TVA et
// d'accises du scénario, par décile de niveau de vie et par type de ménage
// (lib/depense-menages.ts).
import { texte } from "../../lib/textes";
import { region } from "../../lib/region";
import { effetDepense } from "../../lib/depense-menages";
import type { DepenseMenages, FourchetteDonnee } from "../../lib/donnees";

const entier = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const pourcent = new Intl.NumberFormat("fr-FR", {
  style: "percent",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function fourchette(f: FourchetteDonnee, format: (v: number) => string): string {
  const [b, c, h] = [f.bas, f.central, f.haut].map(format);
  return b === h ? c : texte("entreprises.fourchette", { central: c, bas: b, haut: h });
}

const NOMENCLATURES = ["decile", "type_menage"] as const;

export function DepenseMenagesScenario({
  donnees,
  valeurs,
}: {
  donnees: DepenseMenages;
  valeurs: Record<string, number>;
}) {
  const tableaux = NOMENCLATURES.map((n) => ({ n, lignes: effetDepense(donnees, n, valeurs) }));
  const actif = tableaux.some((t) => t.lignes !== null);
  return (
    <section>
      <h2>{texte("simulateur.depense.titre")}</h2>
      {!actif ? (
        <p>{texte("simulateur.depense.aucune")}</p>
      ) : (
        <>
          <p>{texte("simulateur.depense.intro", { annee: donnees.annee })}</p>
          {tableaux.map(({ n, lignes }) => {
            const legende = texte(`simulateur.depense.legendes.${n}`);
            return (
              <div key={n} className="defilement" {...region(legende)}>
                <table>
                  <caption>{legende}</caption>
                  <thead>
                    <tr>
                      <th scope="col">{texte("simulateur.depense.classe")}</th>
                      <th scope="col">{texte("simulateur.depense.effet")}</th>
                      <th scope="col">{texte("simulateur.depense.part")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(lignes ?? []).map(({ classe, effet, part }) => (
                      <tr key={classe.id}>
                        <th scope="row">{texte(`simulateur.depense.classes.${n}.${classe.id}`)}</th>
                        <td className="nombre">
                          {fourchette(effet, (v) => entier.format(Math.round(v)))}
                        </td>
                        <td className="nombre">{fourchette(part, (v) => pourcent.format(v))}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          })}
        </>
      )}
      <p className="source">
        {texte("simulateur.depense.methode", {
          annee: donnees.annee,
          annee_enquete: donnees.annee_enquete,
        })}
      </p>
      {donnees.controles.map((c) => (
        <p key={c.annee} className="source">
          {texte("simulateur.depense.controle", {
            modele: pourcent.format(c.modele.central),
            reference: pourcent.format(c.reference),
            annee_controle: c.annee,
            ecart: pourcent.format(c.ecart),
          })}
        </p>
      ))}
      <p className="source">{texte("simulateur.depense.detail")}</p>
    </section>
  );
}
