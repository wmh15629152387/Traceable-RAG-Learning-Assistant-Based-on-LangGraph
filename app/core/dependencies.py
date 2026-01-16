from functools import lru_cache
from app.core.config import get_settings
from app.storage.postgres import PostgresClient
from app.storage.vector_store import VectorStore
from app.models.embeddings import EmbeddingsClient
from app.models.llm import LLMClient
from app.ingestion.loader import DocumentLoader
from app.ingestion.cleaner import DocumentCleaner
from app.ingestion.splitter import SemanticSplitter
from app.ingestion.metadata import MetadataBuilder
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import HybridRetriever
from app.rag.reranker import SimpleReranker
from app.rag.generator import AnswerGenerator
from app.rag.self_check import SelfCheck
from app.graph.graph_builder import build_graph
from app.ingestion import Ingestor


@lru_cache
def get_db() -> PostgresClient:
    s = get_settings()
    return PostgresClient(dsn=s.postgres_dsn)


@lru_cache
def get_vector_store() -> VectorStore:
    db = get_db()
    return VectorStore(db=db)


@lru_cache
def get_embeddings() -> EmbeddingsClient:
    s = get_settings()
    return EmbeddingsClient(provider=s.embeddings_provider, model=s.embeddings_model, openai_api_key=s.openai_api_key)


@lru_cache
def get_llm() -> LLMClient:
    s = get_settings()
    return LLMClient(
        provider=s.llm_provider,
        model=s.llm_model,
        temperature=s.llm_temperature,
        openai_api_key=s.openai_api_key,
    )


@lru_cache
def get_retriever() -> HybridRetriever:
    s = get_settings()
    return HybridRetriever(
        vector_store=get_vector_store(),
        embeddings=get_embeddings(),
        vector_top_k=s.vector_top_k,
        bm25_top_k=s.bm25_top_k,
    )


@lru_cache
def get_reranker() -> SimpleReranker:
    return SimpleReranker()


@lru_cache
def get_generator() -> AnswerGenerator:
    return AnswerGenerator(llm=get_llm())


@lru_cache
def get_self_check() -> SelfCheck:
    s = get_settings()
    return SelfCheck(min_items=s.min_evidence_items, min_max_score=s.min_max_score)


@lru_cache
def get_langgraph():
    # Build once, reuse.
    return build_graph()


@lru_cache
def get_rag_pipeline() -> RAGPipeline:
    s = get_settings()
    pipeline = RAGPipeline(
        retriever=get_retriever(),
        reranker=get_reranker(),
        generator=get_generator(),
        self_check=get_self_check(),
        graph=get_langgraph(),
        default_top_k=s.default_top_k,
    )
    return pipeline


@lru_cache
def get_ingestor() -> "Ingestor":
    return Ingestor(
        loader=DocumentLoader(),
        cleaner=DocumentCleaner(),
        splitter=SemanticSplitter(),
        metadata=MetadataBuilder(),
        embeddings=get_embeddings(),
        vector_store=get_vector_store(),
    )
