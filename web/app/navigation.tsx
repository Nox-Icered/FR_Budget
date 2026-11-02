"use client";
// Menu en trois groupes dépliables (maquette du 2 novembre 2026). Il se referme à chaque
// changement de page (clé sur le chemin) et signale la page courante.
import Link from "next/link";
import { usePathname } from "next/navigation";
import { texte } from "../lib/textes";

const GROUPES: { id: string; liens: [string, string][] }[] = [
  {
    id: "groupe_simuler",
    liens: [
      ["/simulateur/", "simulateur"],
      ["/comparaison/", "comparaison"],
      ["/baseline/", "baseline"],
    ],
  },
  {
    id: "groupe_effets",
    liens: [
      ["/menages/", "menages"],
      ["/mon-menage/", "mon_menage"],
      ["/entreprises/", "entreprises"],
    ],
  },
  {
    id: "groupe_transparence",
    liens: [
      ["/sources/", "sources"],
      ["/hypotheses/", "hypotheses"],
      ["/validation/", "validation"],
      ["/journal/", "journal"],
      ["/relectures/", "relectures"],
    ],
  },
];

export function Navigation() {
  const chemin = usePathname() ?? "/";
  const courant = (href: string) => chemin.replace(/\/?$/, "/").endsWith(href);
  return (
    <nav aria-label={texte("site.titre")} className="menu" key={chemin}>
      {GROUPES.map((g) => (
        <details key={g.id} className="menu-groupe">
          <summary className={g.liens.some(([h]) => courant(h)) ? "actif" : undefined}>
            {texte(`navigation.${g.id}`)}
          </summary>
          <ul>
            {g.liens.map(([href, cle]) => (
              <li key={href}>
                <Link href={href} aria-current={courant(href) ? "page" : undefined}>
                  {texte(`navigation.${cle}`)}
                </Link>
              </li>
            ))}
          </ul>
        </details>
      ))}
    </nav>
  );
}
