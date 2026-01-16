from app.core.dependencies import get_self_check
from app.rag.query_parser import QueryParser

_sc = get_self_check()
_qp = QueryParser()


def node_self_check(state: dict) -> dict:
    q = state.get("rewritten_query") or state["query"]
    evidences = state.get("evidences") or []

    check = _sc.check(q, evidences)
    max_loops = int(state.get("max_loops") or 2)
    loop = int(state.get("loop") or 0)

    if check.ok:
        state["boundary_notice"] = None
        state["hint"] = ""
        state["_need_retry"] = False
        return state

    if loop < max_loops:
        # rewrite and retry
        pq = _qp.parse(state["query"])
        pq = _qp.rewrite(pq, check.hint)
        state["rewritten_query"] = pq.rewritten or q
        state["hint"] = check.hint
        state["loop"] = loop + 1
        state["_need_retry"] = True
        return state

    # final: boundary
    allow_general = bool(state.get("allow_general_knowledge", True))
    if allow_general:
        state["boundary_notice"] = "资料未涉及或覆盖不足：以下回答将基于通用知识补充说明（请自行核对）。"
    else:
        state["boundary_notice"] = "资料未涉及或覆盖不足：已按要求不使用通用知识。"
    state["_need_retry"] = False
    return state
