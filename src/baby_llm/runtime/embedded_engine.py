"""Embedded zero-daemon LLM engine running Qwen2.5-0.5B-Instruct via llama-cpp-python."""

import os
import sys
import threading
import warnings
from pathlib import Path
from typing import Generator, List, Optional

# Suppress unauthenticated Hugging Face Hub rate-limit warnings for public models
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")

try:
    from huggingface_hub.utils import logging as hf_logging
    hf_logging.set_verbosity_error()
except Exception:
    pass

from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from baby_llm.config import settings


DEFAULT_REPO_ID = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
DEFAULT_FILENAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"


class EmbeddedLLMEngine:
    def __init__(
        self,
        repo_id: Optional[str] = None,
        filename: Optional[str] = None,
        n_ctx: Optional[int] = None,
        n_gpu_layers: Optional[int] = None,
        n_threads: Optional[int] = None,
    ):
        self.repo_id = repo_id or getattr(settings, "embedded_model_repo", DEFAULT_REPO_ID)
        self.filename = filename or getattr(settings, "embedded_model_filename", DEFAULT_FILENAME)
        self.n_ctx = n_ctx if n_ctx is not None else getattr(settings, "embedded_model_n_ctx", 2048)
        self.n_gpu_layers = n_gpu_layers if n_gpu_layers is not None else getattr(settings, "embedded_model_n_gpu_layers", 0)
        self.n_threads = n_threads if n_threads is not None else getattr(settings, "embedded_model_n_threads", 4)
        self._llm: Optional[Llama] = None
        self._model_path: Optional[str] = None
        self._lock = threading.Lock()

    def ensure_model(self) -> str:
        """Download (if needed) and return path to GGUF model."""
        with self._lock:
            if self._model_path and os.path.exists(self._model_path):
                return self._model_path

            print(f"📥 Loading embedded model: {self.filename} (~398 MB)...", flush=True)
            self._model_path = hf_hub_download(
                repo_id=self.repo_id,
                filename=self.filename,
            )
            return self._model_path

    def get_llm(self) -> Llama:
        """Thread-safe singleton initialization of Llama instance."""
        with self._lock:
            if self._llm is None:
                if not self._model_path:
                    # Releases lock temporarily to download if needed
                    pass
            if self._llm is None:
                model_path = self._model_path or hf_hub_download(
                    repo_id=self.repo_id,
                    filename=self.filename,
                )
                self._model_path = model_path
                self._llm = Llama(
                    model_path=model_path,
                    n_ctx=self.n_ctx,
                    n_threads=self.n_threads,
                    n_gpu_layers=self.n_gpu_layers,
                    verbose=False,
                )
            return self._llm

    def chat_sync(
        self,
        messages: List[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Thread-safe synchronous chat completion."""
        llm = self.get_llm()
        with self._lock:
            response = llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response["choices"][0]["message"]["content"].strip()

    def stream_chat_sync(
        self,
        messages: List[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> Generator[str, None, None]:
        """Thread-safe stream chunks."""
        llm = self.get_llm()
        with self._lock:
            response = llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            for chunk in response:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    yield delta["content"]


embedded_engine = EmbeddedLLMEngine()
