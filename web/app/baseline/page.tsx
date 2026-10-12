import { texte, nombre } from "../../lib/textes";
import { lire, type Baseline } from "../../lib/donnees";
import { GraphiqueDette } from "./graphique";
import { REGION } from "../../lib/region";

export default function PageBaseline() {
  const b = lire<Baseline>("baseline.json");
  return (
    <>
      <h1>{texte("baseline.titre")}</h1>
      {b.statut !== "valide" && (
        <p className="avertissement" role="note">
          {texte("baseline.bandeau")}
        </p>
      )}
      <p>{texte("baseline.intro", { raccord: b.annee_raccord })}</p>
      <GraphiqueDette
        points={b.valeurs.map((v) => ({ annee: v.annee, ...v.dette }))}
        raccord={b.annee_raccord}
        libelles={{
          titre: texte("baseline.graphique_titre"),
          bas: texte("baseline.bas"),
          central: texte("baseline.central"),
          haut: texte("baseline.haut"),
          raccord: texte("baseline.graphique_raccord"),
          unite: texte("baseline.graphique_lecture"),
        }}
      />
      <div className="defilement" {...REGION}>
        <table>
          <thead>
            <tr>
              <th scope="col" rowSpan={2}>{texte("baseline.annee")}</th>
              <th scope="colgroup" colSpan={3}>{texte("baseline.dette")}</th>
              <th scope="colgroup" colSpan={3}>{texte("baseline.solde_primaire")}</th>
            </tr>
            <tr>
              <th scope="col">{texte("baseline.bas")}</th>
              <th scope="col">{texte("baseline.central")}</th>
              <th scope="col">{texte("baseline.haut")}</th>
              <th scope="col">{texte("baseline.bas")}</th>
              <th scope="col">{texte("baseline.central")}</th>
              <th scope="col">{texte("baseline.haut")}</th>
            </tr>
          </thead>
          {(["resf", "projection"] as const).map((segment) => (
            <tbody key={segment}>
              <tr>
                <th scope="rowgroup" colSpan={7} className="groupe">
                  {texte(`baseline.segments.${segment}`)}
                </th>
              </tr>
              {b.valeurs
                .filter((v) => v.segment === segment)
                .map((v) => (
                  <tr key={v.annee}>
                    <th scope="row">{v.annee}</th>
                    <td className="nombre">{nombre(v.dette.bas)}</td>
                    <td className="nombre">{nombre(v.dette.central)}</td>
                    <td className="nombre">{nombre(v.dette.haut)}</td>
                    <td className="nombre">{nombre(v.solde_primaire.bas)}</td>
                    <td className="nombre">{nombre(v.solde_primaire.central)}</td>
                    <td className="nombre">{nombre(v.solde_primaire.haut)}</td>
                  </tr>
                ))}
            </tbody>
          ))}
        </table>
      </div>
      <p className="source">{texte("baseline.unite", { unite: b.unite })}</p>
      <h2>{texte("baseline.methode_titre")}</h2>
      <p>{texte("baseline.methode")}</p>
      <h2>{texte("baseline.hypotheses_titre")}</h2>
      <ul>
        {b.hypotheses.map((h) => (
          <li key={h}>
            <a href={`/hypotheses/#${h}`}>{h}</a>
          </li>
        ))}
      </ul>
      <p className="source">
        {b.sources.map((s, i) => (
          <span key={s}>
            {i > 0 && " ; "}
            <a href={`/sources/#${s}`}>{texte("accueil.source", { source: s })}</a>
          </span>
        ))}
      </p>
    </>
  );
}
