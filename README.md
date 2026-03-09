# DevLocal AI

Assistant IA local pour développeurs utilisant Ollama. L'application analyse un projet, indexe le code et fournit des fonctionnalités de chat, documentation, tests et refactor.

## Prérequis
- Python 3.12 à 3.13 recommandé (3.14 nécessite des ajustements pour pydantic-core)
- Ollama installé localement
- Modèles : `deepseek-coder:6.7b`, `qwen2.5-coder:7b`

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Note Python 3.14 : pydantic-core peut échouer à compiler. Dans ce cas, utilisez Python 3.12/3.13.

## Configuration
Copier `.env.example` en `.env` puis ajuster si nécessaire.

Variables principales :
- `OLLAMA_URL` (par défaut `http://localhost:11434`)
- `MODEL_CODE` (par défaut `deepseek-coder:6.7b`)
- `MODEL_REASONING` (par défaut `qwen2.5-coder:7b`)
- `IGNORE_FILES` (par défaut `.env,.env.*,*.env`)

## Lancement
```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

## API
- `GET /health`
- `POST /chat`
- `POST /docs/generate`
- `POST /tests/generate`
- `POST /refactor/suggest`
- `POST /projects/index`
- `GET /projects/{id}/stats`
- `GET /projects/{id}/tree`
- `GET /` (UI locale)

## UI
Ouvrir `http://127.0.0.1:8000/`.

## Tests
```bash
source .venv/bin/activate
pytest
```

## Docs
Voir `docs/ARCHITECTURE.md`.
