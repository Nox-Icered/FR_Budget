"use client";
// Graphique de la dette en fourchette : bande bas-haut, ligne centrale, repère du raccord.
// Une seule série : pas de légende (le titre la nomme) ; le tableau sous le graphique
// donne toutes les valeurs. Survol : ligne verticale et valeurs bas, centrale et haute.
import { useState } from "react";
import { nombre } from "../../lib/textes";

type Point = { annee: number; bas: number; central: number; haut: number };
type Libelles = {
  titre: string;
  bas: string;
  central: string;
  haut: string;
  raccord: string;
  unite: string;
};

const L = 640;
const H = 300;
const MARGE = { gauche: 52, droite: 16, haut: 32, bas: 36 };

export function GraphiqueDette({
  points,
  raccord,
  libelles,
  reference,
}: {
  points: Point[];
  raccord: number;
  libelles: Libelles;
  reference?: { libelle: string; valeurs: number[] };
}) {
  const [survol, setSurvol] = useState<number | null>(null);
  const annees = points.map((p) => p.annee);
  const extremes = [...points.flatMap((p) => [p.bas, p.haut]), ...(reference?.valeurs ?? [])];
  const min = Math.floor(Math.min(...extremes) / 10) * 10;
  const max = Math.ceil(Math.max(...extremes) / 10) * 10;
  const x = (a: number) =>
    MARGE.gauche +
    ((a - annees[0]) / (annees[annees.length - 1] - annees[0])) * (L - MARGE.gauche - MARGE.droite);
  const y = (v: number) => MARGE.haut + ((max - v) / (max - min)) * (H - MARGE.haut - MARGE.bas);
  const graduations: number[] = [];
  for (let v = min; v <= max; v += 10) graduations.push(v);
  const bande =
    points.map((p, i) => `${i ? "L" : "M"}${x(p.annee)},${y(p.haut)}`).join("") +
    [...points].reverse().map((p) => `L${x(p.annee)},${y(p.bas)}`).join("") +
    "Z";
  const ligne = points.map((p, i) => `${i ? "L" : "M"}${x(p.annee)},${y(p.central)}`).join("");
  const actif = survol === null ? null : points[survol];

  function deplacer(e: React.PointerEvent<SVGRectElement>) {
    const boite = e.currentTarget.ownerSVGElement!.getBoundingClientRect();
    const px = ((e.clientX - boite.left) / boite.width) * L;
    let meilleur = 0;
    points.forEach((p, i) => {
      if (Math.abs(x(p.annee) - px) < Math.abs(x(points[meilleur].annee) - px)) meilleur = i;
    });
    setSurvol(meilleur);
  }

  return (
    <figure className="graphique">
      <figcaption>{libelles.titre}</figcaption>
      <div className="graphique-cadre">
        <svg viewBox={`0 0 ${L} ${H}`} role="img" aria-label={libelles.titre}>
          {graduations.map((v) => (
            <g key={v}>
              <line x1={MARGE.gauche} x2={L - MARGE.droite} y1={y(v)} y2={y(v)} className="grille" />
              <text x={MARGE.gauche - 6} y={y(v)} className="axe" textAnchor="end" dominantBaseline="middle">
                {v}
              </text>
            </g>
          ))}
          {annees
            .filter((a) => a % 5 === 0)
            .map((a) => (
              <text key={a} x={x(a)} y={H - 8} className="axe" textAnchor="middle">
                {a}
              </text>
            ))}
          <line x1={x(raccord)} x2={x(raccord)} y1={MARGE.haut - 8} y2={H - MARGE.bas} className="raccord" />
          <text x={x(raccord) + 4} y={MARGE.haut - 10} className="axe">
            {libelles.raccord}
          </text>
          <path d={bande} className="bande" />
          {reference && (
            <path
              d={reference.valeurs.map((v, i) => `${i ? "L" : "M"}${x(annees[i])},${y(v)}`).join("")}
              className="reference"
            />
          )}
          <path d={ligne} className="centrale" />
          {actif && (
            <g>
              <line x1={x(actif.annee)} x2={x(actif.annee)} y1={MARGE.haut} y2={H - MARGE.bas} className="viseur" />
              <circle cx={x(actif.annee)} cy={y(actif.central)} r={4} className="point" />
            </g>
          )}
          <rect
            x={MARGE.gauche}
            y={0}
            width={L - MARGE.gauche - MARGE.droite}
            height={H}
            fill="transparent"
            onPointerMove={deplacer}
            onPointerLeave={() => setSurvol(null)}
          />
        </svg>
        {actif && (
          <div
            className="infobulle"
            style={{ left: `${Math.min(80, Math.max(20, (x(actif.annee) / L) * 100))}%` }}
            aria-live="polite"
          >
            <strong>{actif.annee}</strong>
            <span>
              {libelles.haut} : {nombre(actif.haut)}
            </span>
            <span>
              {libelles.central} : {nombre(actif.central)}
            </span>
            <span>
              {libelles.bas} : {nombre(actif.bas)}
            </span>
            {reference && (
              <span>
                {reference.libelle} : {nombre(reference.valeurs[survol!])}
              </span>
            )}
          </div>
        )}
      </div>
      <p className="source">{libelles.unite}</p>
    </figure>
  );
}
