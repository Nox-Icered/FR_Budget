"use client";
// Effet du scénario sur la charge des entreprises, par taille : cotisations (Urssaf) et impôt
// sur les sociétés (DGFiP), chacun dans sa nomenclature (lib/entreprises.ts).
import Link from "next/link";
import { texte } from "../../lib/textes";
import { region } from "../../lib/region";
import { effetScenario, GROUPES } from "../../lib/entreprises";
import type { Entreprises } from "../../lib/donnees";
import { millions } from "../entreprises/tableaux";

export function EffetsEntreprisesScenario({
  donnees,
  valeurs,
  autresReglees,
}: {
  donnees: Entreprises;
  valeurs: Record<string, number>;
  /** Dépenses fiscales ou crédits des missions réglés : effet non calculé par taille. */
  autresReglees: boolean;
}) {
  const titre = texte("simulateur.entreprises.titre");
  const groupes = Object.entries(GROUPES)
    .map(([nom, leviers]) => ({ nom, lignes: effetScenario(donnees, leviers, "taille", valeurs) }))
    .filter((g) => g.lignes !== null);
  return (
    <section>
      <h2>{titre}</h2>
      {groupes.length === 0 ? (
        <p>
          {texte(autresReglees ? "simulateur.entreprises.aucune_chiffree" : "simulateur.entreprises.aucune")}
        </p>
      ) : (
        groupes.map(({ nom, lignes }) => {
          const legende = texte(`simulateur.entreprises.groupes.${nom}`);
          return (
            <div key={nom} className="defilement" {...region(legende)}>
              <table>
                <caption>{legende}</caption>
                <thead>
                  <tr>
                    <th scope="col">{texte("entreprises.classe")}</th>
                    <th scope="col">{texte("entreprises.effet")}</th>
                  </tr>
                </thead>
                <tbody>
                  {(lignes ?? []).map(({ classe, effet }) => (
                    <tr key={classe.id}>
                      <th scope="row">{classe.libelle}</th>
                      <td className="nombre">{millions(effet)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })
      )}
      {autresReglees && groupes.length > 0 && <p>{texte("simulateur.entreprises.autres_non_chiffrees")}</p>}
      <p className="source">{texte("simulateur.entreprises.methode")}</p>
      <p>
        <Link href="/entreprises/">{texte("simulateur.entreprises.detail")}</Link>
      </p>
    </section>
  );
}
