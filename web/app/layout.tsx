import type { ReactNode } from "react";
import Link from "next/link";
import { texte } from "../lib/textes";
import { lire, type Version } from "../lib/donnees";
import { Navigation } from "./navigation";
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
          <div className="entete">
            <Link href="/" className="marque">
              <svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true">
                <rect x="2" y="14" width="5" height="12" rx="1" className="marque-1" />
                <rect x="11" y="8" width="5" height="18" rx="1" className="marque-2" />
                <rect x="20" y="3" width="5" height="23" rx="1" className="marque-3" />
              </svg>
              <span>{texte("site.titre")}</span>
            </Link>
            <Navigation />
          </div>
        </header>
        <main>{children}</main>
        <footer>
          <p>{texte("site.pied")}</p>
          <p>
            <Link href="/mentions-legales/">{texte("navigation.mentions")}</Link>
          </p>
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
