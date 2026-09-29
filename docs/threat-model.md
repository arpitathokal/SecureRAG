# Threat model

## Assets

- indexed document contents;
- user questions and retrieved evidence;
- model and database credentials in future provider adapters;
- citation integrity and evaluation results.

## Trust boundaries

User questions and uploaded documents are untrusted. Retrieved document text is evidence, never an instruction. A future hosted model and vector database form separate external trust boundaries.

## Priority threats and controls

| Threat | Current control | Residual risk / next control |
|---|---|---|
| Direct prompt injection | High-confidence pattern blocking | Add classifier and adversarial evaluation |
| Indirect injection in documents | Extractive answerer does not execute instructions | Add document-injection scanner before generative model integration |
| PII persistence | Redaction before indexing | Add named-entity model and regional detectors |
| Hallucinated claims | Extractive answers and citations | Add groundedness evaluation for generative answers |
| Cross-tenant data exposure | Single local index only | Tenant-scoped storage, authorisation, and row-level policies |
| Denial of service | Input-length limits | Rate limits, quotas, request timeouts, and queueing |
| Sensitive data in logs | Raw content is not logged | Structured logging with explicit allow-list |

## Security assumptions

This version is a local portfolio demonstration. It has no authentication or tenant isolation and must not be exposed directly to the public internet. Regex PII detection is illustrative rather than a compliance guarantee.

## Abuse cases to test next

1. Obfuscated prompt injection using Unicode or encoded text.
2. Malicious instructions embedded inside a retrieved document.
3. Questions designed to reconstruct redacted values.
4. Very large documents intended to exhaust memory.
5. Citation spoofing inside source text.
