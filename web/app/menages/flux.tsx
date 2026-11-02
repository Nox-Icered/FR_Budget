// Où va l'écart entre le coût employeur et le revenu après impôt d'un ménage type : un
// diagramme de Sankey par étape (employeur, salarié, retraite, indépendant, impôt), à la même
// échelle pour un ménage. Dessin statique ; le tableau qui suit donne tous les montants.
import { texte } from "../../lib/textes";
import type { EtapeFlux } from "../../lib/donnees";
import { bande, espacer, miseEnPage, regrouper, type Flux } from "../../lib/sankey";
import { region } from "../../lib/region";

const L = 1140;
const H_MAX = 420;
const H_MIN = 90;
const MARGE = 20;
const ECART = 8;
const LARGEUR_NOEUD = 14;
const X_GAUCHE = 330;
const X_CENTRE = 560;
const X_DROITE = 790;
const ESPACE_ETIQUETTES = 16;
const SEUIL_AUTRES = 0.02;
// Montants qui passent d'une étape à la suivante (revenus du ménage), mis en avant.
const PASSAGES = new Set([
  "cout_employeur",
  "salaire_brut",
  "net_avant_impot",
  "pension_brute",
  "pension_nette",
  "revenu_independant_brut",
  "revenu_independant_net",
  "net_apres_impot",
]);
// Montants que le ménage ou l'employeur ne paient pas (allègements, exonérations).
const ALLEGEMENTS = new Set(["allegements", "exonerations_salariales", "restitution_impot"]);

const euros = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });

export function libellePoste(id: string): string {
  if (id.startsWith("prestation_")) return texte(`menages.prestations.${id.slice("prestation_".length)}`);
  return texte(`menages.flux.postes.${id}`);
}

function flux(montants: Record<string, number>): Flux[] {
  return Object.entries(montants).map(([id, montant]) => ({ id, libelle: libellePoste(id), montant }));
}

function classe(id: string): string {
  if (PASSAGES.has(id)) return "flux-recette";
  if (ALLEGEMENTS.has(id)) return "flux-deficit";
  return "flux-emploi";
}

function Etape({ etape, echelle }: { etape: EtapeFlux; echelle: number }) {
  const entrees = flux(etape.entrees);
  const sorties = regrouper(flux(etape.sorties), SEUIL_AUTRES, (n) => texte("menages.flux.autres", { nombre: n }));
  const total = entrees.reduce((s, f) => s + f.montant, 0);
  const h = Math.max(H_MIN, total * echelle);
  const m = miseEnPage(entrees, sorties, h, ECART);
  const yGauche = espacer(m.gauche.map((n) => n.y + n.hauteur / 2), ESPACE_ETIQUETTES);
  const yDroite = espacer(m.droite.map((n) => n.y + n.hauteur / 2), ESPACE_ETIQUETTES);
  const hauteur = Math.max(h, ...yGauche, ...yDroite) + MARGE;
  const titre = texte(`menages.flux.etapes.${etape.id}`);
  return (
    <figure className="etape-flux">
      <figcaption>{titre}</figcaption>
      <div className="defilement sankey" {...region(titre)}>
        <svg viewBox={`0 0 ${L} ${hauteur}`} role="img" aria-label={texte("menages.flux.aria", { etape: titre })}>
          <g transform={`translate(0,${MARGE / 2})`}>
            {m.liensGauche.map((l) => (
              <path
                key={l.source.id}
                d={bande(X_GAUCHE + LARGEUR_NOEUD, X_CENTRE, l.y0, l.y1, l.epaisseur)}
                className={`lien ${classe(l.source.id)}`}
              >
                <title>{`${l.source.libelle} : ${euros.format(l.source.montant)} €`}</title>
              </path>
            ))}
            {m.liensDroite.map((l) => (
              <path
                key={l.cible.id}
                d={bande(X_CENTRE + LARGEUR_NOEUD, X_DROITE, l.y0, l.y1, l.epaisseur)}
                className={`lien ${classe(l.cible.id)}`}
              >
                <title>{`${l.cible.libelle} : ${euros.format(l.cible.montant)} €`}</title>
              </path>
            ))}
            {m.gauche.map((n, i) => (
              <g key={n.id}>
                <rect x={X_GAUCHE} y={n.y} width={LARGEUR_NOEUD} height={n.hauteur} className={`noeud ${classe(n.id)}`} />
                <text x={X_GAUCHE - 8} y={yGauche[i]} textAnchor="end" dominantBaseline="middle" className="etiquette-sankey">
                  {n.libelle} · {euros.format(n.montant)} €
                </text>
              </g>
            ))}
            <rect x={X_CENTRE} y={m.centre.y} width={LARGEUR_NOEUD} height={m.centre.hauteur} className="noeud noeud-centre" />
            {m.droite.map((n, i) => (
              <g key={n.id}>
                <rect x={X_DROITE} y={n.y} width={LARGEUR_NOEUD} height={n.hauteur} className={`noeud ${classe(n.id)}`} />
                <text x={X_DROITE + LARGEUR_NOEUD + 8} y={yDroite[i]} dominantBaseline="middle" className="etiquette-sankey">
                  {n.libelle} · {euros.format(n.montant)} €
                </text>
              </g>
            ))}
          </g>
        </svg>
      </div>
    </figure>
  );
}

export function FluxMenage({ etapes, libelle }: { etapes: EtapeFlux[]; libelle: string }) {
  // Même échelle pour toutes les étapes du ménage : la plus grande occupe H_MAX.
  const plusGrand = Math.max(...etapes.map((e) => Object.values(e.entrees).reduce((s, v) => s + v, 0)));
  const echelle = H_MAX / plusGrand;
  const tableau = texte("menages.flux.tableau");
  return (
    <details className="explication flux-menage">
      <summary>{texte("menages.flux.titre")}</summary>
      <p>{texte("menages.flux.intro")}</p>
      {etapes.map((e) => (
        <Etape key={e.id} etape={e} echelle={echelle} />
      ))}
      <p className="source">{texte("menages.flux.lecture")}</p>
      <div className="defilement" {...region(`${tableau} : ${libelle}`)}>
        <table>
          <caption>{tableau}</caption>
          <thead>
            <tr>
              <th scope="col">{texte("menages.flux.poste")}</th>
              <th scope="col">{texte("menages.an")}</th>
            </tr>
          </thead>
          <tbody>
            {etapes.map((e) => (
              <FragmentEtape key={e.id} etape={e} />
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

function FragmentEtape({ etape }: { etape: EtapeFlux }) {
  const lignes = (montants: Record<string, number>, sens: "entree" | "sortie") =>
    Object.entries(montants).map(([id, v]) => (
      <tr key={`${sens}-${id}`}>
        <th scope="row">
          {texte(`menages.flux.${sens}`)} {libellePoste(id)}
        </th>
        <td className="nombre">{euros.format(v)} €</td>
      </tr>
    ));
  return (
    <>
      <tr>
        <th scope="rowgroup" colSpan={2} className="groupe">
          {texte(`menages.flux.etapes.${etape.id}`)}
        </th>
      </tr>
      {lignes(etape.entrees, "entree")}
      {lignes(etape.sorties, "sortie")}
    </>
  );
}
