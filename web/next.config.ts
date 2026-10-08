import type { NextConfig } from "next";

// Site statique : les pages sont générées à partir des fichiers de web/donnees/,
// produits par l'export de l'API (pnpm donnees).
const config: NextConfig = {
  output: "export",
  reactStrictMode: true,
  trailingSlash: true,
};

export default config;
