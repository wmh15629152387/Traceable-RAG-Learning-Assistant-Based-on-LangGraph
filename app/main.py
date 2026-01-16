from fastapi import FastAPI
from app.core.logging import setup_logging
from app.api.chat import router as chat_router
from app.api.ingest import router as ingest_router
from app.api.health import router as health_router


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="Traceable RAG Learning Assistant",
        version="0.1.0",
        description="LangGraph + RAG, traceable citations, self-check and boundary control.",
    )

    app.include_router(health_router, tags=["health"])
    app.include_router(ingest_router, prefix="/api", tags=["ingest"])
    app.include_router(chat_router, prefix="/api", tags=["chat"])
    return app


app = create_app()
