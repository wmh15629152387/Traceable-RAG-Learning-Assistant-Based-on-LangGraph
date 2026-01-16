from app.rag.retriever import HybridRetriever
from app.storage.vector_store import VectorStore
from app.storage.postgres import PostgresClient
from app.models.embeddings import EmbeddingsClient


def test_retriever_smoke():
    db = PostgresClient("postgresql://postgres:postgres@localhost:5432/rag")
    vs = VectorStore(db)
    emb = EmbeddingsClient(provider="openai", model="text-embedding-3-small")
    r = HybridRetriever(vs, emb)

    out = r.retrieve("什么是RAG？")
    assert hasattr(out, "evidences")
