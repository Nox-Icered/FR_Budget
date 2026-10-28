import { texte, nombre } from "../../lib/textes";
import { lire, type Chiffrage, type Comparaison, type Levier } from "../../lib/donnees";
import { region } from "../../lib/region";
import { chemin } from "../../lib/chemin";
import { libelleCommun } from "../../lib/validation";


// Confrontations d'un levier à des sources indépendantes de l'administration (règle de
// publication) : nombre de références et nombre dans la tolérance.
function confrontation(comparaisons: Comparaison[], levier: string): string {
  const liste = comparaisons.filter((c) => c.independante && c.levier === levier);
  if (liste.length === 0) return texte("validation.independante_aucune");
  return texte("validation.independante_resultat", {
    dans: liste.filter((c) => c.dans_la_tolerance).length,
    total: liste.length,
  });
}

export default function Validation() {
  const leviers = lire<Levier[]>("registre-leviers.json");
  const chiffrages = lire<Chiffrage[]>("registre-chiffrages.json");
  const comparaisons = lire<Comparaison[]>("validation.json");
  const mesures = new Map(chiffrages.map((c) => [c.id, c]));
  const tolerance = comparaisons.length ? comparaisons[0].tolerance * 100 : 0;
  return (
    <>
      <h1>{texte("validation.titre")}</h1>
      <p>{texte("validation.intro")}</p>
      <div className="defilement" {...region(texte("validation.titre"))}>
        <table>
        <thead>
          <tr>
            <th scope="col">{texte("validation.levier")}</th>
            <th scope="col">{texte("validation.statut")}</th>
            <th scope="col">{texte("validation.independante")}</th>
          </tr>
        </thead>
        <tbody>
          {leviers.map((l) => (
            <tr key={l.id}>
              <td>{l.libelle}</td>
              <td>{texte(`validation.statuts.${l.statut}`)}</td>
              <td>{confrontation(comparaisons, l.id)}</td>
            </tr>
          ))}
        </tbody>
      </table>
        </div>
      <h2>{texte("validation.comparaisons_titre")}</h2>
      <p>{texte("validation.comparaisons_intro", { tolerance: nombre(tolerance) })}</p>
      <div className="defilement" {...region(texte("validation.comparaisons_titre"))}>
        <table>
          <thead>
            <tr>
              <th scope="col">{texte("validation.reference")}</th>
              <th scope="col">{texte("validation.modele")}</th>
              <th scope="col">{texte("validation.valeur")}</th>
              <th scope="col">{texte("validation.ecart")}</th>
              <th scope="col">{texte("validation.resultat")}</th>
            </tr>
          </thead>
          <tbody>
            {comparaisons.map((c) => (
              <tr key={`${c.reference}-${c.variante ?? ""}`}>
                <td>
                  {c.reference_haute
                    ? texte("validation.fourchette_libelle", {
                        mesure: libelleCommun(
                          mesures.get(c.reference)?.mesure ?? c.reference,
                          mesures.get(c.reference_haute)?.mesure ?? c.reference_haute,
                        ),
                      })
                    : (mesures.get(c.reference)?.mesure ?? c.reference)}
                  {c.variante ? ` — ${texte(`validation.variantes.${c.variante}`)}` : ""}
                  {c.independante ? ` — ${texte("validation.source_independante")}` : ""}
                </td>
                <td className="nombre">
                  {nombre(c.modele)} {c.unite}
                </td>
                <td className="nombre">
                  {c.valeur_haute != null
                    ? texte("validation.fourchette_valeur", {
                        bas: nombre(c.valeur_reference),
                        haut: nombre(c.valeur_haute),
                      })
                    : nombre(c.valeur_reference)}{" "}
                  {c.unite}
                </td>
                <td className="nombre">{texte("validation.pourcent", { valeur: nombre(c.ecart * 100) })}</td>
                <td>{texte(c.dans_la_tolerance ? "validation.dans_tolerance" : "validation.hors_tolerance")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h2>{texte("validation.references_titre")}</h2>
      <div className="defilement" {...region(texte("validation.references_titre"))}>
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
                {c.mesure} ({c.millesime}) — <a href={chemin(`/sources/#${c.source}`)}>{c.source}</a>, {c.localisation}
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
