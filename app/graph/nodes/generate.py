from app.core.dependencies import get_generator
from app.rag.citation import format_citations

_gen = get_generator()


def node_generate(state: dict) -> dict:
    evidences = state.get("evidences") or []
    allow_general = bool(state.get("allow_general_knowledge", True))

    gen = _gen.generate(
        query=state["query"],
        evidences=evidences,
        allow_general_knowledge=allow_general,
        boundary_notice=state.get("boundary_notice"),
    )

    state["answer"] = gen["answer"]
    state["used_general_knowledge"] = gen["used_general_knowledge"]
    state["citations"] = format_citations(evidences)
    return state
