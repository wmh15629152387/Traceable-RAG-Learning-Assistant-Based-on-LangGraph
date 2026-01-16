from app.rag.citation import Evidence
from app.models.llm import LLMClient


class AnswerGenerator:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(
        self,
        query: str,
        evidences: list[Evidence],
        allow_general_knowledge: bool,
        boundary_notice: str | None = None,
    ) -> dict:
        evidence_block = "\n\n".join(
            [
                f"[{i+1}] {e.doc_title} ({e.locator or 'unknown'})\n{e.text}"
                for i, e in enumerate(evidences)
            ]
        )

        system = (
            "你是一个严谨的学习助手。优先使用用户资料回答，并为每个结论提供可追溯证据。"
            "当证据不足时，必须明确标注资料边界。"
        )
        user = f"""
用户问题：
{query}

可用证据（必须优先引用）：
{evidence_block if evidence_block else "(无)"}

要求：
1) 回答尽量基于证据；引用时用 [1][2]... 标注
2) 若资料未覆盖或覆盖不足：先明确写“资料未涉及/覆盖不足”，再（如果允许）用通用知识补充，并明确这是通用知识
3) 不要编造不存在的页码/章节，引用仅来自证据
"""

        text = self.llm.chat(system=system, user=user)

        used_general = False
        if boundary_notice and "资料未涉及" in boundary_notice:
            used_general = allow_general_knowledge

        return {
            "answer": text.strip(),
            "boundary_notice": boundary_notice,
            "used_general_knowledge": used_general,
        }
