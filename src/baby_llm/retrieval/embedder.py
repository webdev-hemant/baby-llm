"""Local embedding generation using FastEmbed (ONNX BAAI/bge-small-en-v1.5)."""

from typing import List
import numpy as np
from fastembed import TextEmbedding
from baby_llm.config import settings


class LocalEmbedder:
    _instance = None

    def __init__(self, model_name: str = settings.embedding_model):
        self.model_name = model_name
        self._model = TextEmbedding(model_name=model_name)

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string into a 384-dim normalized vector."""
        generator = self._model.embed([text])
        return list(next(generator))

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings."""
        if not texts:
            return []
        generator = self._model.embed(texts)
        return [list(vec) for vec in generator]


_embedder_instance = None


def get_embedder() -> LocalEmbedder:
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = LocalEmbedder()
    return _embedder_instance
