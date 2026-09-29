from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    source: str = Field(min_length=1, max_length=500)
    text: str = Field(min_length=1, max_length=200_000)


class DocumentReceipt(BaseModel):
    document_id: str
    chunks_indexed: int
    pii_redactions: int


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    source: str
    score: float
    excerpt: str


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    top_k: int = Field(default=3, ge=1, le=10)


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    safety_status: str


class EvaluationCase(BaseModel):
    question: str = Field(min_length=3)
    expected_document_id: str


class EvaluationRequest(BaseModel):
    cases: list[EvaluationCase] = Field(min_length=1, max_length=100)
    top_k: int = Field(default=3, ge=1, le=10)


class EvaluationResult(BaseModel):
    question: str
    expected_document_id: str
    rank: int | None
    passed: bool


class EvaluationResponse(BaseModel):
    hit_rate_at_k: float
    mean_reciprocal_rank: float
    results: list[EvaluationResult]
