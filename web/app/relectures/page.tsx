import { texte } from "../../lib/textes";
import { lire, type Chiffrage, type Levier, type Relecture } from "../../lib/donnees";

export default function Relectures() {
  const relectures = lire<Relecture[]>("registre-relectures.json");
  const chiffrages = lire<Chiffrage[]>("registre-chiffrages.json");
  const leviers = lire<Levier[]>("registre-leviers.json");
  const relues = chiffrages.filter((c) => c.relecture === "relu").length;
  const compte = (statut: Levier["statut"]) => leviers.filter((l) => l.statut === statut).length;
  return (
    <>
      <h1>{texte("relectures.titre")}</h1>
      <p>{texte("relectures.intro")}</p>
      {relectures.length === 0 ? (
        <p>{texte("relectures.aucune")}</p>
      ) : (
        <ul className="fiches">
          {relectures.map((r) => (
            <li key={r.id} id={r.id}>
              <h2>
                {r.relecteur} · {r.date}
              </h2>
              <p>
                {texte("relectures.objet")} : {r.objet.join(", ")}
              </p>
              <p>
                {texte("relectures.retour")} : {r.retour}
              </p>
              <p>
                {texte("relectures.reponse")} : {r.reponse}
              </p>
              {r.lien && (
                <p>
                  <a href={r.lien} rel="noopener">
                    {texte("relectures.lien")}
                  </a>
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
      <h2>{texte("relectures.valeurs_titre")}</h2>
      <p>
        {texte("relectures.valeurs", {
          total: chiffrages.length,
          relues,
          a_relire: chiffrages.length - relues,
        })}
      </p>
      <p>
        {texte("relectures.leviers", {
          valides: compte("valide"),
          beta: compte("beta"),
          non_publies: compte("non_publie"),
        })}
      </p>
    </>
  );
}
