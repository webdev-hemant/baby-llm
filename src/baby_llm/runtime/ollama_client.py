"""Ollama streaming bridge for local inference."""

import json
from typing import AsyncGenerator, List, Optional
import httpx
from baby_llm.config import settings


class OllamaClient:
    def __init__(self, base_url: str = settings.ollama_base_url, model: str = settings.chat_model):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def is_available(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/version")
                return res.status_code == 200
        except Exception:
            return False

    async def stream_chat(
        self,
        messages: List[dict],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks token-by-token from Ollama."""
        target_model = model or self.model
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    error_detail = await response.aread()
                    raise RuntimeError(f"Ollama error {response.status_code}: {error_detail.decode('utf-8')}")

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
                    except json.JSONDecodeError:
                        continue

    def chat_sync(
        self,
        messages: List[dict],
        model: Optional[str] = None,
    ) -> str:
        """Synchronous chat completion."""
        target_model = model or self.model
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
        }

        with httpx.Client(timeout=60.0) as client:
            res = client.post(url, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Ollama error {res.status_code}: {res.text}")
            data = res.json()
            return data["message"]["content"]


ollama_client = OllamaClient()
