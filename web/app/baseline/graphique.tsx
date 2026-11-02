"use client";
// Graphique de la dette en fourchette : bande bas-haut, ligne centrale, repère du raccord.
// Une courbe de comparaison facultative (Commission européenne) a sa propre bande, en trait
// plein pour les années publiées et en pointillés pour le prolongement ; une légende nomme
// alors chaque courbe. Survol : ligne verticale et valeurs de chaque courbe.
import { useState } from "react";
import { nombre } from "../../lib/textes";

type Point = { annee: number; bas: number; central: number; haut: number };
type Comparaison = {
  libelle: string;
  prolongement: string;
  points: (Point & { publiee: boolean })[];
};
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
  comparaison,
  legende,
}: {
  points: Point[];
  raccord: number;
  libelles: Libelles;
  reference?: { libelle: string; valeurs: number[] };
  comparaison?: Comparaison;
  legende?: string;
}) {
  const [survol, setSurvol] = useState<number | null>(null);
  const annees = points.map((p) => p.annee);
  const extremes = [
    ...points.flatMap((p) => [p.bas, p.haut]),
    ...(reference?.valeurs ?? []),
    ...(comparaison?.points.flatMap((p) => [p.bas, p.haut]) ?? []),
  ];
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
  const comp = comparaison?.points;
  const compActif = actif && comp ? comp.find((p) => p.annee === actif.annee) : undefined;
  // Trait plein jusqu'à la dernière année publiée, pointillés ensuite (raccordés à elle).
  const publiees = comp?.filter((p) => p.publiee) ?? [];
  const prolongees = comp ? [...publiees.slice(-1), ...comp.filter((p) => !p.publiee)] : [];
  const trace = (ps: Point[]) =>
    ps.map((p, i) => `${i ? "L" : "M"}${x(p.annee)},${y(p.central)}`).join("");
  const bandeComp = comp
    ? comp.map((p, i) => `${i ? "L" : "M"}${x(p.annee)},${y(p.haut)}`).join("") +
      [...comp].reverse().map((p) => `L${x(p.annee)},${y(p.bas)}`).join("") +
      "Z"
    : "";

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
          {comp && <path d={bandeComp} className="bande-comparaison" />}
          <path d={bande} className="bande" />
          {comp && <path d={trace(publiees)} className="comparaison" />}
          {comp && prolongees.length > 1 && (
            <path d={trace(prolongees)} className="comparaison prolongee" />
          )}
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
            {comparaison && compActif && (
              <span>
                {comparaison.libelle} : {nombre(compActif.central)} ({nombre(compActif.bas)} –{" "}
                {nombre(compActif.haut)})
              </span>
            )}
          </div>
        )}
      </div>
      {comparaison && (
        <ul className="legende">
          <li>
            <span className="cle cle-serie" aria-hidden="true" />
            {legende ?? libelles.titre}
          </li>
          {reference && (
            <li>
              <span className="cle cle-reference" aria-hidden="true" />
              {reference.libelle}
            </li>
          )}
          <li>
            <span className="cle cle-comparaison" aria-hidden="true" />
            {comparaison.libelle}
          </li>
          <li>
            <span className="cle cle-prolongee" aria-hidden="true" />
            {comparaison.prolongement}
          </li>
        </ul>
      )}
      <p className="source">{libelles.unite}</p>
    </figure>
  );
}
