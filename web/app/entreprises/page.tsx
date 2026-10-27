import { texte } from "../../lib/textes";
import { lire, type Entreprises } from "../../lib/donnees";
import { region } from "../../lib/region";
import { TableauxEntreprises } from "./tableaux";
import { chemin } from "../../lib/chemin";

const pourcent = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1, signDisplay: "exceptZero" });
const deux = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2, minimumFractionDigits: 2 });
const POURCENT = 100;

export default function PageEntreprises() {
  const donnees = lire<Entreprises>("entreprises.json");
  const titreControles = texte("entreprises.controles_titre");
  return (
    <>
      <h1>{texte("entreprises.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("entreprises.bandeau")}
      </p>
      <p>
        {texte("entreprises.intro", {
          annee_urssaf: donnees.annee_urssaf,
          annee_is: donnees.annees_is[0],
          annee_is_2: donnees.annees_is[1],
        })}
      </p>
      <TableauxEntreprises donnees={donnees} />
      <h2>{titreControles}</h2>
      <p>{texte("entreprises.controles_intro")}</p>
      <div className="defilement" {...region(titreControles)}>
        <table>
          <thead>
            <tr>
              <th scope="col">{texte("entreprises.controle")}</th>
              <th scope="col">{texte("entreprises.urssaf")}</th>
              <th scope="col">{texte("entreprises.ccss")}</th>
              <th scope="col">{texte("entreprises.ecart")}</th>
            </tr>
          </thead>
          <tbody>
            {donnees.controles.map((c) => (
              <tr key={c.id}>
                <th scope="row">
                  {texte(`entreprises.controles.${c.id.startsWith("point") ? "point" : c.id}`, {
                    annee: c.annee,
                  })}{" "}
                  (<a href={chemin(`/sources/#${c.source}`)}>{c.source}</a>)
                </th>
                <td className="nombre">{deux.format(c.urssaf)}</td>
                <td className="nombre">{deux.format(c.reference)}</td>
                <td className="nombre">{pourcent.format(c.ecart * POURCENT)} %</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="source">{texte("entreprises.limites")}</p>
      <p className="source">{texte("entreprises.licence")}</p>
      <p className="source">{texte("entreprises.lien_fiche")}</p>
    </>
  );
}
