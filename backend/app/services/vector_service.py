from __future__ import annotations

from typing import Dict, List

import numpy as np
from openai import OpenAI

from app.core.config import settings

try:  # pragma: no cover - import depends on runtime platform wheels
    import faiss  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    faiss = None


class FaissVectorStore:
    DIM = 256

    def __init__(self) -> None:
        self._store: Dict[int, str] = {}
        self._index = faiss.IndexFlatL2(self.DIM) if faiss else None
        self._media_ids: List[int] = []
        self._client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def _fallback_embed(self, text: str) -> np.ndarray:
        vec = np.zeros(self.DIM, dtype=np.float32)
        for token in text.lower().split():
            vec[hash(token) % self.DIM] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def _embed(self, text: str) -> np.ndarray:  # pragma: no cover - OpenAI embedding branch
        if not text:
            return np.zeros(self.DIM, dtype=np.float32)
        if not self._client:
            return self._fallback_embed(text)
        embedding = self._client.embeddings.create(model="text-embedding-3-small", input=text)
        vector = np.array(embedding.data[0].embedding, dtype=np.float32)
        if vector.shape[0] > self.DIM:
            return vector[: self.DIM]
        if vector.shape[0] < self.DIM:
            return np.pad(vector, (0, self.DIM - vector.shape[0]), mode="constant")
        return vector

    def upsert(self, media_id: int, text: str) -> None:
        self._store[media_id] = text
        if self._index:  # pragma: no cover - FAISS path is optional in local env
            vector = self._embed(text).reshape(1, -1)
            self._index.add(vector)
            self._media_ids.append(media_id)

    def retrieve(self, media_id: int, query: str) -> str:
        if not self._index or self._index.ntotal == 0:
            return self._store.get(media_id, "")
        return self._retrieve_with_faiss(media_id, query)

    def _retrieve_with_faiss(self, media_id: int, query: str) -> str:  # pragma: no cover - optional path
        query_vector = self._embed(query).reshape(1, -1)  # pragma: no cover - FAISS path
        k = min(5, self._index.ntotal)
        _, indices = self._index.search(query_vector, k)
        candidate_ids = [self._media_ids[idx] for idx in indices[0] if idx >= 0]
        if media_id in candidate_ids:
            return self._store.get(media_id, "")
        return " ".join(self._store.get(candidate_id, "") for candidate_id in candidate_ids).strip()


vector_store = FaissVectorStore()
