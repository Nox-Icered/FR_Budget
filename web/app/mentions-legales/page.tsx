import { texte } from "../../lib/textes";

const DEPOT = "https://github.com/Nox-Icered/FR_Budget";

export default function MentionsLegales() {
  const sections = ["editeur", "hebergement", "code", "donnees", "responsabilite"] as const;
  return (
    <>
      <h1>{texte("mentions.titre")}</h1>
      {sections.map((s) => (
        <section key={s}>
          <h2>{texte(`mentions.${s}_titre`)}</h2>
          <p>{texte(`mentions.${s}`)}</p>
          {s === "code" && (
            <p>
              <a href={DEPOT} rel="noopener">
                {texte("mentions.depot")}
              </a>
            </p>
          )}
        </section>
      ))}
    </>
  );
}
