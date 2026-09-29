from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from securerag.models import (
    DocumentCreate,
    DocumentReceipt,
    EvaluationRequest,
    EvaluationResponse,
    QueryRequest,
    QueryResponse,
)
from securerag.security import SafetyGuard, UnsafeInputError
from securerag.services import (
    AnswerGenerationError,
    DocumentIngestor,
    EvaluationService,
    QueryService,
    TfidfRetriever,
    configured_answerer,
)
from securerag.store import InMemoryChunkStore


def create_app() -> FastAPI:
    store = InMemoryChunkStore()
    guard = SafetyGuard()
    ingestor = DocumentIngestor(store, guard)
    query_service = QueryService(TfidfRetriever(store), configured_answerer(), guard)
    evaluator = EvaluationService(query_service)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        store.clear()

    app = FastAPI(
        title="SecureRAG API",
        version="0.1.0",
        description="Citation-aware document retrieval with PII and prompt-injection controls.",
        lifespan=lifespan,
    )

    @app.exception_handler(UnsafeInputError)
    async def unsafe_input_handler(_, exc: UnsafeInputError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc), "safety_status": "blocked"},
        )

    @app.exception_handler(AnswerGenerationError)
    async def answer_generation_error_handler(_, exc: AnswerGenerationError):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)},
        )

    @app.get("/health")
    def health() -> dict[str, str | int]:
        return {"status": "ok", "documents_indexed": store.document_count}

    @app.post("/v1/documents", response_model=DocumentReceipt, status_code=201)
    def add_document(request: DocumentCreate) -> DocumentReceipt:
        return ingestor.ingest(request)

    @app.delete("/v1/documents", status_code=204)
    def clear_documents() -> None:
        store.clear()

    @app.post("/v1/query", response_model=QueryResponse)
    def query(request: QueryRequest) -> QueryResponse:
        if store.document_count == 0:
            raise HTTPException(
                status_code=409, detail="Index at least one document before querying."
            )
        return query_service.query(request.question, request.top_k)

    @app.post("/v1/evaluate", response_model=EvaluationResponse)
    def evaluate(request: EvaluationRequest) -> EvaluationResponse:
        if store.document_count == 0:
            raise HTTPException(
                status_code=409, detail="Index at least one document before evaluation."
            )
        return evaluator.evaluate(request)

    return app


app = create_app()
