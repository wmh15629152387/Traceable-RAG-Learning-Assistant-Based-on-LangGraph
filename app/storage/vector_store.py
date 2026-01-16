from __future__ import annotations
import json
from app.storage.postgres import PostgresClient
from app.rag.citation import Evidence


class VectorStore:
    """
    PostgreSQL + pgvector recommended.
    Table: chunks(chunk_id, doc_id, doc_title, locator, text, meta_json, embedding vector)
    """

    def __init__(self, db: PostgresClient):
        self.db = db
        self._ensure_schema()

    def _ensure_schema(self):
        # best-effort create; requires pgvector extension for true vector ops
        sql = """
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            doc_id TEXT NOT NULL,
            doc_title TEXT NOT NULL,
            locator TEXT,
            text TEXT NOT NULL,
            meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
            embedding vector(1536)
        );

        CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
        """
        try:
            self.db.execute(sql)
        except Exception:
            # allow running even if vector extension not installed (dev)
            pass

    def upsert_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> int:
        inserted = 0
        for c, emb in zip(chunks, embeddings):
            meta = {
                "source_type": c.get("source_type"),
            }
            sql = """
            INSERT INTO chunks(chunk_id, doc_id, doc_title, locator, text, meta_json, embedding)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (chunk_id) DO UPDATE SET
                doc_id=EXCLUDED.doc_id,
                doc_title=EXCLUDED.doc_title,
                locator=EXCLUDED.locator,
                text=EXCLUDED.text,
                meta_json=EXCLUDED.meta_json,
                embedding=EXCLUDED.embedding;
            """
            try:
                self.db.execute(
                    sql,
                    (
                        c["chunk_id"],
                        c["doc_id"],
                        c["doc_title"],
                        c.get("locator"),
                        c["text"],
                        json.dumps(meta),
                        emb,
                    ),
                )
                inserted += 1
            except Exception:
                # If pgvector not available, store without embedding
                sql2 = """
                INSERT INTO chunks(chunk_id, doc_id, doc_title, locator, text, meta_json)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    doc_id=EXCLUDED.doc_id,
                    doc_title=EXCLUDED.doc_title,
                    locator=EXCLUDED.locator,
                    text=EXCLUDED.text,
                    meta_json=EXCLUDED.meta_json;
                """
                self.db.execute(
                    sql2,
                    (
                        c["chunk_id"],
                        c["doc_id"],
                        c["doc_title"],
                        c.get("locator"),
                        c["text"],
                        json.dumps(meta),
                    ),
                )
                inserted += 1
        return inserted

    def search_by_vector(self, query_emb: list[float], top_k: int = 10) -> list[Evidence]:
        # pgvector distance: embedding <-> %s
        sql = """
        SELECT chunk_id, doc_id, doc_title, locator, text,
               1.0 / (1.0 + (embedding <-> %s)) AS score
        FROM chunks
        WHERE embedding IS NOT NULL
        ORDER BY embedding <-> %s
        LIMIT %s;
        """
        try:
            rows = self.db.fetchall(sql, (query_emb, query_emb, top_k))
            return [
                Evidence(
                    chunk_id=r[0],
                    doc_id=r[1],
                    doc_title=r[2],
                    locator=r[3],
                    text=r[4],
                    score=float(r[5]),
                )
                for r in rows
            ]
        except Exception:
            return []

    def search_by_keyword(self, query: str, top_k: int = 10) -> list[Evidence]:
        # Prefer full-text if available; fallback to ILIKE
        sql_ts = """
        SELECT chunk_id, doc_id, doc_title, locator, text,
               ts_rank(to_tsvector('simple', text), plainto_tsquery('simple', %s)) AS score
        FROM chunks
        WHERE to_tsvector('simple', text) @@ plainto_tsquery('simple', %s)
        ORDER BY score DESC
        LIMIT %s;
        """
        try:
            rows = self.db.fetchall(sql_ts, (query, query, top_k))
            return [
                Evidence(
                    chunk_id=r[0],
                    doc_id=r[1],
                    doc_title=r[2],
                    locator=r[3],
                    text=r[4],
                    score=float(r[5]),
                )
                for r in rows
            ]
        except Exception:
            sql_like = """
            SELECT chunk_id, doc_id, doc_title, locator, text,
                   0.2 AS score
            FROM chunks
            WHERE text ILIKE %s
            LIMIT %s;
            """
            rows = self.db.fetchall(sql_like, (f"%{query}%", top_k))
            return [
                Evidence(
                    chunk_id=r[0],
                    doc_id=r[1],
                    doc_title=r[2],
                    locator=r[3],
                    text=r[4],
                    score=float(r[5]),
                )
                for r in rows
            ]
