"use client";
// Copie du lien et exports : tout se fait dans le navigateur, rien n'est envoyé.
import { useState } from "react";
import { texte } from "../../lib/textes";
import type { Version } from "../../lib/donnees";
import { versCsv, versJson, type ScenarioExporte } from "../../lib/etat";

function telecharger(nom: string, contenu: string, type: string) {
  const url = URL.createObjectURL(new Blob([contenu], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = nom;
  a.click();
  URL.revokeObjectURL(url);
}

export function Exports({
  scenarios,
  version,
  nomFichier,
}: {
  scenarios: ScenarioExporte[];
  version: Version;
  nomFichier: string;
}) {
  return (
    <>
      <button
        type="button"
        onClick={() => telecharger(`${nomFichier}.csv`, versCsv(scenarios), "text/csv")}
      >
        {texte("partage.export_csv")}
      </button>
      <button
        type="button"
        onClick={() =>
          telecharger(`${nomFichier}.json`, versJson(scenarios, version), "application/json")
        }
      >
        {texte("partage.export_json")}
      </button>
    </>
  );
}

export function CopierLien() {
  const [message, setMessage] = useState("");
  const copier = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setMessage(texte("partage.lien_copie"));
    } catch {
      // Presse-papiers refusé (contexte non sécurisé, permission) : l'adresse de la page suffit.
      setMessage(texte("partage.lien_non_copie"));
    }
  };
  return (
    <>
      <button type="button" onClick={copier}>
        {texte("partage.copier_lien")}
      </button>
      <span className="source" role="status">
        {message}
      </span>
    </>
  );
}
