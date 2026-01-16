from __future__ import annotations
from typing import Any


class SemanticSplitter:
    """
    Simple chunking:
      - split by paragraphs
      - enforce max chars per chunk
    Replace with LangChain text splitters if desired.
    """

    def __init__(self, max_chars: int = 900, overlap: int = 80):
        self.max_chars = max_chars
        self.overlap = overlap

    def split_one(self, doc: dict[str, Any]) -> list[dict[str, Any]]:
        text = doc.get("text", "") or ""
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks: list[str] = []
        cur = ""
        for p in paras:
            if len(cur) + len(p) + 2 <= self.max_chars:
                cur = (cur + "\n\n" + p).strip()
            else:
                if cur:
                    chunks.append(cur)
                cur = p
        if cur:
            chunks.append(cur)

        # add overlap
        out = []
        for i, ch in enumerate(chunks):
            if self.overlap > 0 and i > 0:
                prefix = chunks[i - 1][-self.overlap :]
                ch2 = (prefix + "\n" + ch).strip()
            else:
                ch2 = ch
            out.append(
                {
                    "doc_title": doc.get("doc_title"),
                    "text": ch2,
                    "locator": doc.get("locator"),
                    "source_type": doc.get("source_type"),
                }
            )
        return out

    def split_many(self, docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        res: list[dict[str, Any]] = []
        for d in docs:
            res.extend(self.split_one(d))
        return res
