import { texte } from "../../lib/textes";
import { lire, type LigneJournal } from "../../lib/donnees";

export default function Journal() {
  const lignes = lire<LigneJournal[]>("journal.json");
  return (
    <>
      <h1>{texte("journal.titre")}</h1>
      <p>{texte("journal.intro")}</p>
      <ul className="fiches">
        {lignes.map((l, i) => (
          <li key={`${l.fiche}-${i}`}>
            <p>
              <strong>{l.date}</strong> · {l.titre}
            </p>
            <p>{l.changement}</p>
            <p className="source">
              {texte("journal.tests")} : {l.tests}
            </p>
          </li>
        ))}
      </ul>
    </>
  );
}
