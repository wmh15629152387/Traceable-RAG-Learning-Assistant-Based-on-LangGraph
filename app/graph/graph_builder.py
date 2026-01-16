import logging

logger = logging.getLogger(__name__)


def build_graph():
    """
    Build LangGraph:
      parse_query -> retrieve -> self_check
         if need_retry: retrieve -> self_check (loop)
         else: generate -> end
    """
    try:
        from langgraph.graph import StateGraph, END  # type: ignore
    except Exception as e:
        logger.warning("LangGraph import failed, fallback to local pipeline. err=%s", e)
        return None

    from app.graph.state import GraphState
    from app.graph.nodes.parse_query import node_parse_query
    from app.graph.nodes.retrieve import node_retrieve
    from app.graph.nodes.self_check import node_self_check
    from app.graph.nodes.generate import node_generate

    g = StateGraph(GraphState)
    g.add_node("parse_query", node_parse_query)
    g.add_node("retrieve", node_retrieve)
    g.add_node("self_check", node_self_check)
    g.add_node("generate", node_generate)

    g.set_entry_point("parse_query")
    g.add_edge("parse_query", "retrieve")
    g.add_edge("retrieve", "self_check")

    def route_after_check(state: dict) -> str:
        return "retrieve" if state.get("_need_retry") else "generate"

    g.add_conditional_edges("self_check", route_after_check, {"retrieve": "retrieve", "generate": "generate"})
    g.add_edge("generate", END)

    return g.compile()
