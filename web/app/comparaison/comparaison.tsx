"use client";
// Comparaison de 2 à 3 scénarios collés sous forme de liens du simulateur. L'adresse de la page
// porte les scénarios (paramètres s1 à s3) ; rien n'est envoyé ni enregistré.
import { useEffect, useId, useState } from "react";
import { texte, nombre } from "../../lib/textes";
import type {
  CatalogueCreditsMissions,
  CatalogueDepensesFiscales,
  ReponsesUnitaires,
  Version,
} from "../../lib/donnees";
import { calculer, type Fourchette } from "../../lib/scenario";
import {
  decoder,
  empreinteVersion,
  encoder,
  mesures,
  problemes,
  type ScenarioExporte,
} from "../../lib/etat";
import { Exports } from "../partage/actions";
import { region } from "../../lib/region";
import { useReponses } from "../../lib/chargement";
import Link from "next/link";


const NOMBRE_SCENARIOS = 3;
const ANNEES_AFFICHEES = [2027, 2030, 2035, 2040, 2046];

type Lecture = { scenario?: ScenarioExporte; alerte?: string };

function ComparaisonChargee({
  donnees,
  catalogue,
  missions,
  version,
}: {
  donnees: ReponsesUnitaires;
  catalogue: CatalogueDepensesFiscales;
  missions: CatalogueCreditsMissions;
  version: Version;
}) {
  const idBase = useId();
  const [liens, setLiens] = useState<string[]>(Array(NOMBRE_SCENARIOS).fill(""));
  const [lu, setLu] = useState(false);
  const empreinte = empreinteVersion(version);

  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    setLiens((l) => l.map((_, k) => p.get(`s${k + 1}`) ?? ""));
    setLu(true);
  }, []);

  const lectures: Lecture[] = liens.map((lien, k) => {
    if (!lien.trim()) return {};
    const etat = decoder(lien.trim());
    if (!etat) return { alerte: texte("partage.lien_illisible") };
    if (problemes(etat, donnees, catalogue, missions).length > 0)
      return { alerte: texte("partage.lien_invalide") };
    const nom = texte("comparaison.nom", { numero: k + 1 });
    const lignes = calculer(
      donnees,
      mesures(etat, catalogue, missions),
      etat.annee,
      etat.croissance === true,
    );
    return {
      scenario: { nom, etat, lignes },
      alerte:
        etat.version && etat.version !== empreinte ? texte("partage.autre_version") : undefined,
    };
  });
  const scenarios = lectures.flatMap((l) => (l.scenario ? [l.scenario] : []));

  const adresse = new URLSearchParams(
    lectures.flatMap((l, k) => (l.scenario ? [[`s${k + 1}`, encoder(l.scenario.etat)]] : [])),
  ).toString();
  useEffect(() => {
    if (lu) window.history.replaceState(null, "", adresse ? `?${adresse}` : "?");
  }, [lu, adresse]);

  const centieme = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    signDisplay: "exceptZero",
  });
  const ecart = (v: number) => centieme.format(Math.abs(v) < 0.005 ? 0 : v);
  const fourchette = (f: Fourchette, format: (v: number) => string) =>
    texte("simulateur.fourchette", {
      central: format(f.central),
      bas: format(f.bas),
      haut: format(f.haut),
    });

  return (
    <>
      <fieldset className="reglages">
        <legend>{texte("comparaison.liens")}</legend>
        {liens.map((lien, k) => (
          <div key={k} className="reglage">
            <label htmlFor={`${idBase}-${k}`}>
              {texte("comparaison.nom", { numero: k + 1 })}
            </label>
            <input
              id={`${idBase}-${k}`}
              type="url"
              value={lien}
              placeholder={texte("comparaison.exemple")}
              onChange={(e) => setLiens(liens.map((l, j) => (j === k ? e.target.value : l)))}
            />
            {lectures[k].alerte && (
              <span className="source" role="alert">
                {lectures[k].alerte}
              </span>
            )}
            {lectures[k].scenario && (
              <Link href={`/simulateur/?${encoder(lectures[k].scenario.etat)}`}>
                {texte("comparaison.ouvrir")}
              </Link>
            )}
          </div>
        ))}
      </fieldset>
      {scenarios.length < 2 ? (
        <p>{texte("comparaison.deux_au_moins")}</p>
      ) : (
        <>
          {(
            [
              ["ecart_solde_primaire", "simulateur.ecart_solde", ecart],
              ["ecart_dette", "simulateur.ecart_dette", ecart],
              ["dette", "simulateur.dette", nombre],
            ] as const
          ).map(([cle, titre, format]) => (
            <div key={cle} className="defilement" {...region(texte(titre))}>
              <table>
                <caption>{texte(titre)}</caption>
                <thead>
                  <tr>
                    <th scope="col">{texte("baseline.annee")}</th>
                    {scenarios.map((s) => (
                      <th key={s.nom} scope="col">
                        {texte("comparaison.entete", {
                          nom: s.nom,
                          annee: s.etat.annee,
                          croissance: texte(
                            s.etat.croissance ? "comparaison.avec_croissance" : "comparaison.sans_croissance",
                          ),
                        })}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ANNEES_AFFICHEES.map((a) => (
                    <tr key={a}>
                      <th scope="row">{a}</th>
                      {scenarios.map((s) => {
                        const ligne = s.lignes.find((l) => l.annee === a);
                        return (
                          <td key={s.nom} className="nombre">
                            {ligne ? fourchette(ligne[cle], format) : ""}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
          <p className="source">{texte("simulateur.unite")}</p>
          <div className="actions">
            <Exports scenarios={scenarios} version={version} nomFichier="comparaison" />
          </div>
        </>
      )}
    </>
  );
}

// Les réponses unitaires (plusieurs mégaoctets) sont chargées par le navigateur, pas
// incluses dans la page (lib/chargement.ts).
export function Comparaison(props: {
  catalogue: CatalogueDepensesFiscales;
  missions: CatalogueCreditsMissions;
  version: Version;
}) {
  const chargement = useReponses(empreinteVersion(props.version));
  if (chargement.etat === "en_cours") return <p role="status">{texte("site.chargement")}</p>;
  if (chargement.etat === "erreur")
    return (
      <p className="avertissement" role="alert">
        {texte("site.chargement_erreur")}
      </p>
    );
  return <ComparaisonChargee donnees={chargement.donnees} {...props} />;
}
