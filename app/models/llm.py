from __future__ import annotations
import os


class LLMClient:
    def __init__(self, provider: str, model: str, temperature: float = 0.2, openai_api_key: str | None = None):
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        self._impl = None
        if provider == "openai":
            try:
                from langchain_openai import ChatOpenAI  # type: ignore
                self._impl = ChatOpenAI(model=self.model, temperature=self.temperature, api_key=self.openai_api_key)
            except Exception:
                self._impl = None

    def chat(self, system: str, user: str) -> str:
        if self._impl:
            from langchain_core.messages import SystemMessage, HumanMessage  # type: ignore
            resp = self._impl.invoke([SystemMessage(content=system), HumanMessage(content=user)])
            return getattr(resp, "content", str(resp))

        # fallback: dev echo (no real LLM)
        return (
            "（LLM未配置，返回占位输出）\n"
            f"系统提示：{system[:120]}...\n"
            f"用户内容：{user[:400]}...\n"
        )
