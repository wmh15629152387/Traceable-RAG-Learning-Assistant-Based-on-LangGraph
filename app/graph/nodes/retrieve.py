from app.core.dependencies import get_retriever, get_reranker, get_settings

_retriever = get_retriever()
_reranker = get_reranker()
_settings = get_settings()


def node_retrieve(state: dict) -> dict:
    q = state.get("rewritten_query") or state["query"]
    top_k = int(state.get("top_k") or _settings.default_top_k)

    retrieved = _retriever.retrieve(q)
    reranked = _reranker.rerank(q, retrieved.evidences, top_k=top_k)
    state["evidences"] = reranked
    return state
