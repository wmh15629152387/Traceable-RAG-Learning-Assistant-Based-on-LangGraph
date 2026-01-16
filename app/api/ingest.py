from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas.response import IngestResponse
from app.core.dependencies import get_ingestor

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...), ingestor=Depends(get_ingestor)) -> IngestResponse:
    content = await file.read()
    report = ingestor.ingest_bytes(
        filename=file.filename or "upload.bin",
        data=content,
        content_type=file.content_type or "application/octet-stream",
    )
    return IngestResponse(**report)
