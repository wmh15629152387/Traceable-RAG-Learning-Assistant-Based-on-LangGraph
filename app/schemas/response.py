from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    answer: str
    citations: list[dict] = Field(default_factory=list)
    boundary_notice: str | None = None
    used_general_knowledge: bool = False


class IngestResponse(BaseModel):
    filename: str
    documents: int
    chunks: int
    inserted: int
