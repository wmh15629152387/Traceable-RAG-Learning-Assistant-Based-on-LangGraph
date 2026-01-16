from dataclasses import dataclass
from app.ingestion.loader import DocumentLoader
from app.ingestion.cleaner import DocumentCleaner
from app.ingestion.splitter import SemanticSplitter
from app.ingestion.metadata import MetadataBuilder
from app.models.embeddings import EmbeddingsClient
from app.storage.vector_store import VectorStore


@dataclass
class Ingestor:
    loader: DocumentLoader
    cleaner: DocumentCleaner
    splitter: SemanticSplitter
    metadata: MetadataBuilder
    embeddings: EmbeddingsClient
    vector_store: VectorStore

    def ingest_bytes(self, filename: str, data: bytes, content_type: str) -> dict:
        docs = self.loader.load_bytes(filename=filename, data=data, content_type=content_type)
        cleaned = [self.cleaner.clean(d) for d in docs]
        chunks = self.splitter.split_many(cleaned)
        enriched = [self.metadata.enrich(c) for c in chunks]

        # embeddings
        texts = [c["text"] for c in enriched]
        vecs = self.embeddings.embed_documents(texts)

        # store
        inserted = self.vector_store.upsert_chunks(enriched, vecs)

        return {
            "filename": filename,
            "documents": len(docs),
            "chunks": len(enriched),
            "inserted": inserted,
        }
