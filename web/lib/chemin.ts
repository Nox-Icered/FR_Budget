// Préfixe des adresses du site, fixé à la construction (NEXT_PUBLIC_BASE_PATH) : vide quand le
// site est servi à la racine d'un domaine, « /FR_Budget » sur GitHub Pages
// (nox-icered.github.io/FR_Budget/). Les composants Link de Next.js l'ajoutent d'eux-mêmes ; les
// liens <a> et les téléchargements de données passent par chemin().
export const PREFIXE = normaliser(process.env.NEXT_PUBLIC_BASE_PATH);

export function normaliser(prefixe: string | undefined): string {
  const p = (prefixe ?? "").trim().replace(/\/+$/, "");
  if (p === "") return "";
  return p.startsWith("/") ? p : `/${p}`;
}

export function chemin(adresse: string, prefixe: string = PREFIXE): string {
  return `${prefixe}${adresse}`;
}
