# DaeMon: Project Roadmap (ROADMAP.md)

> **Document Type:** Multi-Phase Project Roadmap (ROADMAP.md)  
> **Repository:** `Gaurravvvv/Daemon`  
> **Status:** Active Execution (Strategic Pivot: Distributed Data Cleaning Engine)  

---

## Active Milestone: Distributed Dataset Cleaning Engine (Milestone-ETL)

### Phase 1: Distributed Structured Data (CSV) Cleaning Engine (Status: COMPLETED - 100% Verified)
- [x] Task 1.1: Line-preserving streaming CSV partitioning engine (`orchestrator/core/csv_splitter.py`) with header distribution.
- [x] Task 1.2: Worker tabular cleaning strategy (`worker/strategies/csv_cleaning.py`) with deduplication, sentinel null standardization, and regex-based PII masking.
- [x] Task 1.3: Orchestrator State Aggregator & Concatenator (`orchestrator/core/aggregator.py`) to merge clean chunks with cross-chunk deduplication and emit a comprehensive Audit Summary JSON.
- [x] Task 1.4: Next.js Dashboard adaptation (`dashboard/`) with CSV cleaning rule controls and live audit telemetry cards.
- [x] Task 1.5: Benchmark dirty CSV generator script (`generate_dirty_csv.py`) for live demonstrations and testing.
- [x] Task 1.6: Automated end-to-end integration test suite (`tests/test_csv_cleaning_e2e.py`).

### Phase 2: Distributed Unstructured Data (Text / JSONL) Cleaning Engine (Status: PLANNED - Ready for Phase 2)
- [ ] Task 2.1: Document-aware unstructured splitter (`orchestrator/core/text_splitter.py`) for JSONL and raw text corpora.
- [ ] Task 2.2: Worker NLP sanitization strategy (`worker/strategies/text_cleaning.py`) for HTML stripping, boilerplate removal, unicode normalization, and quality filtering.
- [ ] Task 2.3: Orchestrator State Aggregator & Corpus Reassembly for token-ready training datasets.
- [ ] Task 2.4: Dashboard side-by-side "Dirty vs Clean" document preview.
- [ ] Task 2.5: Benchmark dirty text corpus generator (`generate_dirty_text.py`).

---

## Sidelined Foundation Milestones (Preserved)
- **Milestone 1:** Core Infrastructure & Backend Master (COMPLETE)
- **Milestone 2:** Worker Daemon, Docker Sandboxing & GPU Acceleration (COMPLETE)
- **Milestone 3:** Polymorphic Workloads (Image, Matrix, Crypto) (SIDELINED / COMPLETE)
- **Milestone 4:** Output Stitching & Artifact Aggregation (COMPLETE)
- **Milestone 5:** Sub-15s Churn Resilience & Redis TTL Failover (COMPLETE)
