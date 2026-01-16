from app.rag.citation import Evidence
from app.utils.text import tokenize


class SimpleReranker:
    """
    Lightweight reranker:
      - keep vector score base
      - add keyword overlap bonus
    Replace with a cross-encoder / LLM rerank if needed.
    """

    def rerank(self, query: str, evidences: list[Evidence], top_k: int) -> list[Evidence]:
        q_tokens = set(tokenize(query))
        rescored: list[tuple[float, Evidence]] = []

        for e in evidences:
            e_tokens = set(tokenize(e.text))
            overlap = len(q_tokens & e_tokens) / max(1, len(q_tokens))
            score = float(e.score) * 0.8 + overlap * 0.2
            rescored.append((score, e))

        rescored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in rescored[:top_k]]
