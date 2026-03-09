from __future__ import annotations

from typing import Iterable


def join_context_blocks(blocks: Iterable[str]) -> str:
    blocks_list = list(blocks)
    if not blocks_list:
        return "(aucun contexte trouvé)"
    return "\n\n---\n\n".join(blocks_list)


def chat_prompt(question: str, context: str) -> str:
    return (
        "Tu es un assistant IA local pour développeurs. Réponds en français de manière concise et précise.\n\n"
        "Question utilisateur:\n"
        f"{question}\n\n"
        "Contexte code (extraits) :\n"
        f"{context}\n\n"
        "Si le contexte est insuffisant, explique ce qui manque et propose où chercher."
    )


def doc_prompt(stats_text: str, file_list: str, context: str) -> str:
    return (
        "Tu es un assistant IA local pour développeurs. Produis une documentation technique complète en Markdown.\n"
        "La documentation doit inclure :\n"
        "1) Un README technique (installation, lancement, structure, conventions).\n"
        "2) Une section d'architecture (modules principaux, flux).\n"
        "3) Une section par module/fichier important (responsabilité, points clés).\n"
        "4) Points d'amélioration et limites connues.\n\n"
        "Contexte projet (stats JSON) :\n"
        f"{stats_text}\n\n"
        "Liste des fichiers :\n"
        f"{file_list}\n\n"
        "Extraits de code :\n"
        f"{context}\n\n"
        "Réponds uniquement en Markdown, sans bloc de code pour le markdown complet."
    )


def test_prompt(target: str, framework: str, context: str) -> str:
    return (
        "Tu es un assistant IA local pour développeurs. Génère des tests unitaires en Python.\n"
        "Contraintes :\n"
        "- Utiliser pytest.\n"
        "- Écrire du vrai code, pas de pseudocode.\n"
        "- Ajouter des mocks si nécessaire (pytest-mock ou unittest.mock).\n"
        "- Couvrir les cas normaux et au moins un cas d'erreur.\n"
        "- Répondre uniquement avec le fichier de tests en code Python.\n\n"
        f"Cible: {target}\n"
        f"Framework: {framework}\n\n"
        "Contexte code (extraits):\n"
        f"{context}\n"
    )


def refactor_prompt(target: str, style: str, context: str) -> str:
    return (
        "Tu es un assistant IA local pour développeurs. Analyse le code et propose des refactors.\n"
        "Contraintes :\n"
        "- Retourner des suggestions concrètes, priorisées.\n"
        "- Fournir un patch diff unifié si possible.\n"
        "- Ne pas exécuter de code.\n"
        "- Être prudent et justifier les changements.\n\n"
        f"Cible: {target}\n"
        f"Style: {style}\n\n"
        "Contexte code (extraits):\n"
        f"{context}\n"
    )
