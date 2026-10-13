"""Configuration management for Baby LLM."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BABY_LLM_",
        env_file=".env",
        extra="ignore"
    )

    # Base Directories
    app_dir: Path = Path.home() / ".baby_llm"
    db_filename: str = "baby_llm.sqlite3"
    lancedb_dirname: str = "lancedb"
    vault_dirname: str = "vault"

    # Server / REST API Settings (21225 spells 'BABY': B=2, A=1, B=2, Y=25)
    api_host: str = "127.0.0.1"
    api_port: int = 21225

    # Embedded Local Inference Settings (100% Standalone / Zero Daemon)
    embedded_model_repo: str = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
    embedded_model_filename: str = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
    embedded_model_n_ctx: int = 2048
    embedded_model_n_threads: int = 4
    embedded_model_n_gpu_layers: int = 0
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dimension: int = 384

    # Dream Engine Settings
    idle_trigger_seconds: int = 900  # 15 minutes
    dream_cron_hour: int = 3         # 3:00 AM

    # Episodic Ring Buffer
    ring_buffer_size: int = 15

    # Retrieval Settings
    hybrid_top_k: int = 5
    rrf_k_constant: int = 60

    # Success Agent Settings
    morning_brief_hour: int = 7
    morning_brief_minute: int = 30
    evening_reflect_hour: int = 21
    evening_reflect_minute: int = 30

    @property
    def db_path(self) -> Path:
        return self.app_dir / self.db_filename

    @property
    def lancedb_path(self) -> Path:
        return self.app_dir / self.lancedb_dirname

    @property
    def vault_path(self) -> Path:
        return self.app_dir / self.vault_dirname

    def ensure_directories(self) -> None:
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.lancedb_path.mkdir(parents=True, exist_ok=True)
        self.vault_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
