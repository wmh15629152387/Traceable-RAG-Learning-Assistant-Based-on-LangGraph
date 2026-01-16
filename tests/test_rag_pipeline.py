from app.rag.pipeline import RAGPipeline
from app.rag.retriever import HybridRetriever
from app.rag.reranker import SimpleReranker
from app.rag.generator import AnswerGenerator
from app.rag.self_check import SelfCheck
from app.storage.vector_store import VectorStore
from app.storage.postgres import PostgresClient
from app.models.embeddings import EmbeddingsClient
from app.models.llm import LLMClient


def test_pipeline_smoke():
    db = PostgresClient("postgresql://postgres:postgres@localhost:5432/rag")
    vs = VectorStore(db)
    emb = EmbeddingsClient(provider="openai", model="text-embedding-3-small")
    llm = LLMClient(provider="openai", model="gpt-4o-mini")

    pipeline = RAGPipeline(
        retriever=HybridRetriever(vs, emb),
        reranker=SimpleReranker(),
        generator=AnswerGenerator(llm),
        self_check=SelfCheck(),
        graph=None,  # local fallback
        default_top_k=5,
    )

    res = pipeline.answer("解释一下 LangGraph 的优势", max_loops=1)
    assert "answer" in res
