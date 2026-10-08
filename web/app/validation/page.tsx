import { texte } from "../../lib/textes";
import { lire, type Chiffrage, type Levier } from "../../lib/donnees";

export default function Validation() {
  const leviers = lire<Levier[]>("registre-leviers.json");
  const chiffrages = lire<Chiffrage[]>("registre-chiffrages.json");
  return (
    <>
      <h1>{texte("validation.titre")}</h1>
      <p>{texte("validation.intro")}</p>
      <div className="defilement">
        <table>
        <thead>
          <tr>
            <th scope="col">{texte("validation.levier")}</th>
            <th scope="col">{texte("validation.statut")}</th>
          </tr>
        </thead>
        <tbody>
          {leviers.map((l) => (
            <tr key={l.id}>
              <td>{l.libelle}</td>
              <td>{texte(`validation.statuts.${l.statut}`)}</td>
            </tr>
          ))}
        </tbody>
      </table>
        </div>
      <h2>{texte("validation.references_titre")}</h2>
      <div className="defilement">
        <table>
        <thead>
          <tr>
            <th scope="col">{texte("validation.reference")}</th>
            <th scope="col">{texte("validation.valeur")}</th>
            <th scope="col">{texte("validation.relecture")}</th>
          </tr>
        </thead>
        <tbody>
          {chiffrages.map((c) => (
            <tr key={c.id}>
              <td>
                {c.mesure} ({c.millesime}) — <a href={`/sources/#${c.source}`}>{c.source}</a>, {c.localisation}
              </td>
              <td className="nombre">
                {c.valeur} {c.unite}
              </td>
              <td>{texte(`validation.relectures.${c.relecture}`)}</td>
            </tr>
          ))}
        </tbody>
      </table>
        </div>
    </>
  );
}
