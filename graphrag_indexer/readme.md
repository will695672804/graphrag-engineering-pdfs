# GraphRAG Engineering Pipeline — Build, Improve, Evaluate

This repository implements a **production-grade GraphRAG pipeline** for large engineering PDFs.  
The system incrementally builds, structures, improves, and evaluates a knowledge graph to support
high-precision retrieval and reasoning.

This document explains **what to run, in what order, and why**.

---

## 🧠 High-Level Architecture

The pipeline is deliberately split into **three distinct phases**:

1. **Graph Construction** – extract factual knowledge
2. **Graph Structuring & Improvement** – add semantic structure and fill gaps
3. **Evaluation** – measure retrieval and reasoning quality

> **Key principle**  
> - Structure is inferred *deterministically* (no LLMs)  
> - Content gaps are filled *selectively* using LLMs  
> - Evaluation is done only after convergence

---

## 📁 Key Artifacts

| Artifact | Description |
|-------|------------|
| `index/graph.pkl` | Materialized NetworkX knowledge graph |
| `index/type_registry.json` | Learned ontology classes |
| `index/type_hierarchy.json` | Inferred `is_a` relationships |
| `index/faiss.index` | Vector index for hybrid retrieval |
| `index/communities.json` | Graph communities |
| `index/strategy_comparison.json` | Evaluation results |

---

## 🚀 Execution Pipeline (Correct Order)

### 🔹 Phase 0 — Initial Graph Build (Extraction)

Build the **raw knowledge graph** from documents.

```bash
python index_documents.py
python extractor.py
python graph_store.py
```

**Output**
```
index/graph.pkl
```

At this stage:
- Entities and relations exist
- Graph is **flat**
- Schema is implicit
- Many gaps still exist

---

### 🔹 Phase 1 — Structural Enrichment (NO LLMs)

This phase improves **graph structure**, not content.

#### 1. Build Type Registry

Learns what *kinds of things* exist in the graph.

```bash
python build_type_registry.py
```

Produces:
```
index/type_registry.json
```

---

#### 2. Infer Type Hierarchy

Infers subclass (`is_a`) relationships between types.

```bash
python infer_type_hierarchy.py
```

Produces:
```
index/type_hierarchy.json
```

---

#### 3. Repair & Enrich Graph Structure

Injects inferred structure back into the graph.

```bash
python repair_graph_pickle.py
```

This step may:
- Add `is_a` edges (marked as inferred)
- Normalize relations
- Reduce fragmentation

**Output**
```
index/graph.pkl   (structurally improved)
```

> ⚠️ Important  
> This phase is **deterministic**.  
> No LLM calls should occur here.

---

### 🔹 Phase 2 — Content Improvement Cycle (LLM-Driven)

This is where **`run_improve_cycle.py` fits**.

```bash
python run_improve_cycle.py
```

#### What this step does
- Detects missing or weak knowledge
- Re-extracts *only* necessary chunks
- Adds **new facts**, not new schema
- Uses checkpoints to resume safely

#### What it consumes
- `graph.pkl`
- Canonical entity & relation dictionaries
- Optional: type registry / hierarchy

#### What it produces
- Updated `graph.pkl`
- `missed_knowledge.json`
- `checkpoint.json`

> **Design rule**  
> `run_improve_cycle.py` improves **completeness**,  
> not **structure**.

---

### 🔁 Optional: Re-structure After Improve

If new entity types appear:

```bash
python build_type_registry.py
python infer_type_hierarchy.py
python repair_graph_pickle.py
```

This stabilizes the ontology before evaluation.

---

### 🔹 Phase 3 — Evaluation

Only run evaluation **after structure and improve cycles converge**.

```bash
python evaluate_queries.py
python evaluate_strategies.py
```

Produces:
```
index/strategy_comparison.json
index/evaluation.json
```

---

## 🧭 Mental Model (Keep This in Mind)

| Phase | Question Answered |
|----|-------------------|
| Phase 0 | *What does the document say?* |
| Phase 1 | *What kinds of things exist?* |
| Phase 2 | *What facts are missing?* |
| Phase 3 | *How good are the answers?* |

---

## ❌ Common Mistakes to Avoid

- Running `run_improve_cycle.py` before structural repair
- Inferring ontology using LLMs
- Modifying `graph.pkl` during extraction
- Evaluating before convergence

---

## ✅ Summary

- **Structure first**
- **LLMs only for gap filling**
- **Evaluation last**
- **Repeatable, deterministic pipeline**

This ordering ensures:
- Stable schema
- Faster convergence
- Lower hallucination rate
- Meaningful strategy comparison

---

## 📌 Next Extensions (Optional)

- Ontology-aware query expansion
- Class-level graph visualizations
- Ontology coverage metrics
- Automatic improve-cycle stopping criteria

---

**Authoring intent:**  
This pipeline is designed for **production GraphRAG systems**, not demos.

