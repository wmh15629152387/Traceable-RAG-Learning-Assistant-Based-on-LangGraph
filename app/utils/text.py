import re


def normalize_text(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def tokenize(s: str) -> list[str]:
    s = s.lower()
    # keep chinese chars + alnum
    tokens = re.findall(r"[\u4e00-\u9fff]+|[a-z0-9]+", s)
    return tokens
