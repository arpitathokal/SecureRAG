# Interview guide

## Thirty-second explanation

SecureRAG is a document question-answering API designed around two production concerns that basic RAG demos often omit: security and measurable retrieval quality. It redacts PII before indexing, blocks common direct prompt-injection attempts, retrieves traceable chunks, and returns extractive answers with citations. It also exposes an evaluation endpoint for hit rate at k and mean reciprocal rank.

## Design questions to expect

### Why start with TF-IDF instead of embeddings?

It creates a deterministic, free, reproducible baseline. I would compare a semantic or hybrid retriever against this baseline using the same labelled evaluation cases rather than assuming embeddings are automatically better.

### Why use an extractive answerer?

It prevents unsupported claims in the first version and makes failures easy to inspect. A generative Bedrock adapter can be added later, but it should be released only with groundedness tests and strict citation validation.

### How would you make the service production-ready?

I would introduce PostgreSQL/pgvector, asynchronous ingestion, authentication and tenant isolation, rate limits, structured logs, OpenTelemetry traces, encrypted secrets, database migrations, and deployment-specific health checks. I would also add rollback criteria based on retrieval and safety evaluations.

### What is the biggest current limitation?

The safety guard uses high-confidence regular expressions. That is explainable and useful as one layer, but it will miss obfuscated and indirect prompt injection. A production system needs layered detection, document scanning, adversarial tests, strict model instructions, least-privilege tools, and output validation.

### Why dependency injection?

The API depends on service interfaces rather than a cloud provider. This keeps local tests fast and lets storage, retrieval, or answer generation change independently.

## Honest project claims

Safe statements after running the included test suite:

- Built a FastAPI document-retrieval service with citation traceability.
- Implemented explainable PII redaction and direct prompt-injection controls.
- Added deterministic TF-IDF retrieval and extractive answering.
- Implemented retrieval evaluation using hit rate at k and mean reciprocal rank.
- Added automated API, service, and security tests with GitHub Actions.

Do not describe the current version as a deployed AWS system, a semantic vector-search system, or a production compliance solution. Those become valid only after the corresponding roadmap work is completed and verified.

## Five-minute demonstration

1. Open `/docs` and show the health endpoint.
2. Ingest the two sample policies.
3. Ask a factual question and point to the returned source and chunk IDs.
4. Submit a prompt-injection phrase and show the typed blocked response.
5. Ingest a document containing a sample email and show the redaction count.
6. Run a labelled evaluation and explain hit rate and reciprocal rank.
