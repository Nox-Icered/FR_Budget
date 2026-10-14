"use client";
// Effet d'une unité d'un levier sur la charge des entreprises, par taille et par secteur.
import { useId, useState } from "react";
import { texte } from "../../lib/textes";
import { region } from "../../lib/region";
import type { ClasseEntreprises, Entreprises, FourchetteDonnee } from "../../lib/donnees";

const MILLIONS_PAR_MILLIARD = 1000;
const EUROS_PAR_MILLIARD = 1e9;
const POURCENT = 100;
const entier = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0, signDisplay: "exceptZero" });
const pourcent = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 });

export function millions(f: FourchetteDonnee): string {
  const [b, c, h] = [f.bas, f.central, f.haut].map((v) => entier.format(Math.round(v * MILLIONS_PAR_MILLIARD)));
  return b === h ? c : texte("entreprises.fourchette", { central: c, bas: b, haut: h });
}

function parUnite(c: ClasseEntreprises): string {
  const base = c.effectifs ?? c.entreprises;
  if (!base) return "";
  return entier.format(Math.round((c.effet.central * EUROS_PAR_MILLIARD) / base));
}

function Tableau({ titre, classes, parSalarie }: { titre: string; classes: ClasseEntreprises[]; parSalarie: boolean }) {
  return (
    <section>
      <h3>{titre}</h3>
      <div className="defilement" {...region(titre)}>
        <table>
          <thead>
            <tr>
              <th scope="col">{texte("entreprises.classe")}</th>
              <th scope="col">{texte("entreprises.part")}</th>
              <th scope="col">{texte("entreprises.effet")}</th>
              <th scope="col">{texte(parSalarie ? "entreprises.par_salarie" : "entreprises.par_entreprise")}</th>
            </tr>
          </thead>
          <tbody>
            {classes.map((c) => (
              <tr key={c.id}>
                <th scope="row">{c.libelle}</th>
                <td className="nombre">
                  {c.part.bas === c.part.haut
                    ? pourcent.format(c.part.central * POURCENT)
                    : texte("entreprises.fourchette", {
                        central: pourcent.format(c.part.central * POURCENT),
                        bas: pourcent.format(c.part.bas * POURCENT),
                        haut: pourcent.format(c.part.haut * POURCENT),
                      })}
                </td>
                <td className="nombre">{millions(c.effet)}</td>
                <td className="nombre">{parUnite(c)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function TableauxEntreprises({ donnees }: { donnees: Entreprises }) {
  const id = useId();
  const [choix, setChoix] = useState(donnees.leviers[0].id);
  const levier = donnees.leviers.find((l) => l.id === choix) ?? donnees.leviers[0];
  const social = levier.nomenclatures.taille.some((c) => c.effectifs !== null);
  return (
    <>
      <div className="reglages">
        <label htmlFor={`${id}-levier`}>{texte("entreprises.mesure")}</label>
        <select id={`${id}-levier`} value={choix} onChange={(e) => setChoix(e.target.value)}>
          {donnees.leviers.map((l) => (
            <option key={l.id} value={l.id}>
              {texte(`entreprises.leviers.${l.id}`)}
            </option>
          ))}
        </select>
      </div>
      <p aria-live="polite">
        {texte("entreprises.national", { effet: millions(levier.effet_national) })}
      </p>
      <Tableau
        titre={texte(social ? "entreprises.par_taille_urssaf" : "entreprises.par_taille_dgfip")}
        classes={levier.nomenclatures.taille}
        parSalarie={social}
      />
      {levier.nomenclatures.secteur.length > 0 ? (
        <Tableau
          titre={texte(social ? "entreprises.par_secteur_urssaf" : "entreprises.par_secteur_dgfip")}
          classes={levier.nomenclatures.secteur}
          parSalarie={social}
        />
      ) : (
        <p>{texte("entreprises.sans_secteur")}</p>
      )}
      <p className="source">
        {texte("entreprises.sources")}{" "}
        {levier.sources.map((s, i) => (
          <span key={s}>
            {i > 0 && ", "}
            <a href={`/sources/#${s}`}>{s}</a>
          </span>
        ))}
      </p>
    </>
  );
}
