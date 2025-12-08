# Project Name: Investigathon NLP - MiniRAG Integration
# Product Requirements Document (PRD)

## Goals and Background Context

### Goals
- **Integrate MiniRAG**: Successfully integrate the MiniRAG framework as a memory module.
- **Beat the Baseline**: Improve upon the "Simple RAG" baseline performance on the LongMemEval benchmark.
- **Optimize for <4B Parameters**: Ensure the solution is efficient and effective using only small language models (specifically **Phi-3.5-mini-instruct**).
- **Submission Readiness**: Generate valid predictions for the Held-Out set by the deadline.

### Background Context
This project is part of the YHat Investigathon NLP track. The challenge is to build a memory system for conversational agents running on small devices (using models <4B parameters). The current codebase provides a baseline RAG implementation (`RAGAgent.py`) and an evaluation pipeline (`main.py`). We aim to replace/enhance this with MiniRAG (HKUDS/MiniRAG).
**Critical Constraint:** The Judge Agent (evaluator) uses **GPT-5-mini** (allowed >4B params), but the Memory Agent (answering system) MUST use **Phi-3.5-mini-instruct** (<4B params).
**Data Usage:** `data/longmemeval` is for optimization/training. `data/investigathon` is STRICTLY for evaluation and submission.

### Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-12-07 | 1.0 | Initial Draft | Antigravity (PM Agent) |

## Requirements

### Functional Requirements
- **FR1**: The system must include a `MiniRAGAgent` class that implements the `answer(instance)` method compatible with `main.py`.
- **FR2**: The agent must be able to index the session history of a `LongMemEvalInstance` using MiniRAG's indexing mechanism.
- **FR3**: The agent must retrieve relevant context for a given question using MiniRAG's retrieval mechanism.
- **FR4**: The system must strictly use the configured memory model (**Phi-3.5-mini-instruct**) for generation, adhering to the <4B parameter constraint.
- **FR5**: The integration must support switching between the baseline `RAGAgent` and `MiniRAGAgent` via configuration or CLI arguments.
- **FR6**: The system must use **GPT-5-mini** as the Judge Agent for evaluation.

### Non-Functional Requirements
- **NFR1**: **Latency**: Retrieval and generation time must be tracked and kept within reasonable limits for "on-device" simulation.
- **NFR2**: **Context Window**: The prompts sent to the LLM must fit within the model's context window (MiniRAG should help condense/select info).
- **NFR3**: **Reliability**: The system must robustly handle empty retrievals or API failures (e.g., from Ollama).
- **NFR4**: **Reproducibility**: Results must be deterministic where possible or variance must be reported.

## Technical Assumptions
- **Repository**: Single Monorepo (`investigaton-NLP`).
- **Architecture**:
  - **Wrapper**: `MiniRAGAgent` wraps the external `MiniRAG` library.
  - **Dependency**: `MiniRAG` will be cloned/submoduled into `src/MiniRAG`.
  - **Model Server**: Ollama is used for LLM inference (**Phi-3.5-mini-instruct**) and Embeddings (nomic-embed-text).
- **Testing**:
  - Validation via `main.py` (Short track).
  - Comparison against Baseline RAG results.

## Epic List
- **Epic 1: Integration & Baseline**: Get MiniRAG running within the `main.py` pipeline and establish a performance baseline.
- **Epic 2: Optimization & Tuning**: Analyze failures and tune MiniRAG parameters using `data/longmemeval` dataset.
- **Epic 3: Final Eval**: Run full evaluation on Investigathon Evaluation set and generate Held-Out submission.

## Epic Details

### Epic 1: Integration & Baseline
**Goal**: Integrate the MiniRAG library and confirm it can answer questions end-to-end using Phi-3.5-mini-instruct.
**Stories**:
- **Story 1.1**: Clone and setup MiniRAG in `src/MiniRAG`.
- **Story 1.2**: Create `MiniRAGAgent.py` wrapper class.
- **Story 1.3**: Update `main.py` default models to `Phi-3.5-mini-instruct` (memory) and `GPT-5-mini` (judge).
- **Story 1.4**: Run a smoke test (2 samples) on `data/longmemeval` to verify end-to-end flow.

### Epic 2: Optimization & Tuning
**Goal**: Iterate on the configuration to maximize the accuracy score using `data/longmemeval` for tuning.
**Stories**:
- **Story 2.1**: Measure baseline performance on `data/longmemeval`.
- **Story 2.2**: Analyze errors using the Judge (`GPT-5-mini`).
- **Story 2.3**: Tune MiniRAG retrieval parameters (top-k, expansion depth).
- **Story 2.4**: Validate improvements on `data/longmemeval` (held-out subset if applicable).

### Epic 3: Final Eval
**Goal**: Produce the final artifacts for submission.
**Stories**:
- **Story 3.1**: Run full `investigathon_evaluation` Set.
- **Story 3.2**: Run full `investigathon_held_out` Set.
- **Story 3.3**: Generate Submission JSON.
- **Story 3.4**: Compile metrics (Latency, Context Len, Score) for the report.

## Next Steps
### Architect Prompt
Proceed to **Epic 1**.
Start by cloning the MiniRAG repository and creating the `MiniRAGAgent` class.
Ensure `main.py` is updated to switch between agents.
