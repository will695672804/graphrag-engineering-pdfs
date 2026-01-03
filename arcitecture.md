# GraphRAG Architecture

## High-Level Flow

PDFs
→ Chunking
→ Entity & Relation Extraction
→ Knowledge Graph
→ Ontology Induction
→ Community Detection
→ Hybrid Retrieval
→ Answer Generation

---

## Offline Components

- Knowledge Graph (NetworkX)
- Type Registry (ontology classes)
- Type Hierarchy (`is_a`)
- Community partitions
- Vector index (FAISS)

---

## Runtime Query Flow

1. Receive question
2. Select retrieval strategy
3. Retrieve candidate facts
4. Enforce community boundaries
5. Assemble evidence
6. Generate answer
7. Compute confidence
8. Log audit trail

---

## Failure Handling

- Insufficient evidence → explicit failure
- Cross-community leakage → veto
- Low confidence → flagged answer

---

## Key Principles

- Deterministic first
- LLMs for completion, not reasoning
- No silent hallucinations
- Explainable decisions
