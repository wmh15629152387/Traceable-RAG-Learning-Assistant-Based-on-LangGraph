from __future__ import annotations
import logging

logger = logging.getLogger(__name__)


class PostgresClient:
    """
    Minimal psycopg3 client.
    You must install: psycopg[binary]
    """

    def __init__(self, dsn: str):
        self.dsn = dsn

    def _connect(self):
        import psycopg  # type: ignore
        return psycopg.connect(self.dsn)

    def execute(self, sql: str, params: tuple | None = None) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
            conn.commit()

    def fetchall(self, sql: str, params: tuple | None = None) -> list[tuple]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                rows = cur.fetchall()
            return rows
