# Work Items & Roadmap

This document lists remaining work required to move the system from a
research-grade GraphRAG engine to a production-ready platform.

---

## 1. Batch Ingestion & Corpus Lifecycle (HIGH PRIORITY)

### What is missing
Ingestion is currently manual and one-off.

### Work Items
- Folder-based batch PDF ingestion
- Content hashing to detect changes
- Skip unchanged documents
- Incremental graph updates
- Corpus versioning
- Selective improve-cycle reruns

---

## 2. Query API Layer (FOUNDATIONAL)

### What is missing
There is no stable query contract.

### Work Items
- Single `answer(question, strategy)` entry point
- Strategy-selectable execution
- Structured JSON response
- Debug / trace mode

---

## 3. Community-Aware Retrieval Enforcement (CRITICAL)

### What is missing
Communities are computed but not enforced at query time.

### Work Items
- Enforce community boundaries
- Block cross-community traversal
- Minimum graph-support threshold
- Explicit “insufficient evidence” fallback

---

## 4. Continuous Improve Loop (OPERATIONALIZE)

### What is missing
Improve cycle is not scheduled or regression-checked.

### Work Items
- Scheduled improve runs
- Priority scoring for gaps
- Automatic re-evaluation
- Regression detection
- Rollback on degradation

---

## 5. Governance & Trust Controls

### What is missing
No confidence or answer veto.

### Work Items
- Confidence calibration
- Evidence sufficiency checks
- Answer veto
- Full audit trail

---

## 6. Frontend (OPTIONAL)

### Guidance
Frontend should be thin and contain no business logic.

### Work Items
- Streamlit or Gradio UI
- Question input
- Answer + evidence display
- Graph/community trace view

---

## Execution Order

1. Batch ingestion
2. Query API
3. Community enforcement
4. Improve loop automation
5. Governance controls
6. Frontend (optional)

