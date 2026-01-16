from dataclasses import dataclass
from app.rag.citation import Evidence
from app.utils.text import tokenize
from app.storage.vector_store import VectorStore
from app.models.embeddings import EmbeddingsClient


@dataclass
class Retrieved:
    evidences: list[Evidence]


class HybridRetriever:
    """
    Hybrid retrieval:
      - vector retrieval (pgvector similarity)
      - keyword retrieval (simple TS query / fallback ILIKE)
    """

    def __init__(self, vector_store: VectorStore, embeddings: EmbeddingsClient, vector_top_k: int = 12, bm25_top_k: int = 12):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.vector_top_k = vector_top_k
        self.bm25_top_k = bm25_top_k

    def retrieve(self, query: str) -> Retrieved:
        q_emb = self.embeddings.embed_query(query)

        vec_hits = self.vector_store.search_by_vector(q_emb, top_k=self.vector_top_k)
        kw_tokens = tokenize(query)
        kw_hits = self.vector_store.search_by_keyword(" ".join(kw_tokens), top_k=self.bm25_top_k)

        # Merge unique by chunk_id, keep best score
        by_id: dict[str, Evidence] = {}
        for hit in (vec_hits + kw_hits):
            if hit.chunk_id not in by_id or hit.score > by_id[hit.chunk_id].score:
                by_id[hit.chunk_id] = hit

        evidences = sorted(by_id.values(), key=lambda e: e.score, reverse=True)
        return Retrieved(evidences=evidences)
