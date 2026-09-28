"""Embedded zero-daemon LLM engine running Qwen2.5-0.5B-Instruct via llama-cpp-python."""

import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator, List, Optional
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from baby_llm.config import settings


DEFAULT_REPO_ID = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
DEFAULT_FILENAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"


class EmbeddedLLMEngine:
    def __init__(
        self,
        repo_id: str = DEFAULT_REPO_ID,
        filename: str = DEFAULT_FILENAME,
        n_ctx: int = 4096,
        n_gpu_layers: int = 0,  # 0 runs cleanly on CPU with zero Metal driver teardown issues
    ):
        self.repo_id = repo_id
        self.filename = filename
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self._llm: Optional[Llama] = None
        self._model_path: Optional[str] = None

    def ensure_model(self) -> str:
        """Download (if needed) and return path to GGUF model."""
        if self._model_path and os.path.exists(self._model_path):
            return self._model_path

        print(f"📥 Loading embedded model: {self.filename} (~398 MB)...", flush=True)
        self._model_path = hf_hub_download(
            repo_id=self.repo_id,
            filename=self.filename,
        )
        return self._model_path

    def get_llm(self) -> Llama:
        """Lazy initialization of Llama instance."""
        if self._llm is None:
            model_path = self.ensure_model()
            # Suppress noisy C++ stdout on init
            self._llm = Llama(
                model_path=model_path,
                n_ctx=self.n_ctx,
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
        """Synchronous chat completion."""
        llm = self.get_llm()
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
        """Stream chunks synchronously."""
        llm = self.get_llm()
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
