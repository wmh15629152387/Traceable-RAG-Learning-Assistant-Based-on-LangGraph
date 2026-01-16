from app.rag.query_parser import QueryParser

_qp = QueryParser()


def node_parse_query(state: dict) -> dict:
    pq = _qp.parse(state["query"])
    state["rewritten_query"] = pq.normalized
    state["loop"] = 0
    state["hint"] = ""
    return state
