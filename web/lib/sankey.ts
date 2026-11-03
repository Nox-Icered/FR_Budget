// Diagramme de Sankey du budget de l'État : ressources à gauche, une barre centrale, emplois à
// droite. Mise en page pure (testée) ; le dessin est dans app/budget-etat.tsx.
export type Flux = { id: string; libelle: string; montant: number };
export type Noeud = Flux & { y: number; hauteur: number };
export type Lien = { source: Noeud; cible: Noeud; y0: number; y1: number; epaisseur: number };
export type MiseEnPage = {
  gauche: Noeud[];
  droite: Noeud[];
  centre: { y: number; hauteur: number };
  liensGauche: Lien[];
  liensDroite: Lien[];
  total: number;
};

// Regroupe les emplois plus petits que `seuil` (part du total) en un seul flux final.
export function regrouper(emplois: Flux[], seuil: number, libelleAutres: (n: number) => string): Flux[] {
  const total = emplois.reduce((s, f) => s + f.montant, 0);
  const grands = emplois.filter((f) => f.montant >= seuil * total);
  const petits = emplois.filter((f) => f.montant < seuil * total);
  if (petits.length < 2) return emplois;
  return [
    ...grands,
    { id: "autres", libelle: libelleAutres(petits.length), montant: petits.reduce((s, f) => s + f.montant, 0) },
  ];
}

function empiler(flux: Flux[], hauteur: number, ecart: number, echelle: number): Noeud[] {
  const utile = flux.reduce((s, f) => s + f.montant * echelle, 0) + ecart * (flux.length - 1);
  let y = (hauteur - utile) / 2;
  return flux.map((f) => {
    const n = { ...f, y, hauteur: f.montant * echelle };
    y += n.hauteur + ecart;
    return n;
  });
}

export function miseEnPage(ressources: Flux[], emplois: Flux[], hauteur: number, ecart: number): MiseEnPage {
  const total = ressources.reduce((s, f) => s + f.montant, 0);
  const plusNombreux = Math.max(ressources.length, emplois.length);
  const echelle = (hauteur - ecart * (plusNombreux - 1)) / total;
  const gauche = empiler(ressources, hauteur, ecart, echelle);
  const droite = empiler(emplois, hauteur, ecart, echelle);
  const centre = { y: (hauteur - total * echelle) / 2, hauteur: total * echelle };
  let yc = centre.y;
  const liensGauche = gauche.map((n) => {
    const l = { source: n, cible: n, y0: n.y, y1: yc, epaisseur: n.hauteur };
    yc += n.hauteur;
    return l;
  });
  yc = centre.y;
  const liensDroite = droite.map((n) => {
    const l = { source: n, cible: n, y0: yc, y1: n.y, epaisseur: n.hauteur };
    yc += n.hauteur;
    return l;
  });
  return { gauche, droite, centre, liensGauche, liensDroite, total };
}

// Bande entre deux colonnes : bord haut et bord bas en courbes de Bézier.
export function bande(x0: number, x1: number, y0: number, y1: number, epaisseur: number): string {
  const m = (x0 + x1) / 2;
  return (
    `M${x0},${y0}C${m},${y0} ${m},${y1} ${x1},${y1}` +
    `L${x1},${y1 + epaisseur}C${m},${y1 + epaisseur} ${m},${y0 + epaisseur} ${x0},${y0 + epaisseur}Z`
  );
}

// Centres d'étiquettes espacés d'au moins `min` (dans l'ordre, sans changer le premier ni
// l'ordre) : les petits flux voisins ne se chevauchent plus.
export function espacer(centres: number[], min: number): number[] {
  const sortie: number[] = [];
  for (const c of centres) {
    const precedent = sortie.at(-1);
    sortie.push(precedent === undefined ? c : Math.max(c, precedent + min));
  }
  return sortie;
}
