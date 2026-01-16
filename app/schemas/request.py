from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., description="User question")
    session_id: str | None = Field(default=None)
    top_k: int | None = Field(default=None, ge=1, le=50)
    allow_general_knowledge: bool = Field(default=True, description="If evidence insufficient, allow general knowledge supplement")
    max_loops: int = Field(default=2, ge=0, le=5, description="Max self-check retry loops")
