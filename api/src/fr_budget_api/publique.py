"""API publique, version 1 (lot V2 « API publique », plan validé le 9 novembre 2026).

Sous-application montée sur ``/v1`` par ``fr_budget_api.app.creer_application``. Contrat stable :
une route ou un champ n'est retiré ou changé de sens que dans une nouvelle version (``/v2``).
Documentation : ``/v1/docs`` ; description OpenAPI versionnée dans ``api/openapi-v1.json``
(``python -m fr_budget_api.openapi``) ; guide en français dans ``docs/api.md``.

Règles (CLAUDE.md) :

- sans état : rien n'est stocké ni journalisé, et aucun message d'erreur ne reprend une valeur
  saisie (format unique : ``{"erreur": {"code", "message", "champs"}}``) ;
- chaque résultat chiffré est en fourchette et porte la version du modèle et des données, ses
  sources et ses hypothèses ;
- statut de chaque levier (« beta » : non validé) et écarts aux références (``/v1/validation``) ;
- aucune recommandation ni classement : l'API calcule ce que l'appelant demande.

Garde-fous : corps de requête limité à ``TAILLE_MAX`` octets et à ``MESURES_MAX`` mesures ;
appels de tout domaine permis (CORS ouvert, sans cookies). Le plafond de requêtes par minute est
laissé à l'hébergeur (``docs/api.md``).
"""

from __future__ import annotations

import json
import math
from collections.abc import Awaitable, Callable
from functools import cache
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fr_budget import objectif as module_objectif
from fr_budget import scenario as module_scenario
from fr_budget.agrege import interactions as module_interactions
from fr_budget.baseline import ANNEE_FIN
from fr_budget.menages import deciles as module_deciles
from fr_budget.menages import leviers as module_leviers_menages
from fr_budget.registres.verification import RACINE_DEPOT
from pydantic import BaseModel, Field, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import circulaire voulu : ``app`` monte cette sous-application dans ``creer_application`` ;
# ses fonctions ne sont appelées qu'à la requête. Importer ``fr_budget_api.app`` en premier.
from fr_budget_api import app as base

VERSION_API = "1"
TAILLE_MAX = 32_768
"""Taille maximale d'un corps de requête, en octets."""
MESURES_MAX = 40
NON_TROUVE = 404
LICENCES = {
    "code": "AGPL-3.0-or-later",
    "donnees": "Licence Ouverte 2.0 (chaque source garde sa licence : /v1/registres/sources)",
}
LEVIERS_INTERNES = (
    module_scenario.LEVIER_DEPENSE_FISCALE_UNITE,
    module_scenario.LEVIER_CREDITS_UNITE,
    module_scenario.LEVIER_IR_BAREME,
)
"""Leviers génériques du site, en Md€ : par l'API, une dépense fiscale ou une mission est
désignée par son identifiant (``/v1/depenses-fiscales``, ``/v1/credits-missions``)."""
FICHIER_TEXTES = RACINE_DEPOT / "web" / "messages" / "fr.json"
DESCRIPTION = (
    "API publique du simulateur du budget des administrations publiques françaises. "
    "Sans état : aucune donnée envoyée n'est stockée ni journalisée. Chaque résultat est une "
    "fourchette (basse, centrale, haute) et porte la version du modèle et des données. Les "
    "leviers marqués « beta » ne sont pas validés ; les écarts aux références officielles sont "
    "dans /v1/validation. L'API calcule ce que l'appelant demande : elle ne recommande ni ne "
    "classe aucune mesure. Code sous licence AGPL-3.0-or-later, données sous Licence Ouverte 2.0."
)


# Entrées --------------------------------------------------------------------------------------


class MesureV1(BaseModel):
    levier: str = Field(max_length=80, description="Identifiant du levier (/v1/leviers).")
    valeur: float = Field(description="Réglage, dans l'unité et les bornes du levier.")
    annee: int = Field(
        ge=module_scenario.ANNEE_PREMIERE_MESURE,
        le=ANNEE_FIN,
        description="Année d'entrée en vigueur.",
    )

    @field_validator("valeur")
    @classmethod
    def _finie(cls, v: float) -> float:
        if not math.isfinite(v):
            msg = "valeur non finie"
            raise ValueError(msg)
        return v


class ScenarioV1(BaseModel):
    mesures: list[MesureV1] = Field(default_factory=list, max_length=MESURES_MAX)
    croissance: bool = Field(
        default=False, description="Effet sur l'activité (multiplicateur), désactivé par défaut."
    )


class DecilesV1(BaseModel):
    mesures: list[MesureV1] = Field(min_length=1, max_length=MESURES_MAX)


class ObjectifV1(BaseModel):
    levier: str = Field(max_length=80)
    entree: int = Field(ge=module_scenario.ANNEE_PREMIERE_MESURE, le=ANNEE_FIN)
    indicateur: Literal["dette", "solde_primaire"]
    annee: int = Field(ge=module_scenario.ANNEE_PREMIERE_MESURE, le=ANNEE_FIN)
    cible: float = Field(ge=-100, le=1000, description="Valeur à atteindre, en % du PIB.")


# Erreurs : format unique, sans la valeur saisie -----------------------------------------------


def _erreur(statut: int, code: str, message: str, champs: list[str] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=statut,
        content={"erreur": {"code": code, "message": message, "champs": champs or []}},
    )


class ErreurV1(HTTPException):
    def __init__(self, statut: int, code: str, message: str) -> None:
        super().__init__(status_code=statut, detail=message)
        self.code = code


# Leviers --------------------------------------------------------------------------------------


@cache
def _textes() -> dict[str, Any]:
    if not FICHIER_TEXTES.is_file():
        return {}
    contenu: dict[str, Any] = json.loads(FICHIER_TEXTES.read_text(encoding="utf-8"))
    return contenu


def _nombre(x: float) -> str:
    """Nombre au format français, au plus deux décimales."""
    texte = f"{x:.2f}".rstrip("0").rstrip(".")
    return texte.replace(".", ",")


def leviers_publics() -> list[str]:
    return [lv for lv in module_scenario.LEVIERS_REGISTRE if lv not in LEVIERS_INTERNES]


def description_levier(levier: str) -> dict[str, Any]:
    textes = _textes().get("simulateur", {}).get("leviers", {}).get(levier, {})
    reference = module_scenario.taux_reference(levier)
    basse, haute = module_scenario.bornes_levier(levier)
    sources, hypotheses = module_scenario.provenance([levier])
    unite = textes.get("valeur", "").replace("{valeur}", "").strip(" +")
    raison = module_leviers_menages.SANS_EFFET.get(levier)
    return {
        "id": levier,
        "libelle": textes.get("libelle", "")
        .replace("{reference}", _nombre(reference))
        .replace("{annee}", str(module_scenario.ANNEE_REFERENCE)),
        "explication": textes.get("explication", ""),
        "unite": unite,
        "bornes": [basse, haute],
        "valeur_reference": reference,
        "statut": base._statut_levier(levier),
        "registre": module_scenario.levier_registre(levier),
        "rendement_unitaire_md_euros": base._fourchette(module_scenario.rendement_unitaire(levier)),
        "annee_euros": module_scenario.ANNEE_REFERENCE,
        "sources": sources,
        "hypotheses": hypotheses,
        "menages_types": "sans_effet" if raison else "calcule",
        "deciles": "reparti" if module_deciles.est_reparti(levier) else "non_reparti",
        "crans": module_scenario.grille_levier(levier)
        if levier in module_scenario.LEVIERS_NON_LINEAIRES
        else None,
    }


def _version() -> dict[str, str]:
    return {**base.version_donnees(), "api": VERSION_API}


# Application ----------------------------------------------------------------------------------


def creer_api_publique() -> FastAPI:
    api = FastAPI(
        title="Simulateur du budget des administrations publiques : API publique",
        description=DESCRIPTION,
        version=VERSION_API,
        license_info={"name": "AGPL-3.0-or-later", "identifier": "AGPL-3.0-or-later"},
    )
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
    )

    @api.middleware("http")
    async def limiter_taille(
        requete: Request, suite: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        longueur = requete.headers.get("content-length")
        if longueur is not None and (not longueur.isdigit() or int(longueur) > TAILLE_MAX):
            return _erreur(413, "requete_trop_grande", f"Corps limité à {TAILLE_MAX} octets.")
        return await suite(requete)

    @api.exception_handler(RequestValidationError)
    async def requete_invalide(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Seuls les noms des champs fautifs, jamais les valeurs envoyées (règle 5).
        champs = sorted({".".join(str(p) for p in e.get("loc", ())[1:]) for e in exc.errors()})
        return _erreur(422, "requete_invalide", "Requête mal formée ou hors des bornes.", champs)

    @api.exception_handler(StarletteHTTPException)
    async def erreur_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = getattr(exc, "code", "introuvable" if exc.status_code == NON_TROUVE else "erreur")
        return _erreur(exc.status_code, code, str(exc.detail))

    @api.get("/")
    def presentation() -> dict[str, Any]:
        """Présentation, version, licences et liste des routes."""
        return {
            "description": DESCRIPTION,
            "version": _version(),
            "licences": LICENCES,
            "documentation": "/v1/docs",
            "routes": sorted(
                {
                    chemin
                    for r in api.routes
                    if (chemin := getattr(r, "path", "")).startswith("/") and "docs" not in chemin
                }
            ),
        }

    @api.get("/version")
    def route_version() -> dict[str, str]:
        """Version de l'API, du moteur et des données."""
        return _version()

    @api.get("/leviers")
    def route_leviers() -> list[dict[str, Any]]:
        """Leviers réglables : libellé, unité, bornes, statut, rendement d'une unité, sources."""
        return [description_levier(lv) for lv in leviers_publics()]

    @api.get("/leviers/{levier}")
    def route_levier(levier: str) -> dict[str, Any]:
        if levier not in leviers_publics():
            raise ErreurV1(404, "levier_inconnu", "Levier inconnu (voir /v1/leviers).")
        return description_levier(levier)

    @api.get("/interactions")
    def route_interactions() -> dict[str, Any]:
        """Termes croisés chiffrés entre leviers, et interactions connues non chiffrées."""
        return {
            "chiffrees": [
                {
                    "id": ident,
                    "leviers": list(paire),
                    "rendement_unitaire_md_euros": base._fourchette(
                        module_interactions.rendement_unitaire(ident)
                    ),
                }
                for ident, paire in module_interactions.CHIFFREES.items()
            ],
            "non_chiffrees": [
                {
                    "mecanisme": p.mecanisme,
                    "leviers_a": list(p.leviers_a),
                    "leviers_b": list(p.leviers_b),
                    "manque": p.manque,
                }
                for p in module_interactions.NON_CHIFFREES
            ],
        }

    @api.post("/scenario")
    def route_scenario(entree: ScenarioV1) -> dict[str, Any]:
        """Dette et solde primaire de 2025 à 2046 avec les mesures, en fourchette, avec les
        termes croisés et les interactions non chiffrées."""
        resultat = base.calcul_scenario(
            base.ScenarioEntree(
                mesures=[base.MesureEntree(**m.model_dump()) for m in entree.mesures],
                croissance=entree.croissance,
            )
        )
        if resultat is None:
            raise ErreurV1(
                422,
                "mesure_invalide",
                "Levier inconnu ou interne, valeur hors des bornes, ou combinaison refusée "
                "(double compte).",
            )
        return {**resultat, "version": _version()}

    @api.post("/deciles")
    def route_deciles(entree: DecilesV1) -> dict[str, Any]:
        """Variation du revenu disponible par dixième de niveau de vie (Md€, euros par unité
        de consommation, % du revenu disponible), année pleine, euros de 2025."""
        mesures = [module_scenario.Mesure(m.levier, m.valeur, m.annee) for m in entree.mesures]
        if any(m.levier in LEVIERS_INTERNES for m in mesures):
            raise ErreurV1(422, "mesure_invalide", "Levier interne au site.")
        try:
            for m in mesures:
                module_scenario.effet_solde(m)
            r = module_deciles.repartition(mesures)
        except ValueError as erreur:
            raise ErreurV1(
                422, "mesure_invalide", "Levier inconnu, valeur hors des bornes ou double compte."
            ) from erreur
        return {
            "statut": "beta",
            "unite": "variation du revenu disponible (négatif : baisse)",
            "milliards_euros": [base._fourchette(f) for f in r.milliards],
            "euros_par_unite_de_consommation": [base._fourchette(f) for f in r.euros_par_uc],
            "pourcent_revenu_disponible": [base._fourchette(f) for f in r.pourcent_revenu],
            "non_repartis": r.non_repartis,
            "sources": ["insee_cnd_2023", "insee_budget_de_famille_2017"],
            "version": _version(),
        }

    @api.post("/objectif")
    def route_objectif(entree: ObjectifV1) -> dict[str, Any]:
        """Valeur d'un levier, pris seul, qui amène la dette ou le solde primaire à la cible
        l'année choisie, pour chaque borne des hypothèses. Aucun levier n'est proposé."""
        if entree.levier not in leviers_publics() or entree.annee < entree.entree:
            raise ErreurV1(
                422, "objectif_invalide", "Levier inconnu ou année de l'objectif avant l'entrée."
            )
        objectif = module_objectif.Objectif(entree.indicateur, entree.annee, entree.cible)
        try:
            s = module_objectif.resoudre(entree.levier, entree.entree, objectif)
        except ValueError as erreur:
            raise ErreurV1(
                422, "objectif_invalide", "Objectif hors du domaine calculé."
            ) from erreur
        f = module_objectif.fourchette_valeur(s)
        return {
            "levier": entree.levier,
            "valeur": None if f is None else base._fourchette(f),
            "valeur_par_borne": s.par_borne,
            "atteignable": f is not None,
            "sans_mesure": s.sans_mesure,
            "unite_indicateur": "% du PIB",
            "version": _version(),
        }

    @api.get("/baseline")
    def route_baseline() -> dict[str, Any]:
        """Trajectoire sans mesure, 2025-2046, en fourchette."""
        return base.serie_baseline()

    @api.get("/validation")
    def route_validation() -> list[dict[str, Any]]:
        """Écarts du modèle aux chiffrages de référence, y compris hors tolérance."""
        return base.resume_validation()

    @api.get("/registres/{nom}")
    def route_registre(nom: str) -> list[dict[str, Any]]:
        """Registres : sources, jeux de données, hypothèses, leviers, chiffrages."""
        contenu = base.registre(nom)
        if contenu is None:
            raise ErreurV1(404, "registre_inconnu", "Registre inconnu.")
        return contenu

    @api.get("/depenses-fiscales")
    def route_depenses_fiscales() -> dict[str, Any]:
        """Dépenses fiscales réglables une à une (levier ``depense_fiscale_<code>``)."""
        return base.catalogue_depenses_fiscales()

    @api.get("/credits-missions")
    def route_credits_missions() -> dict[str, Any]:
        """Missions de l'État réglables une à une (levier ``credits_mission_<identifiant>``)."""
        return base.catalogue_credits_missions()

    return api
