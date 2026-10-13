import { texte } from "../../lib/textes";
import { lire, type MenagesTypes } from "../../lib/donnees";
import { region } from "../../lib/region";

const MOIS_PAR_AN = 12;
const euros = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });

export default function Menages() {
  const { menages, annee_revenus, sources } = lire<MenagesTypes>("menages-types.json");
  return (
    <>
      <h1>{texte("menages.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("menages.bandeau")}
      </p>
      <p>{texte("menages.intro", { annee: annee_revenus })}</p>
      {menages.map((m) => {
        // Lignes du salaire pour un ménage qui en a un, de la pension pour un retraité.
        const salaire: [string, number][] =
          m.salaire_brut > 0
            ? [
                [texte("menages.cout_employeur"), m.cout_employeur],
                [texte("menages.salaire_brut"), m.salaire_brut],
                [texte("menages.net_avant_impot"), m.net_avant_impot],
              ]
            : [];
        const pension: [string, number][] =
          m.pension_brute > 0
            ? [
                [texte("menages.pension_brute"), m.pension_brute],
                [texte("menages.pension_nette"), m.pension_nette],
              ]
            : [];
        const lignes: [string, number][] = [
          ...salaire,
          ...pension,
          [texte("menages.impot_revenu"), -m.impot_revenu],
          ...Object.entries(m.prestations).map(
            ([cle, v]): [string, number] => [texte(`menages.prestations.${cle}`), v],
          ),
          [texte("menages.net_apres_impot"), m.net_apres_impot],
        ];
        return (
          <section key={m.id} id={m.id}>
            <h2>{m.libelle}</h2>
            <div className="defilement" {...region(m.libelle)}>
              <table>
                <thead>
                  <tr>
                    <th scope="col">{texte("menages.ligne")}</th>
                    <th scope="col">{texte("menages.an")}</th>
                    <th scope="col">{texte("menages.mois")}</th>
                  </tr>
                </thead>
                <tbody>
                  {lignes.map(([libelle, v]) => (
                    <tr key={libelle}>
                      <th scope="row">{libelle}</th>
                      <td className="nombre">{euros.format(v)}</td>
                      <td className="nombre">{euros.format(v / MOIS_PAR_AN)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        );
      })}
      <p className="source">{texte("menages.limites")}</p>
      <p className="source">
        {texte("menages.sources")}{" "}
        {sources.map((s, i) => (
          <span key={s}>
            {i > 0 && ", "}
            <a href={`/sources/#${s}`}>{s}</a>
          </span>
        ))}
      </p>
      <p className="source">{texte("menages.lien_fiche")}</p>
    </>
  );
}
