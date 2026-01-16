from fastapi import APIRouter, Depends
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse
from app.core.dependencies import get_rag_pipeline

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, pipeline=Depends(get_rag_pipeline)) -> ChatResponse:
    result = pipeline.answer(
        query=req.query,
        session_id=req.session_id,
        top_k=req.top_k,
        allow_general_knowledge=req.allow_general_knowledge,
        max_loops=req.max_loops,
    )
    return ChatResponse(**result)
