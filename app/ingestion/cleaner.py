import re


class DocumentCleaner:
    def clean(self, doc: dict) -> dict:
        text = doc.get("text", "") or ""
        # normalize spaces/newlines
        text = text.replace("\r\n", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        doc["text"] = text
        return doc
