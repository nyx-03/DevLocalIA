from __future__ import annotations

from functools import lru_cache
from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(value: str) -> Set[str]:
    return {item.strip() for item in value.split(",") if item.strip()}


class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    model_code: str = "deepseek-coder:6.7b"
    model_reasoning: str = "qwen2.5-coder:7b"
    max_file_size: str = "500kb"
    ignore_dirs: str = ".git,node_modules,venv,dist,build,__pycache__"
    ignore_files: str = ".env,.env.*,*.env"
    db_path: str = "data/devlocal.db"
    chunk_size: int = 1500
    chunk_overlap: int = 200

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def ignore_dir_set(self) -> Set[str]:
        return _split_csv(self.ignore_dirs)

    @property
    def ignore_file_patterns(self) -> Set[str]:
        return _split_csv(self.ignore_files)

    @property
    def max_file_size_bytes(self) -> int:
        from app.utils.file_utils import parse_size_to_bytes

        return parse_size_to_bytes(self.max_file_size)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
