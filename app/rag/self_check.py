from dataclasses import dataclass
from app.rag.citation import Evidence
from app.utils.text import tokenize


@dataclass
class CheckResult:
    ok: bool
    reason: str
    hint: str


class SelfCheck:
    """
    Evidence coverage heuristic:
      - require at least min_items evidences
      - require max score above threshold
      - require query keyword overlap above minimal level
    """

    def __init__(self, min_items: int = 3, min_max_score: float = 0.35):
        self.min_items = min_items
        self.min_max_score = min_max_score

    def check(self, query: str, evidences: list[Evidence]) -> CheckResult:
        if not evidences:
            return CheckResult(False, "no_evidence", "请尝试改写问题为更具体的关键术语/课程章节名/概念名。")

        if len(evidences) < self.min_items:
            return CheckResult(False, "too_few_evidence", "证据条目过少：加入更具体关键词（课程名/章节名/术语）重检索。")

        max_score = max(float(e.score) for e in evidences)
        if max_score < self.min_max_score:
            return CheckResult(False, "low_confidence", "证据相似度偏低：尝试改写为定义/公式/步骤等更明确问法。")

        # overlap check
        q = set(tokenize(query))
        best_overlap = 0.0
        for e in evidences[:8]:
            t = set(tokenize(e.text))
            overlap = len(q & t) / max(1, len(q))
            best_overlap = max(best_overlap, overlap)

        if best_overlap < 0.15:
            return CheckResult(False, "low_overlap", "关键词覆盖不足：加入同义词/英文术语/缩写重检索。")

        return CheckResult(True, "ok", "")
