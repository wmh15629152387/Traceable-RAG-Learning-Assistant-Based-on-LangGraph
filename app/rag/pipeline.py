import logging
from app.rag.query_parser import QueryParser
from app.rag.retriever import HybridRetriever
from app.rag.reranker import SimpleReranker
from app.rag.generator import AnswerGenerator
from app.rag.self_check import SelfCheck
from app.rag.citation import format_citations

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(
        self,
        retriever: HybridRetriever,
        reranker: SimpleReranker,
        generator: AnswerGenerator,
        self_check: SelfCheck,
        graph,
        default_top_k: int = 8,
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.generator = generator
        self.self_check = self_check
        self.graph = graph
        self.default_top_k = default_top_k
        self.qp = QueryParser()

    def answer(
        self,
        query: str,
        session_id: str | None = None,
        top_k: int | None = None,
        allow_general_knowledge: bool = True,
        max_loops: int = 2,
    ) -> dict:
        top_k = top_k or self.default_top_k

        # Use LangGraph if available; fallback to local run.
        if self.graph is not None:
            state = {
                "query": query,
                "session_id": session_id,
                "top_k": top_k,
                "allow_general_knowledge": allow_general_knowledge,
                "max_loops": max_loops,
            }
            out = self.graph.invoke(state)
            return out

        logger.warning("LangGraph not available; using local pipeline fallback.")
        return self._run_local(query, top_k, allow_general_knowledge, max_loops)

    def _run_local(self, query: str, top_k: int, allow_general_knowledge: bool, max_loops: int) -> dict:
        pq = self.qp.parse(query)
        cur_q = pq.normalized

        evidences = []
        boundary_notice = None

        for loop in range(max_loops + 1):
            retrieved = self.retriever.retrieve(cur_q)
            reranked = self.reranker.rerank(cur_q, retrieved.evidences, top_k=top_k)
            evidences = reranked

            check = self.self_check.check(cur_q, evidences)
            if check.ok:
                boundary_notice = None
                break

            if loop < max_loops:
                pq = self.qp.rewrite(pq, check.hint)
                cur_q = pq.rewritten or cur_q
                continue

            boundary_notice = "资料未涉及或覆盖不足：以下回答将基于通用知识补充说明（请自行核对）。"
            break

        gen = self.generator.generate(
            query=query,
            evidences=evidences,
            allow_general_knowledge=allow_general_knowledge,
            boundary_notice=boundary_notice if allow_general_knowledge else "资料未涉及或覆盖不足：已按要求不使用通用知识。",
        )

        return {
            "answer": gen["answer"],
            "citations": format_citations(evidences),
            "boundary_notice": gen["boundary_notice"],
            "used_general_knowledge": gen["used_general_knowledge"],
        }
