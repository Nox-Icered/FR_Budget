from pathlib import Path
from typing import Any

import pytest
import yaml

from fr_budget.registres.verification import Rapport, charger, main, verifier

SOURCE: dict[str, Any] = {
    "id": "source_a",
    "nom": "Document A",
    "editeur": "Éditeur A",
    "url": "https://exemple.invalid/a",
    "licence": "Licence Ouverte 2.0",
    "acces": "direct",
    "consulte_le": "2026-10-07",
}
LEVIER: dict[str, Any] = {
    "id": "levier_a",
    "libelle": "Taux de la taxe A",
    "parametres_reglables": ["Taux"],
    "moteur": "agrege",
    "references_visees": ["Document A"],
    "statut": "non_publie",
}
HYPOTHESE: dict[str, Any] = {
    "id": "hypothese_a",
    "libelle": "Élasticité A",
    "unite": "sans unité",
    "valeur_centrale": 1.0,
    "plage": {"basse": 0.5, "haute": 1.5},
    "sources": ["source_a"],
    "justification": "Fourchette de la littérature citée",
    "instruments": ["levier_a"],
}


def ecrire_registres(dossier: Path, **contenus: Any) -> Path:
    registres = dossier / "registres"
    (registres / "references").mkdir(parents=True)
    valeurs: dict[str, Any] = {
        "sources": [SOURCE],
        "datasets": [],
        "hypotheses": [HYPOTHESE],
        "leviers": [LEVIER],
        "chiffrages": [],
        "termes": ["effort"],
    }
    valeurs.update(contenus)
    fichiers = {
        "sources": "sources.yaml",
        "datasets": "datasets.yaml",
        "hypotheses": "hypotheses.yaml",
        "leviers": "leviers.yaml",
        "chiffrages": "references/chiffrages.yaml",
        "termes": "libelles_interdits.yaml",
    }
    for cle, fichier in fichiers.items():
        (registres / fichier).write_text(yaml.safe_dump({cle: valeurs[cle]}), encoding="utf-8")
    return registres


def erreurs(registres: Path) -> list[str]:
    rapport = Rapport()
    verifier(charger(registres, rapport), registres.parent, rapport)
    return rapport.erreurs


def test_registres_du_depot_valides() -> None:
    assert main() == 0


def test_registres_minimaux_valides(tmp_path: Path) -> None:
    assert erreurs(ecrire_registres(tmp_path)) == []


def test_source_sans_licence_refusee(tmp_path: Path) -> None:
    source = {k: v for k, v in SOURCE.items() if k != "licence"}
    assert any("licence" in e for e in erreurs(ecrire_registres(tmp_path, sources=[source])))


def test_champ_inconnu_refuse(tmp_path: Path) -> None:
    source = {**SOURCE, "licnece": "faute de frappe"}
    assert any("licnece" in e for e in erreurs(ecrire_registres(tmp_path, sources=[source])))


@pytest.mark.parametrize(("basse", "haute"), [(1.2, 1.5), (0.5, 0.8)])
def test_plage_qui_n_encadre_pas_la_valeur_centrale_refusee(
    tmp_path: Path, basse: float, haute: float
) -> None:
    hypothese = {**HYPOTHESE, "plage": {"basse": basse, "haute": haute}}
    resultat = erreurs(ecrire_registres(tmp_path, hypotheses=[hypothese]))
    assert any("basse ≤ centrale ≤ haute" in e for e in resultat)


def test_source_inconnue_refusee(tmp_path: Path) -> None:
    hypothese = {**HYPOTHESE, "sources": ["source_absente"]}
    resultat = erreurs(ecrire_registres(tmp_path, hypotheses=[hypothese]))
    assert any("source_absente" in e for e in resultat)


def test_identifiant_en_double_refuse(tmp_path: Path) -> None:
    resultat = erreurs(ecrire_registres(tmp_path, sources=[SOURCE, SOURCE]))
    assert any("en double" in e for e in resultat)


def test_libelle_oriente_refuse(tmp_path: Path) -> None:
    levier = {**LEVIER, "libelle": "Effort sur la taxe A"}
    resultat = erreurs(ecrire_registres(tmp_path, leviers=[levier]))
    assert any("libellé orienté" in e for e in resultat)


def test_empreinte_differente_refusee(tmp_path: Path) -> None:
    fichier = tmp_path / "data" / "raw" / "a.csv"
    fichier.parent.mkdir(parents=True)
    fichier.write_text("colonne\n1\n", encoding="utf-8")
    dataset = {
        "id": "dataset_a",
        "source": "source_a",
        "description": "Tableau A",
        "fichier": "data/raw/a.csv",
        "empreinte_sha256": "0" * 64,
        "methode_transformation": "pipelines/a.py",
        "telecharge_le": "2026-10-07",
    }
    resultat = erreurs(ecrire_registres(tmp_path, datasets=[dataset]))
    assert any("empreinte" in e for e in resultat)
