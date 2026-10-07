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
    Hypothese,
    Levier,
    RegistreCorrections,
    Source,
)

RACINE_DEPOT = Path(__file__).parents[4]


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
    )


def _doublons(nom: str, identifiants: list[str], rapport: Rapport) -> None:
    for ident, nombre in Counter(identifiants).items():
        if nombre > 1:
            rapport.erreurs.append(f"{nom} : identifiant en double « {ident} »")


def _renvoi(lieu: str, cible: str, connus: set[str], nature: str, rapport: Rapport) -> None:
    if cible not in connus:
        rapport.erreurs.append(f"{lieu} : {nature} inconnu(e) « {cible} »")


def verifier(registres: Registres, racine: Path, rapport: Rapport) -> None:
    """Contrôles qui portent sur plusieurs entrées ou plusieurs registres."""
    sources = {s.id for s in registres.sources}
    leviers = {lv.id for lv in registres.leviers}
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
            _renvoi(f"hypotheses.yaml / {h.id}", instrument, leviers, "levier", rapport)
    for c in registres.chiffrages:
        _renvoi(f"chiffrages.yaml / {c.id}", c.levier, leviers, "levier", rapport)
        _renvoi(f"chiffrages.yaml / {c.id}", c.source, sources, "source", rapport)
    if registres.corrections is not None:
        _doublons(
            "corrections_openfisca.yaml", [c.id for c in registres.corrections.corrections], rapport
        )
        for corr in registres.corrections.corrections:
            for s in corr.sources:
                _renvoi(f"corrections_openfisca.yaml / {corr.id}", s, sources, "source", rapport)

    for lv in registres.leviers:
        for terme in registres.libelles_interdits:
            if re.search(rf"\b{re.escape(terme)}\b", lv.libelle, re.IGNORECASE):
                rapport.erreurs.append(
                    f"leviers.yaml / {lv.id} : libellé orienté (« {terme} ») : {lv.libelle}"
                )


def main(dossier: Path = RACINE_DEPOT / "registres") -> int:
    rapport = Rapport()
    registres = charger(dossier, rapport)
    verifier(registres, dossier.parent, rapport)
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
