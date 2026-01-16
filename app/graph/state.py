from typing import TypedDict, Any


class GraphState(TypedDict, total=False):
    query: str
    rewritten_query: str
    hint: str

    top_k: int
    allow_general_knowledge: bool
    max_loops: int
    loop: int

    evidences: list[Any]        # Evidence list (pydantic models -> Any to keep graph minimal)
    boundary_notice: str | None

    answer: str
    citations: list[dict]
    used_general_knowledge: bool

    session_id: str | None
