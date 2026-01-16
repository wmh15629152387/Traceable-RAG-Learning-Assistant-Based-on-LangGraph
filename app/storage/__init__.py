import uuid


class MetadataBuilder:
    """
    Attach traceable metadata:
      - doc_id: stable per title (you can change to real doc table later)
      - chunk_id: uuid
      - locator: page/slide/section (from loader)
    """

    def enrich(self, chunk: dict) -> dict:
        doc_title = chunk.get("doc_title") or "unknown"
        doc_id = f"doc_{abs(hash(doc_title))}"
        chunk_id = str(uuid.uuid4())
        return {
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "doc_title": doc_title,
            "locator": chunk.get("locator"),
            "source_type": chunk.get("source_type"),
            "text": chunk.get("text", ""),
        }
