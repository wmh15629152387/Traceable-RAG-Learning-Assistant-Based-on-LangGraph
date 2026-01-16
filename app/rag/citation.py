from pydantic import BaseModel


class Evidence(BaseModel):
    chunk_id: str
    doc_id: str
    doc_title: str
    locator: str | None = None  # page/section
    text: str
    score: float


def format_citations(evidences: list[Evidence]) -> list[dict]:
    """Return API-friendly citations."""
    return [
        {
            "chunk_id": e.chunk_id,
            "doc_id": e.doc_id,
            "doc_title": e.doc_title,
            "locator": e.locator,
            "score": round(float(e.score), 4),
            "text": e.text,
        }
        for e in evidences
    ]
