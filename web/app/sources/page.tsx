import { texte } from "../../lib/textes";
import { lire, type Source } from "../../lib/donnees";

export default function Sources() {
  const sources = lire<Source[]>("registre-sources.json");
  return (
    <>
      <h1>{texte("sources.titre")}</h1>
      <p>{texte("sources.intro")}</p>
      <ul className="fiches">
        {sources.map((s) => (
          <li key={s.id} id={s.id}>
            <h2>{s.nom}</h2>
            <p>
              {texte("sources.editeur")} : {s.editeur}
              {s.millesime && (
                <>
                  {" · "}
                  {texte("sources.millesime")} : {s.millesime}
                </>
              )}
            </p>
            <p>
              {texte("sources.licence")} : {s.licence}
            </p>
            <p>
              {texte("sources.consulte_le", { date: s.consulte_le })} ·{" "}
              <a href={s.url} rel="noopener">
                {texte("sources.lien")}
              </a>
            </p>
          </li>
        ))}
      </ul>
    </>
  );
}
