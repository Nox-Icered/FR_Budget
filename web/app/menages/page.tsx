import { texte } from "../../lib/textes";
import { lire, type EffetsMenages, type MenagesTypes } from "../../lib/donnees";
import { EffetsLeviers } from "./effets";
import { region } from "../../lib/region";
import { lignesEnFourchette } from "../../lib/cascade";
import { chemin } from "../../lib/chemin";

const MOIS_PAR_AN = 12;
const euros = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });

export default function Menages() {
  const { menages, annee_revenus, sources } = lire<MenagesTypes>("menages-types.json");
  // Sans la grille exacte (simulateur) : seuls les effets d'une unité servent à la page.
  const { grille: _grille, controle: _controle, ...effetsTout } = lire<
    EffetsMenages & { grille?: unknown; controle?: unknown }
  >("menages-effets.json");
  const effets: EffetsMenages = {
    ...effetsTout,
    variantes: Object.fromEntries(
      Object.entries(effetsTout.variantes).map(([v, e]) => [
        v,
        { effets: e.effets, effets_salaire: e.effets_salaire },
      ]),
    ) as EffetsMenages["variantes"],
  };
  return (
    <>
      <h1>{texte("menages.titre")}</h1>
      <p className="avertissement" role="note">
        {texte("menages.bandeau")}
      </p>
      <p>{texte("menages.intro", { annee: annee_revenus })}</p>
      <p>{texte("menages.fourchette_aide")}</p>
      {menages.map((m) => {
        const lignes = lignesEnFourchette(m, [m.variantes.bas, m.variantes.haut]);
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
                    <th scope="col">{texte("menages.fourchette")}</th>
                  </tr>
                </thead>
                <tbody>
                  {lignes.map((l) => (
                    <tr key={l.libelle}>
                      <th scope="row">{l.libelle}</th>
                      <td className="nombre">{euros.format(l.valeur)}</td>
                      <td className="nombre">{euros.format(l.valeur / MOIS_PAR_AN)}</td>
                      <td className="nombre">
                        {texte("menages.de_a", { bas: euros.format(l.bas), haut: euros.format(l.haut) })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        );
      })}
      <EffetsLeviers effets={effets} menages={menages} />
      <p className="source">{texte("menages.limites")}</p>
      <p className="source">
        {texte("menages.sources")}{" "}
        {sources.map((s, i) => (
          <span key={s}>
            {i > 0 && ", "}
            <a href={chemin(`/sources/#${s}`)}>{s}</a>
          </span>
        ))}
      </p>
      <p className="source">{texte("menages.lien_fiche")}</p>
    </>
  );
}
