# DevLocal AI - Architecture

## Vue d'ensemble
DevLocal AI est un assistant local qui analyse et indexe un projet, puis fournit des fonctionnalités de chat, documentation, tests et refactors via une API FastAPI.

## Modules principaux
- **app/services** : orchestration des cas d'usage (scan, indexation, chat, docs, tests, refactor).
- **app/repositories** : accès SQLite, index FTS et stats.
- **app/llm** : client Ollama et sélection du modèle par tâche.
- **app/indexers** : découpage des fichiers en chunks.
- **app/utils** : utilitaires (hash, taille, détection binaire, langage).

## Flux clés
- **Scan -> Index** : scan fichiers → métadonnées → chunks → stockage SQLite + FTS + stats.
- **Chat** : requête utilisateur → recherche FTS → contexte → LLM (qwen2.5-coder).
- **Docs/Tests/Refactor** : récupération contexte → prompt spécialisé → LLM (deepseek-coder).

## Données
- **SQLite** : tables `projects`, `files`, `chunks`, `chunks_fts`, `stats`.
- **FTS5** : recherche texte pour extraire des passages de code.

## Sécurité
- Pas d'exécution de code.
- Limite taille fichier et détection binaire.
- Pas d'accès internet requis.
