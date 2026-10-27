import { texte, nombre } from "../lib/textes";
import { lire, type ComptesApu, type Cofog } from "../lib/donnees";
import { region } from "../lib/region";
import { chemin } from "../lib/chemin";


export default function Accueil() {
  const comptes = lire<ComptesApu>("comptes-apu.json");
  const cofog = lire<Cofog>("cofog.json");
  const { sous_secteurs, indicateurs, series } = comptes;
  const derniere = Math.max(...series.S13.dette_maastricht.valeurs.map((p) => p.annee));
  const divisions = cofog.valeurs.filter((v) => /^GF\d{2}$/.test(v.cofog));

  return (
    <>
      <h1>{texte("accueil.titre")}</h1>
      <p>{texte("accueil.intro")}</p>
      <h2>{texte("accueil.annee", { annee: derniere })}</h2>
      {sous_secteurs.map((secteur) => (
        <section key={secteur}>
          <h3>{texte(`accueil.sous_secteurs.${secteur}`)}</h3>
          <dl className="chiffres">
            {indicateurs.map((indicateur) => {
              const point = series[secteur][indicateur].valeurs.find((p) => p.annee === derniere);
              if (!point) return null;
              return (
                <div key={indicateur}>
                  <dt>{texte(`accueil.indicateurs.${indicateur}`)}</dt>
                  <dd>
                    {texte("accueil.milliards", { valeur: nombre(point.valeur) })}
                    {point.pourcent_pib !== undefined && (
                      <span className="secondaire">
                        {texte("accueil.pourcent_pib", { valeur: nombre(point.pourcent_pib) })}
                      </span>
                    )}
                  </dd>
                </div>
              );
            })}
          </dl>
          <p className="source">
            <a href={chemin(`/sources/#${series[secteur].dette_maastricht.source}`)}>
              {texte("accueil.source", { source: series[secteur].dette_maastricht.source })}
            </a>
          </p>
        </section>
      ))}
      <section>
        <h2>{texte("accueil.fonctions_titre", { annee: cofog.annee })}</h2>
        <div className="defilement" {...region(texte("accueil.fonctions_titre", { annee: cofog.annee }))}>
        <table>
          <thead>
            <tr>
              <th scope="col">{texte("accueil.fonction")}</th>
              <th scope="col">{texte("accueil.montant")}</th>
            </tr>
          </thead>
          <tbody>
            {divisions.map((v) => (
              <tr key={v.cofog}>
                <td>{v.libelle}</td>
                <td className="nombre">{texte("accueil.milliards", { valeur: nombre(v.valeur) })}</td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
        <p className="source">
          <a href={chemin(`/sources/#${cofog.source}`)}>{texte("accueil.source", { source: cofog.source })}</a>
        </p>
        <p className="source">{texte("accueil.mention_eurostat")}</p>
      </section>
    </>
  );
}
