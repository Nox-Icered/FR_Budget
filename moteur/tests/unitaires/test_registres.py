import hashlib
from pathlib import Path
from typing import Any

import pytest
import yaml

from fr_budget.registres.verification import (
    Rapport,
    charger,
    main,
    modules_documentes,
    verifier,
    verifier_fiches,
)

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


def test_cle_racine_mal_orthographiee_refusee(tmp_path: Path) -> None:
    registres = ecrire_registres(tmp_path)
    (registres / "hypotheses.yaml").write_text(
        yaml.safe_dump({"hypotheeses": [HYPOTHESE]}), encoding="utf-8"
    )
    assert any("clé racine" in e for e in erreurs(registres))


def test_instrument_inconnu_refuse(tmp_path: Path) -> None:
    hypothese = {**HYPOTHESE, "instruments": ["levier_absent"]}
    resultat = erreurs(ecrire_registres(tmp_path, hypotheses=[hypothese]))
    assert any("levier_absent" in e for e in resultat)


@pytest.mark.parametrize("contenu", [None, {"termes": []}, {"terms": ["effort"]}])
def test_liste_de_termes_interdits_absente_ou_vide_refusee(
    tmp_path: Path, contenu: dict[str, Any] | None
) -> None:
    registres = ecrire_registres(tmp_path)
    fichier = registres / "libelles_interdits.yaml"
    if contenu is None:
        fichier.unlink()
    else:
        fichier.write_text(yaml.safe_dump(contenu), encoding="utf-8")
    assert any("libelles_interdits.yaml" in e for e in erreurs(registres))


@pytest.mark.parametrize("chemin", ["data/processed/a.csv", "data/raw/../processed/a.csv"])
def test_fichier_hors_de_data_raw_refuse(tmp_path: Path, chemin: str) -> None:
    fichier = tmp_path / "data" / "processed" / "a.csv"
    fichier.parent.mkdir(parents=True)
    fichier.write_text("colonne\n1\n", encoding="utf-8")
    dataset = {
        "id": "dataset_a",
        "source": "source_a",
        "description": "Tableau A",
        "fichier": chemin,
        "empreinte_sha256": hashlib.sha256(fichier.read_bytes()).hexdigest(),
        "methode_transformation": "pipelines/a.py",
        "telecharge_le": "2026-10-07",
    }
    resultat = erreurs(ecrire_registres(tmp_path, datasets=[dataset]))
    assert any("data/raw/" in e for e in resultat)


@pytest.mark.parametrize(
    ("contenu", "valide"),
    [
        ("---\nlevier: levier_a\n---\n# Fiche\n", True),
        ("---\nmodule: cascade\n---\n# Fiche\n", True),
        ("---\nlevier: levier_absent\n---\n# Fiche\n", False),
        ("---\nlevier: levier_a\nmodule: cascade\n---\n# Fiche\n", False),
        ("---\nmodule:\n---\n# Fiche\n", False),
        ("---\nmodule: [a, b]\n---\n# Fiche\n", False),
        ("---\nmodule: Module Invalide\n---\n# Fiche\n", False),
        ("# Fiche sans en-tête\n", False),
    ],
)
def test_en_tete_des_fiches(tmp_path: Path, contenu: str, valide: bool) -> None:
    (tmp_path / "fiche.md").write_text(contenu, encoding="utf-8")
    (tmp_path / "_modele.md").write_text("# Modèle sans en-tête\n", encoding="utf-8")
    rapport = Rapport()
    verifier_fiches(tmp_path, {"levier_a"}, rapport)
    assert (rapport.erreurs == []) is valide


CHIFFRAGE: dict[str, Any] = {
    "id": "chiffrage_a",
    "levier": "levier_a",
    "source": "source_a",
    "millesime": "2023",
    "mesure": "Coût du taux réduit A",
    "valeur": 100.0,
    "unite": "M€",
    "localisation": "page 1",
    "saisi_le": "2026-10-08",
    "relecture": "a_relire",
}


@pytest.mark.parametrize(
    ("entree", "message"),
    [
        ({"chiffrage": "inconnu", "usage": "ecart_territorial", "annee": 2023}, "inconnu"),
        ({"chiffrage": "chiffrage_a", "usage": "repartition", "annee": 2023}, "produit"),
        (
            {
                "chiffrage": "chiffrage_a",
                "usage": "ecart_territorial",
                "annee": 2023,
                "produit": "P1",
                "regime": "reduit",
            },
            "produit",
        ),
    ],
)
def test_depenses_fiscales_tva_controlees(
    tmp_path: Path, entree: dict[str, Any], message: str
) -> None:
    registres = ecrire_registres(tmp_path, chiffrages=[CHIFFRAGE])
    (registres / "tva").mkdir()
    (registres / "tva" / "depenses_fiscales.yaml").write_text(
        yaml.safe_dump({"depenses_fiscales": [entree]}), encoding="utf-8"
    )
    assert any(message in e for e in erreurs(registres))


def test_chiffrage_d_un_module_inconnu_refuse(tmp_path: Path) -> None:
    chiffrage = {**CHIFFRAGE, "levier": None, "module": "module_inconnu"}
    del chiffrage["levier"]
    assert any("module" in e for e in erreurs(ecrire_registres(tmp_path, chiffrages=[chiffrage])))


def test_chiffrage_avec_levier_et_module_refuse(tmp_path: Path) -> None:
    chiffrage = {**CHIFFRAGE, "module": "dynamique_dette"}
    assert any(
        "exactement" in e for e in erreurs(ecrire_registres(tmp_path, chiffrages=[chiffrage]))
    )


def test_en_tete_yaml_illisible_signale_sans_planter(tmp_path: Path) -> None:
    fiches = tmp_path / "fiches"
    fiches.mkdir()
    (fiches / "casse.md").write_text("---\nmodule: [non ferme\n---\n# Fiche\n", encoding="utf-8")
    (fiches / "_modele.md").write_text(
        "---\nmodule: identifiant_du_module\n---\n", encoding="utf-8"
    )
    rapport = Rapport()
    verifier_fiches(fiches, set(), rapport)
    assert any("casse.md" in e for e in rapport.erreurs)
    assert modules_documentes(fiches) == set()
