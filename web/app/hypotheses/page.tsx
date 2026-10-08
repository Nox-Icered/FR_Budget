import { texte } from "../../lib/textes";
import { lire, type Hypothese } from "../../lib/donnees";

export default function Hypotheses() {
  const hypotheses = lire<Hypothese[]>("registre-hypotheses.json");
  return (
    <>
      <h1>{texte("hypotheses.titre")}</h1>
      <p>{texte("hypotheses.intro")}</p>
      <ul className="fiches">
        {hypotheses.map((h) => (
          <li key={h.id} id={h.id}>
            <h2>{h.libelle}</h2>
            <p>
              {texte("hypotheses.valeur_centrale")} : {h.valeur_centrale} ({h.unite})
            </p>
            <p>{texte("hypotheses.plage", { basse: h.plage.basse, haute: h.plage.haute })}</p>
            <p>
              {texte("hypotheses.justification")} : {h.justification}
            </p>
            <p>
              {texte("hypotheses.sources")} :{" "}
              {h.sources.map((s, i) => (
                <span key={s}>
                  {i > 0 && ", "}
                  <a href={`/sources/#${s}`}>{s}</a>
                </span>
              ))}
            </p>
          </li>
        ))}
      </ul>
    </>
  );
}
