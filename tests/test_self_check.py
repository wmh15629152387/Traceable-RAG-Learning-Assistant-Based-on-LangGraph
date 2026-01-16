from app.rag.self_check import SelfCheck
from app.rag.citation import Evidence


def test_self_check_rules():
    sc = SelfCheck(min_items=2, min_max_score=0.3)
    evs = [
        Evidence(chunk_id="1", doc_id="d", doc_title="t", locator="p:1", text="RAG 是检索增强生成", score=0.4),
        Evidence(chunk_id="2", doc_id="d", doc_title="t", locator="p:2", text="它结合检索与生成", score=0.35),
    ]
    r = sc.check("什么是RAG", evs)
    assert r.ok is True
