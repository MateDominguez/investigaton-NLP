# Optimización de Memoria para LLMs Pequeños Product Requirements Document (PRD)

## Goals and Background Context

### Goals
*   **Maximize LongMemEval Score:** Achieve state-of-the-art performance for <4B parameter models on the LongMemEval benchmark (held-out set).
*   **Enable Edge Memory:** Implement a memory solution viable for edge devices (low resource consumption, <4B models).
*   **Agentic Self-Correction:** Demonstrate that an internal "critic" loop can fix memory retrieval errors without needing a larger model.
*   **Benchmark Compliance:** Satisfy all Investighaton rules (only valid models, correct data splitting).

### Background Context
Small Language Models (SLMs) struggle with long-context reasoning (~115k tokens) due to limited attention windows and "lost-in-the-middle" phenomena. Specific to the Investighaton, we need a solution that competes with larger models using only efficient, local resources.
Existing "trivial RAG" solutions fail to capture complex relationships (Temporal Reasoning, Multi-session logic). By implementing a **GraphRAG** approach combined with an **Agentic Loop** (using Phi 3.5 Mini as an internal critic), we aim to bridge this gap. The system must operate strictly within the <4B parameter constraint for generation, using ChatGPT 5 Mini only as a final, external judge for scoring.

### Change Log
| Date       | Version | Description                   | Author |
|------------|---------|-------------------------------|--------|
| 2025-12-06 | 1.0     | Initial Draft based on Brief  | John   |

## Requirements

### Functional Requirements
*   **FR1: Data Ingestion Pipeline**
    *   The system loads the `data/longmemeval` dataset into memory (assuming ~120MB total size) for faster processing.
    *   (Optional) Includes a fallback to batch processing only if memory limit is exceeded.
*   **FR2: Graph Construction**
    *   The system extracts Entities using Phi 3.5 Mini.
    *   **Configurable Schema:** The system supports `Schema Free` and `Hard Schema` modes.
    *   **Community Detection:** The system processes the graph to identify communities (clusters of tightly connected nodes) using algorithms like Louvain or Leiden.
    *   The system stores the graph using `NetworkX` (serialized to disk when not in use).
*   **FR3: Hybrid Retrieval**
    *   The system performs Vector Search (FAISS) for semantic similarity.
    *   **Search Strategies:** The system supports:
        1.  `Local Search`: Traverses neighbors of specific entities found in the query (high precision).
        2.  `Global Search`: Utilizes detected communities to answer broad/thematic questions (high recall/summary).
    *   The system combines results from both sources for the final context window.
*   **FR4: Internal Evaluator Loop**
    *   The system "Self-Reflects" on the answer quality.
    *   **Configurable Retries:** The maximum number of re-retrieval attempts (`max_retries`) is configurable (Default: 1).
    *   If "Unsatisfactory" and `retries < max_retries`, triggers re-retrieval.
*   **FR5: Evaluation Interface**
    *   The system implements a wrapper compliant with `main.py` to allow easy benchmarking.
    *   The system outputs results in JSON format matching `data/investigathon/Investigathon_LLMTrack_HeldOut_s_cleaned.json`.
*   **FR6: External Judging**
    *   The system integrates `JudgeAgent.py` (ChatGPT 5 Mini) solely for final scoring of the generated answers against `Investighaton_LLMTranck_Evaluation_s_cleaned.json`.

### Non-Functional Requirements
*   **NFR1: Model Constraints:** All generation and internal evaluation MUST use models <4B parameters (e.g., Phi 3.5 Mini).
*   **NFR2: Memory Efficiency:** The ingestion process must not exceed the available system RAM (batch processing required).
*   **NFR3: Latency:** The Agentic Loop must have a hard limit (e.g., `max_retries=1`) to prevent infinite execution time.
*   **NFR4: Dependability:** The solution must be reproducible and runnable in a standard Linux environment with Python.

## Technical Assumptions
*   **Repository Structure:** Monorepo (Single project folder).
*   **Service Architecture:** Monolith (Scripts directly importing modules, no microservices/APIs).
*   **Testing:** System Integration Testing (Run `main.py` against valid dataset).
*   **Language:** Python 3.10+.
*   **Frameworks:** LlamaIndex (RAG/Graph), NetworkX (Graph DB), FAISS (Vector DB).

## Epic List
*   **Epic 1: Core Infrastructure:** Setup LlamaIndex, NetworkX, and batch ingestion pipeline for `data`.
*   **Epic 2: GraphRAG Baseline:** Implement Entity Extraction, Graph Construction, and Hybrid Search.
*   **Epic 3: Agentic Loop:** Implement the "Internal Evaluator" and re-retrieval logic.
*   **Epic 4: Integration & Benchmark:** Wrap everything into `main.py`, run full evaluation, and generate final JSON.

## User Interface Design Goals
*   **Target Device and Platforms:** CLI / Script Only (Linux Terminal).
*   **Interaction Paradigms:** Non-interactive execution (Batch Mode). The user runs a command and waits for the progress bar/final JSON.
*   **Core Views:** Console Output (Progress Bar, Current Question processing status, Error Logs).

## Epic Details

### Epic 1: Core Infrastructure
**Goal:** Establish the foundational Python environment and efficient data ingestion pipeline to handle the large dataset without crashing memory.

*   **Story 1.1: Setup Project Environment**
    *   **As a** Developer, **I want** a `requirements.txt` with LlamaIndex, NetworkX, and FAISS, **so that** I have all necessary libraries installed in the container.
    *   **Acceptance Criteria:**
        1.  `pip install -r requirements.txt` runs without conflict.
        2.  A simple "Hello World" script imports `llama_index` and `networkx` successfully.

*   **Story 1.2: In-Memory Data Loading**
    *   **As a** Developer, **I want** to load the dataset (~120MB) into a pandas DataFrame/List, **so that** access is instant during graph construction.
    *   **Acceptance Criteria:**
        1.  `load_data()` returns the full dataset object.
        2.  System RAM usage monitoring confirms it fits comfortably (<1GB overhead).

### Epic 2: GraphRAG Baseline
**Goal:** Implement the "Baseline" system that constructs a knowledge graph and performs hybrid retrieval to answer questions.

*   **Story 2.1: Entity Extraction (Schema Modes)**
    *   **As a** Developer, **I want** to choose between "Hard Schema" (fixed types) and "Schema Free", **so that** I can experiment with graph quality.
    *   **Acceptance Criteria:**
        1.  Config `graph_schema_mode` accepts "fixed" or "dynamic".
        2.  "Fixed": Prompt restricts output to [Person, Event, Date, etc.].
        3.  "Dynamic": Prompt allows model to define new types.

*   **Story 2.2: Graph Builder & Storage**
    *   **As a** System, **I want** to insert extracted triplets into a NetworkX graph, **so that** I can persist the structural knowledge.
    *   **Acceptance Criteria:**
        1.  Graph nodes represent Entities (Person, Event, etc.).
        2.  Edges represent relationships with timestamps (if available).
        3.  Graph can be serialized to `.gexf` or `.pickle`.

*   **Story 2.3: Configurable Search Strategies (Local/Global)**
    *   **As a** User, **I want** to switch between Local and Global search, **so that** I can answer specific facts ("When did X happen?") vs broad themes ("How did X change over time?").
    *   **Acceptance Criteria:**
        1.  Config `graph_search_mode` accepts "local" or "global".
        2.  "Local": Standard k-hop neighbor retrieval.
        3.  "Global": Selects top nodes from relevant communities based on query vector overlap.

*   **Story 2.4: Community Detection**
    *   **As a** System, **I want** to assign a community ID to every node, **so that** efficient Global Search is possible.
    *   **Acceptance Criteria:**
        1.  Runs community detection (e.g., Louvain) after graph build.
        2.  Each node in NetworkX has a `community` attribute.
        3.  Fast execution (<1min for full graph).

### Epic 3: Agentic Loop (Internal Evaluator)
**Goal:** Implement the "Internal Critic" that improves answer quality before final output.

*   **Story 3.1: Internal Evaluator Agent**
    *   **As a** System, **I want** an agent (Phi 3.5) that compares a Question vs Generated Answer, **so that** it can flag "Missing Info" or "Unclear".
    *   **Acceptance Criteria:**
        1.  Prompt returns strictly "SATISFIED" or "UNSATISFIED".
        2.  Does NOT require Ground Truth to function (Reference-free evaluation).

*   **Story 3.2: Configurable Retry Logic**
    *   **As a** Researcher, **I want** to set `max_retries` in the config, **so that** I can balance latency vs accuracy.
    *   **Acceptance Criteria:**
        1.  Loop stops if `current_try > max_retries`.
        2.  Default `max_retries=1`.
        3.  Logs warning if max retries reached without satisfaction.

### Epic 4: Integration & Benchmark
**Goal:** Connect the new system to the existing `main.py` harness and generate the submission file.

*   **Story 4.1: Main Integration Wrapper**
    *   **As a** User, **I want** to run `python main.py --mode=graph_agent`, **so that** it uses my new class instead of the default RAG.
    *   **Acceptance Criteria:**
        1.  New class adheres to the interface expected by `main.py` (method signatures).
        2.  Config flag allows switching betwen "Baseline" (Epic 2) and "Full Agent" (Epic 3).

*   **Story 4.2: Final Output Generation**
    *   **As a** User, **I want** the system to produce `Investigathon_LLMTrack_HeldOut_s_cleaned.json` with my answers, **so that** I can submit it to the jury.
    *   **Acceptance Criteria:**
        1.  Output JSON matches the exact schema of the provided example.
        2.  File contains answers for all 250 held-out questions.

## Checklist Results
(To be completed after User Approval)

## Next Steps
### UX Expert Prompt
N/A - Project is CLI based.

### Architect Prompt
You are the **Lead Architect**. Input: `docs/prd.md`.
Goal: Design the Python module structure to implement GraphRAG with LlamaIndex and NetworkX.
Key Constraints:
1.  **Memory:** Use generators for data loading.
2.  **Models:** ONLY Phi 3.5 Mini for generation/internal eval.
3.  **Graph:** NetworkX serialized to disk.
Output: Create `docs/architecture.md` defining the class hierarchy (`GraphRAGManager`, `IngestionPipeline`, `AgentLoop`) and data flow.

