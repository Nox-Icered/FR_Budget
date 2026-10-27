import type { NextConfig } from "next";
import { normaliser } from "./lib/chemin.ts";

// Site statique : les pages sont générées à partir des fichiers de web/donnees/,
// produits par l'export de l'API (pnpm donnees).
// NEXT_PUBLIC_BASE_PATH : préfixe des adresses quand le site n'est pas à la racine du domaine
// (GitHub Pages : « /FR_Budget »), voir lib/chemin.ts.
const prefixe = normaliser(process.env.NEXT_PUBLIC_BASE_PATH);

const config: NextConfig = {
  output: "export",
  basePath: prefixe,
  reactStrictMode: true,
  trailingSlash: true,
};

export default config;
