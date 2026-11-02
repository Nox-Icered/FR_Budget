// Diagramme de Sankey du budget de l'État (projet de loi de finances) : d'où vient l'argent
// (impôts, autres recettes, emprunt pour couvrir le déficit) et où il va (collectivités, Union
// européenne, missions). Dessin statique ; le tableau qui suit donne tous les montants.
import { texte, nombre } from "../lib/textes";
import type { BudgetEtat } from "../lib/donnees";
import { bande, miseEnPage, regrouper, type Flux } from "../lib/sankey";
import { region } from "../lib/region";
import { chemin } from "../lib/chemin";

const L = 1140;
const H = 620;
const ECART = 7;
const LARGEUR_NOEUD = 14;
const X_GAUCHE = 240;
const X_CENTRE = 450;
const X_DROITE = 660;
const SEUIL_AUTRES = 0.02;

function libelle(f: { id: string; libelle: string | null }): string {
  return f.libelle ?? texte(`accueil.budget_etat.postes.${f.id}`);
}

export function BudgetEtatSankey({ budget }: { budget: BudgetEtat }) {
  const ressources: Flux[] = budget.ressources.map((f) => ({ ...f, libelle: libelle(f) }));
  const emplois = regrouper(
    budget.emplois.map((f) => ({ ...f, libelle: libelle(f) })),
    SEUIL_AUTRES,
    (n) => texte("accueil.budget_etat.autres_missions", { nombre: n }),
  );
  const m = miseEnPage(ressources, emplois, H - 20, ECART);
  const montant = (v: number) => texte("accueil.milliards", { valeur: nombre(v) });
  const classe = (id: string) => (id === "deficit" ? "flux-deficit" : "flux-recette");
  const titre = texte("accueil.budget_etat.titre", { annee: budget.annee });
  return (
    <section>
      <h2>{titre}</h2>
      <p>{texte("accueil.budget_etat.intro", { total: nombre(m.total) })}</p>
      <div className="defilement sankey" {...region(titre)}>
        <svg viewBox={`0 0 ${L} ${H}`} role="img" aria-label={texte("accueil.budget_etat.aria")}>
          <g transform="translate(0,10)">
            {m.liensGauche.map((l) => (
              <path
                key={l.source.id}
                d={bande(X_GAUCHE + LARGEUR_NOEUD, X_CENTRE, l.y0, l.y1, l.epaisseur)}
                className={`lien ${classe(l.source.id)}`}
              >
                <title>{`${l.source.libelle} : ${montant(l.source.montant)}`}</title>
              </path>
            ))}
            {m.liensDroite.map((l) => (
              <path
                key={l.cible.id}
                d={bande(X_CENTRE + LARGEUR_NOEUD, X_DROITE, l.y0, l.y1, l.epaisseur)}
                className="lien flux-emploi"
              >
                <title>{`${l.cible.libelle} : ${montant(l.cible.montant)}`}</title>
              </path>
            ))}
            {m.gauche.map((n) => (
              <g key={n.id}>
                <rect x={X_GAUCHE} y={n.y} width={LARGEUR_NOEUD} height={n.hauteur} className={`noeud ${classe(n.id)}`} />
                <text x={X_GAUCHE - 8} y={n.y + n.hauteur / 2} textAnchor="end" dominantBaseline="middle" className="etiquette-sankey">
                  {n.libelle} · {nombre(n.montant)}
                </text>
              </g>
            ))}
            <rect x={X_CENTRE} y={m.centre.y} width={LARGEUR_NOEUD} height={m.centre.hauteur} className="noeud noeud-centre" />
            {m.droite.map((n) => (
              <g key={n.id}>
                <rect x={X_DROITE} y={n.y} width={LARGEUR_NOEUD} height={n.hauteur} className="noeud flux-emploi" />
                <text x={X_DROITE + LARGEUR_NOEUD + 8} y={n.y + n.hauteur / 2} dominantBaseline="middle" className="etiquette-sankey">
                  {n.libelle} · {nombre(n.montant)}
                </text>
              </g>
            ))}
          </g>
        </svg>
      </div>
      <p className="source">{texte("accueil.budget_etat.lecture")}</p>
      <details className="explication">
        <summary>{texte("accueil.budget_etat.tableau")}</summary>
        <div className="defilement" {...region(texte("accueil.budget_etat.tableau"))}>
          <table>
            <thead>
              <tr>
                <th scope="col">{texte("accueil.budget_etat.poste")}</th>
                <th scope="col">{texte("accueil.montant")}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="rowgroup" colSpan={2} className="groupe">
                  {texte("accueil.budget_etat.ressources")}
                </th>
              </tr>
              {ressources.map((f) => (
                <tr key={f.id}>
                  <th scope="row">{f.libelle}</th>
                  <td className="nombre">{montant(f.montant)}</td>
                </tr>
              ))}
              <tr>
                <th scope="rowgroup" colSpan={2} className="groupe">
                  {texte("accueil.budget_etat.emplois")}
                </th>
              </tr>
              {budget.emplois.map((f) => (
                <tr key={f.id}>
                  <th scope="row">{libelle(f)}</th>
                  <td className="nombre">{montant(f.montant)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
      <p className="source">
        {budget.sources.map((s, i) => (
          <span key={s}>
            {i > 0 && " ; "}
            <a href={chemin(`/sources/#${s}`)}>{texte("accueil.source", { source: s })}</a>
          </span>
        ))}
      </p>
    </section>
  );
}
