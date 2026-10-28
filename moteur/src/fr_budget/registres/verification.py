"""Vérifie les registres : schémas, identifiants uniques, renvois entre registres, empreintes.

Usage : ``uv run python -m fr_budget.registres.verification`` (depuis ``moteur/``).
Code de sortie 1 si une erreur est trouvée.
"""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from fr_budget.registres.schemas import (
    Chiffrage,
    Dataset,
    DepenseFiscaleTva,
    Hypothese,
    Levier,
    RegistreCorrections,
    Relecture,
    Source,
    Statut,
    StatutRelecture,
)

RACINE_DEPOT = Path(__file__).parents[4]
IDENTIFIANT = re.compile(r"[a-z0-9][a-z0-9_]*")


@dataclass
class Rapport:
    erreurs: list[str] = field(default_factory=list)
    avertissements: list[str] = field(default_factory=list)


@dataclass
class Registres:
    sources: list[Source]
    datasets: list[Dataset]
    hypotheses: list[Hypothese]
    leviers: list[Levier]
    chiffrages: list[Chiffrage]
    corrections: RegistreCorrections | None
    libelles_interdits: list[str]
    depenses_fiscales_tva: list[DepenseFiscaleTva] = field(default_factory=list)
    relectures: list[Relecture] = field(default_factory=list)


def _lire(fichier: Path) -> Any:
    if not fichier.is_file():
        return None
    return yaml.safe_load(fichier.read_text(encoding="utf-8"))


def _racine(fichier: Path, cle: str, rapport: Rapport) -> list[Any] | None:
    """Contenu de la clé racine ``cle``, seule clé admise ; ``None`` (et une erreur) sinon."""
    contenu = _lire(fichier)
    if contenu is None:
        rapport.erreurs.append(f"{fichier.name} : fichier absent ou vide")
        return None
    if not isinstance(contenu, dict) or set(contenu) != {cle}:
        rapport.erreurs.append(f"{fichier.name} : une seule clé racine attendue, « {cle} »")
        return None
    valeur = contenu[cle]
    if not isinstance(valeur, list):
        rapport.erreurs.append(f"{fichier.name} : « {cle} » doit être une liste")
        return None
    return valeur


def _liste[M: BaseModel](fichier: Path, cle: str, modele: type[M], rapport: Rapport) -> list[M]:
    contenu = _racine(fichier, cle, rapport)
    if contenu is None:
        return []
    elements = []
    for i, brut in enumerate(contenu):
        try:
            elements.append(modele.model_validate(brut))
        except ValidationError as erreur:
            ident = brut.get("id", f"élément {i}") if isinstance(brut, dict) else f"élément {i}"
            for detail in erreur.errors():
                lieu = ".".join(str(x) for x in detail["loc"])
                rapport.erreurs.append(f"{fichier.name} / {ident} / {lieu} : {detail['msg']}")
    return elements


def charger(dossier: Path, rapport: Rapport) -> Registres:
    corrections = None
    brut = _lire(dossier / "corrections_openfisca.yaml")
    if brut is not None:
        try:
            corrections = RegistreCorrections.model_validate(brut)
        except ValidationError as erreur:
            for detail in erreur.errors():
                lieu = ".".join(str(x) for x in detail["loc"])
                rapport.erreurs.append(f"corrections_openfisca.yaml / {lieu} : {detail['msg']}")
    interdits = _racine(dossier / "libelles_interdits.yaml", "termes", rapport) or []
    if not interdits:
        rapport.erreurs.append(
            "libelles_interdits.yaml : aucun terme, contrôle de neutralité inactif"
        )
    return Registres(
        sources=_liste(dossier / "sources.yaml", "sources", Source, rapport),
        datasets=_liste(dossier / "datasets.yaml", "datasets", Dataset, rapport),
        hypotheses=_liste(dossier / "hypotheses.yaml", "hypotheses", Hypothese, rapport),
        leviers=_liste(dossier / "leviers.yaml", "leviers", Levier, rapport),
        chiffrages=_liste(
            dossier / "references" / "chiffrages.yaml", "chiffrages", Chiffrage, rapport
        ),
        corrections=corrections,
        libelles_interdits=[str(terme) for terme in interdits],
        # Registre propre au levier TVA : facultatif.
        depenses_fiscales_tva=(
            _liste(
                dossier / "tva" / "depenses_fiscales.yaml",
                "depenses_fiscales",
                DepenseFiscaleTva,
                rapport,
            )
            if (dossier / "tva" / "depenses_fiscales.yaml").is_file()
            else []
        ),
        # Registre des relectures externes : facultatif.
        relectures=(
            _liste(dossier / "relectures.yaml", "relectures", Relecture, rapport)
            if (dossier / "relectures.yaml").is_file()
            else []
        ),
    )


def _doublons(nom: str, identifiants: list[str], rapport: Rapport) -> None:
    for ident, nombre in Counter(identifiants).items():
        if nombre > 1:
            rapport.erreurs.append(f"{nom} : identifiant en double « {ident} »")


def _renvoi(lieu: str, cible: str, connus: set[str], nature: str, rapport: Rapport) -> None:
    if cible not in connus:
        rapport.erreurs.append(f"{lieu} : {nature} inconnu(e) « {cible} »")


def _en_tetes_fiches(dossier_fiches: Path) -> list[tuple[str, Any]]:
    """(nom, en-tête YAML) de chaque fiche, hors modèle et README ; ``None`` si illisible."""
    en_tetes: list[tuple[str, Any]] = []
    if not dossier_fiches.is_dir():
        return en_tetes
    for fiche in sorted(dossier_fiches.glob("*.md")):
        if fiche.name.startswith("_") or fiche.name == "README.md":
            continue
        bloc = re.match(r"---\n(.*?)\n---\n", fiche.read_text(encoding="utf-8"), re.DOTALL)
        try:
            en_tete = yaml.safe_load(bloc.group(1)) if bloc else None
        except yaml.YAMLError:
            en_tete = None
        en_tetes.append((fiche.name, en_tete))
    return en_tetes


def modules_documentes(dossier_fiches: Path) -> set[str]:
    """Identifiants de module déclarés dans l'en-tête des fiches (``module: …``)."""
    return {
        en_tete["module"]
        for _, en_tete in _en_tetes_fiches(dossier_fiches)
        if isinstance(en_tete, dict) and isinstance(en_tete.get("module"), str)
    }


def verifier(registres: Registres, racine: Path, rapport: Rapport) -> None:
    """Contrôles qui portent sur plusieurs entrées ou plusieurs registres."""
    sources = {s.id for s in registres.sources}
    leviers = {lv.id for lv in registres.leviers}
    modules = modules_documentes(racine / "docs" / "fiches")
    _doublons("sources.yaml", [s.id for s in registres.sources], rapport)
    _doublons("datasets.yaml", [d.id for d in registres.datasets], rapport)
    _doublons("hypotheses.yaml", [h.id for h in registres.hypotheses], rapport)
    _doublons("leviers.yaml", [lv.id for lv in registres.leviers], rapport)
    _doublons("chiffrages.yaml", [c.id for c in registres.chiffrages], rapport)

    for d in registres.datasets:
        _renvoi(f"datasets.yaml / {d.id}", d.source, sources, "source", rapport)
        donnees_brutes = (racine / "data" / "raw").resolve()
        fichier = (racine / d.fichier).resolve()
        if Path(d.fichier).is_absolute() or not fichier.is_relative_to(donnees_brutes):
            rapport.erreurs.append(f"datasets.yaml / {d.id} : le fichier doit être sous data/raw/")
        elif not fichier.is_file():
            rapport.avertissements.append(f"datasets.yaml / {d.id} : fichier absent ({d.fichier})")
        elif hashlib.sha256(fichier.read_bytes()).hexdigest() != d.empreinte_sha256:
            rapport.erreurs.append(f"datasets.yaml / {d.id} : empreinte différente du fichier")
    for h in registres.hypotheses:
        for s in h.sources:
            _renvoi(f"hypotheses.yaml / {h.id}", s, sources, "source", rapport)
        for instrument in h.instruments:
            _renvoi(
                f"hypotheses.yaml / {h.id}",
                instrument,
                leviers | modules,
                "levier ou module",
                rapport,
            )
    _doublons("relectures.yaml", [r.id for r in registres.relectures], rapport)
    for r in registres.relectures:
        for objet in r.objet:
            _renvoi(
                f"relectures.yaml / {r.id}", objet, leviers | modules, "levier ou module", rapport
            )
    for c in registres.chiffrages:
        if c.levier is not None:
            _renvoi(f"chiffrages.yaml / {c.id}", c.levier, leviers, "levier", rapport)
        if c.module is not None:
            _renvoi(f"chiffrages.yaml / {c.id}", c.module, modules, "module", rapport)
        _renvoi(f"chiffrages.yaml / {c.id}", c.source, sources, "source", rapport)
    chiffrages = {c.id for c in registres.chiffrages}
    for df in registres.depenses_fiscales_tva:
        _renvoi("tva/depenses_fiscales.yaml", df.chiffrage, chiffrages, "chiffrage", rapport)
    if registres.corrections is not None:
        _doublons(
            "corrections_openfisca.yaml", [c.id for c in registres.corrections.corrections], rapport
        )
        for corr in registres.corrections.corrections:
            for s in corr.sources:
                _renvoi(f"corrections_openfisca.yaml / {corr.id}", s, sources, "source", rapport)

    _verifier_statuts(registres, rapport)
    for lv in registres.leviers:
        for terme in registres.libelles_interdits:
            if re.search(rf"\b{re.escape(terme)}\b", lv.libelle, re.IGNORECASE):
                rapport.erreurs.append(
                    f"leviers.yaml / {lv.id} : libellé orienté (« {terme} ») : {lv.libelle}"
                )


def _verifier_statuts(registres: Registres, rapport: Rapport) -> None:
    """Règle de publication (CLAUDE.md) pour un levier au statut « valide » : au moins une
    confrontation à une source indépendante, et toutes ses valeurs de référence relues. Les
    écarts aux références (±10 %) sont contrôlés par les tests de validation."""
    for lv in registres.leviers:
        if lv.statut != Statut.VALIDE:
            continue
        siens = [c for c in registres.chiffrages if c.levier == lv.id]
        if not any(c.independante for c in siens):
            rapport.erreurs.append(
                f"leviers.yaml / {lv.id} : statut « valide » sans confrontation indépendante"
            )
        a_relire = [c.id for c in siens if c.relecture != StatutRelecture.RELU]
        if a_relire:
            rapport.erreurs.append(
                f"leviers.yaml / {lv.id} : statut « valide » avec des chiffrages à relire "
                f"({', '.join(a_relire)})"
            )


def verifier_fiches(dossier_fiches: Path, leviers: set[str], rapport: Rapport) -> None:
    """Chaque fiche (hors modèle) désigne un levier du registre ou un module, dans son en-tête."""
    for nom, en_tete in _en_tetes_fiches(dossier_fiches):
        if not isinstance(en_tete, dict) or ("levier" in en_tete) == ("module" in en_tete):
            rapport.erreurs.append(f"fiches / {nom} : en-tête avec « levier » ou « module »")
        elif "levier" in en_tete:
            _renvoi(f"fiches / {nom}", str(en_tete["levier"]), leviers, "levier", rapport)
        elif not isinstance(en_tete["module"], str) or not IDENTIFIANT.fullmatch(en_tete["module"]):
            rapport.erreurs.append(f"fiches / {nom} : identifiant de module invalide")


def main(dossier: Path = RACINE_DEPOT / "registres") -> int:
    rapport = Rapport()
    registres = charger(dossier, rapport)
    verifier(registres, dossier.parent, rapport)
    verifier_fiches(
        dossier.parent / "docs" / "fiches", {lv.id for lv in registres.leviers}, rapport
    )
    for message in rapport.avertissements:
        print(f"avertissement : {message}")
    for message in rapport.erreurs:
        print(f"erreur : {message}", file=sys.stderr)
    print(
        f"{len(registres.sources)} sources, {len(registres.datasets)} jeux de données, "
        f"{len(registres.hypotheses)} hypothèses, {len(registres.leviers)} leviers, "
        f"{len(registres.chiffrages)} chiffrages : {len(rapport.erreurs)} erreur(s)"
    )
    return 1 if rapport.erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
