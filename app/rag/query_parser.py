from dataclasses import dataclass
from app.utils.text import normalize_text


@dataclass
class ParsedQuery:
    original: str
    normalized: str
    intent: str = "qa"  # could extend: "definition", "summary", etc.
    rewritten: str | None = None


class QueryParser:
    def parse(self, query: str) -> ParsedQuery:
        nq = normalize_text(query)
        return ParsedQuery(original=query, normalized=nq)

    def rewrite(self, pq: ParsedQuery, hint: str) -> ParsedQuery:
        # Simple rewrite: append hint keywords. Replace with LLM-based rewrite if desired.
        rewritten = f"{pq.normalized}\n\n[检索提示]{hint}".strip()
        pq.rewritten = rewritten
        return pq
