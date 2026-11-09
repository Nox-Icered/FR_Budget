import { texte } from "../../lib/textes";
import { lire, type Version } from "../../lib/donnees";
import { region } from "../../lib/region";

// Page « API » : ce que l'API publique permet, ses règles et son adresse une fois hébergée
// (NEXT_PUBLIC_API_URL, fixée à la construction du site). Guide complet : docs/api.md.
const ROUTES = [
  "leviers",
  "scenario",
  "deciles",
  "objectif",
  "interactions",
  "baseline",
  "validation",
  "registres",
] as const;

export default function PageApi() {
  const version = lire<Version>("version.json");
  const adresse = (process.env.NEXT_PUBLIC_API_URL ?? "").trim().replace(/\/+$/, "");
  return (
    <>
      <h1>{texte("api.titre")}</h1>
      <p>{texte("api.intro")}</p>
      <p className={adresse ? "" : "avertissement"} role="note">
        {adresse ? texte("api.en_ligne", { adresse: `${adresse}/v1/docs` }) : texte("api.pas_en_ligne")}
      </p>
      <h2>{texte("api.routes_titre")}</h2>
      <ul>
        {ROUTES.map((r) => (
          <li key={r}>{texte(`api.routes.${r}`)}</li>
        ))}
      </ul>
      <h2>{texte("api.exemple_titre")}</h2>
      <p>{texte("api.exemple_intro")}</p>
      <pre className="defilement" {...region(texte("api.exemple_titre"))}>
        <code>{`POST /v1/scenario
{"mesures": [{"levier": "tva_taux_normal", "valeur": 1, "annee": 2027}]}`}</code>
      </pre>
      <h2>{texte("api.regles_titre")}</h2>
      <ul>
        {(["sans_etat", "fourchettes", "statut", "neutralite", "limites", "licences"] as const).map((r) => (
          <li key={r}>{texte(`api.regles.${r}`)}</li>
        ))}
      </ul>
      <p className="source">{texte("api.version", { moteur: version.moteur.slice(0, 12) })}</p>
    </>
  );
}
