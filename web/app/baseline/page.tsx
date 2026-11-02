import { texte, nombre } from "../../lib/textes";
import { lire, type Baseline } from "../../lib/donnees";
import { GraphiqueDette } from "./graphique";
import { region } from "../../lib/region";
import { chemin } from "../../lib/chemin";

export default function PageBaseline() {
  const b = lire<Baseline>("baseline.json");
  const c = b.commission;
  const publiee = c.valeurs.find((v) => v.annee === c.derniere_annee_publiee)!;
  const suivante = c.valeurs.find((v) => v.annee === c.derniere_annee_publiee + 1);
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
        legende={texte("baseline.legende_gouvernement", { raccord: b.annee_raccord })}
        comparaison={{
          libelle: texte("baseline.commission"),
          prolongement: texte("baseline.commission_prolongement", { annee: c.derniere_annee_publiee }),
          points: c.valeurs.map((v) => ({ annee: v.annee, publiee: v.publiee, ...v.dette })),
        }}
        libelles={{
          titre: texte("baseline.graphique_titre"),
          bas: texte("baseline.bas"),
          central: texte("baseline.central"),
          haut: texte("baseline.haut"),
          raccord: texte("baseline.graphique_raccord"),
          unite: texte("baseline.graphique_lecture"),
        }}
      />
      <h2>{texte("baseline.commission_titre")}</h2>
      <p>
        {texte("baseline.commission_texte", {
          annee: c.derniere_annee_publiee,
          pente: nombre(suivante ? suivante.dette.central - publiee.dette.central : 0),
          haut: nombre(publiee.dette.haut),
        })}
      </p>
      <div className="defilement" {...region(texte("baseline.commission_titre"))}>
        <table>
          <thead>
            <tr>
              <th scope="col">{texte("baseline.annee")}</th>
              <th scope="col">{texte("baseline.bas")}</th>
              <th scope="col">{texte("baseline.central")}</th>
              <th scope="col">{texte("baseline.haut")}</th>
              <th scope="col">{texte("baseline.commission_statut")}</th>
            </tr>
          </thead>
          <tbody>
            {c.valeurs.map((v) => (
              <tr key={v.annee}>
                <th scope="row">{v.annee}</th>
                <td className="nombre">{nombre(v.dette.bas)}</td>
                <td className="nombre">{nombre(v.dette.central)}</td>
                <td className="nombre">{nombre(v.dette.haut)}</td>
                <td>
                  {texte(v.publiee ? "baseline.commission_publiee" : "baseline.commission_prolongee")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="source">
        <a href={chemin(`/sources/#${c.source}`)}>{texte("accueil.source", { source: c.source })}</a>
        {c.hypotheses.map((h) => (
          <span key={h}>
            {" ; "}
            <a href={chemin(`/hypotheses/#${h}`)}>{h}</a>
          </span>
        ))}
      </p>
      <h2>{texte("baseline.gouvernement_titre")}</h2>
      <div className="defilement" {...region(texte("baseline.gouvernement_titre"))}>
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
            <a href={chemin(`/hypotheses/#${h}`)}>{h}</a>
          </li>
        ))}
      </ul>
      <p className="source">
        {b.sources.map((s, i) => (
          <span key={s}>
            {i > 0 && " ; "}
            <a href={chemin(`/sources/#${s}`)}>{texte("accueil.source", { source: s })}</a>
          </span>
        ))}
      </p>
    </>
  );
}
