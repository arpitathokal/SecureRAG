from securerag.models import DocumentCreate, EvaluationCase, EvaluationRequest
from securerag.security import SafetyGuard
from securerag.services import (
    DocumentIngestor,
    EvaluationService,
    ExtractiveAnswerer,
    QueryService,
    TfidfRetriever,
)
from securerag.store import InMemoryChunkStore


def build_services():
    store = InMemoryChunkStore()
    guard = SafetyGuard()
    ingestor = DocumentIngestor(store, guard)
    query = QueryService(TfidfRetriever(store), ExtractiveAnswerer(), guard)
    return ingestor, query


def test_query_returns_relevant_citation() -> None:
    ingestor, query = build_services()
    receipt = ingestor.ingest(
        DocumentCreate(
            title="Annual leave",
            source="employee-handbook",
            text="Employees receive 25 days of annual leave per calendar year.",
        )
    )
    ingestor.ingest(
        DocumentCreate(
            title="Security",
            source="security-policy",
            text="Passwords must contain at least fourteen characters.",
        )
    )

    response = query.query("How many annual leave days do employees receive?")

    assert "25 days" in response.answer
    assert response.citations[0].document_id == receipt.document_id
    assert response.safety_status == "passed"


def test_evaluation_computes_hit_rate_and_mrr() -> None:
    ingestor, query = build_services()
    leave = ingestor.ingest(
        DocumentCreate(title="Leave", source="handbook", text="Annual leave allowance is 25 days.")
    )
    security = ingestor.ingest(
        DocumentCreate(title="Security", source="policy", text="Security training occurs monthly.")
    )
    evaluator = EvaluationService(query)

    result = evaluator.evaluate(
        EvaluationRequest(
            cases=[
                EvaluationCase(
                    question="What is the annual leave allowance?",
                    expected_document_id=leave.document_id,
                ),
                EvaluationCase(
                    question="How often is security training?",
                    expected_document_id=security.document_id,
                ),
            ],
            top_k=1,
        )
    )

    assert result.hit_rate_at_k == 1.0
    assert result.mean_reciprocal_rank == 1.0
