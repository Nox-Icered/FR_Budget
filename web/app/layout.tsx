import type { ReactNode } from "react";
import Link from "next/link";
import { texte } from "../lib/textes";
import { lire, type Version } from "../lib/donnees";
import "./style.css";

export const metadata = {
  title: texte("site.titre"),
  description: texte("site.description"),
  icons: { icon: "data:," },
};

export default function Gabarit({ children }: { children: ReactNode }) {
  const version = lire<Version>("version.json");
  return (
    <html lang="fr">
      <body>
        <header>
          <p className="avertissement" role="note">
            {texte("site.avertissement")}
          </p>
          <nav aria-label={texte("site.titre")}>
            <Link href="/">{texte("navigation.accueil")}</Link>
            <Link href="/sources/">{texte("navigation.sources")}</Link>
            <Link href="/hypotheses/">{texte("navigation.hypotheses")}</Link>
            <Link href="/validation/">{texte("navigation.validation")}</Link>
          </nav>
        </header>
        <main>{children}</main>
        <footer>
          <p>{texte("site.pied")}</p>
          <p className="version">
            {texte("version.texte", {
              moteur: version.moteur.slice(0, 12),
              registres: version.registres.slice(0, 12),
              donnees: version.donnees.slice(0, 12),
            })}
          </p>
        </footer>
      </body>
    </html>
  );
}
