from __future__ import annotations
import os
from typing import List


class EmbeddingsClient:
    def __init__(self, provider: str, model: str, openai_api_key: str | None = None):
        self.provider = provider
        self.model = model
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        self._impl = None
        if provider == "openai":
            try:
                from langchain_openai import OpenAIEmbeddings  # type: ignore
                self._impl = OpenAIEmbeddings(model=self.model, api_key=self.openai_api_key)
            except Exception:
                self._impl = None

    def embed_query(self, text: str) -> List[float]:
        if self._impl:
            return list(self._impl.embed_query(text))
        # fallback: deterministic fake embedding (dev only)
        return self._fake_embed(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self._impl:
            return [list(x) for x in self._impl.embed_documents(texts)]
        return [self._fake_embed(t) for t in texts]

    def _fake_embed(self, text: str) -> list[float]:
        # 1536 dims to match common OpenAI embeddings
        import hashlib
        h = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
        base = [b / 255.0 for b in h]
        # repeat to 1536
        out = (base * (1536 // len(base) + 1))[:1536]
        return out
