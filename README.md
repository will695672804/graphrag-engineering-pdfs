# GraphRAG for Large Engineering PDFs

Production-grade **GraphRAG pipeline** for building, improving, evaluating, and documenting knowledge graphs over large engineering and technical PDFs.

This repository implements a **deterministic + LLM-assisted GraphRAG system** with ontology induction, community-aware retrieval, evaluation, and automated documentation generation.

---

## What This Project Does

- Extracts entities and relations from engineering PDFs
- Builds a materialized knowledge graph (NetworkX)
- Learns ontology types and type hierarchies from data
- Detects semantic communities in the graph
- Prevents semantic drift using community-aware retrieval
- Supports hybrid retrieval (Graph + Vector / FAISS)
- Runs targeted LLM improve cycles for factual gaps
- Evaluates multiple RAG strategies
- Generates DOCX and PDF technical documentation automatically

---

## Core Pipeline (Implemented)

1. PDF ingestion and chunking  
2. Entity & relation extraction  
3. Graph construction (`graph.pkl`)  
4. Ontology induction (`type_registry.json`, `type_hierarchy.json`)  
5. Community detection (`communities.json`)  
6. Hybrid retrieval (Graph + FAISS)  
7. Improve cycle (LLM-assisted, checkpointed)  
8. Strategy evaluation  
9. Automated documentation generation  

---

## Key Artifacts

| Artifact | Description |
|--------|-------------|
| `index/graph.pkl` | Materialized knowledge graph |
| `index/type_registry.json` | Learned ontology classes |
| `index/type_hierarchy.json` | Inferred type hierarchy |
| `index/communities.json` | Graph communities |
| `index/faiss.index` | Vector index |
| `index/strategy_comparison.json` | Strategy evaluation |
| `index/missed_knowledge.json` | Improve-cycle gaps |
| `documentation/GraphRAG_Documentation.docx` | Auto-generated doc |
| `documentation/GraphRAG_Documentation.pdf` | PDF (LibreOffice) |

---

## Documentation

Technical documentation is generated automatically using:

```bash
python scripts/generate_documentation.py
```

Outputs:
- DOCX (always)
- PDF (via LibreOffice headless)

---

## Design Philosophy

- Deterministic structure before LLMs
- LLMs used only for factual completion
- Community boundaries prevent semantic drift
- Explainability and reproducibility over recall

---

## Status

- Core GraphRAG engine: ✅ COMPLETE
- Ontology & communities: ✅ COMPLETE
- Evaluation & documentation: ✅ COMPLETE
- Operationalization: 🚧 IN PROGRESS
