---
phase_id: "01-structured-data-cleaning"
title: "Distributed Structured Data (CSV) Cleaning Engine"
milestone: "Milestone-ETL"
status: "planned"
date: "2026-11-08"
target_data_type: "Structured (CSV / Tabular)"
---

# Phase 1: Distributed Structured Data (CSV) Cleaning Engine

## 1. Executive Summary & Goal
Transform the DaeMon compute grid into an elastic, volunteer-powered **Distributed Data Cleaning Engine** for large-scale structured tabular datasets (CSV). 

A single laptop running Pandas on a 5 GB - 20 GB dirty CSV easily runs out of memory (OOM) or takes hours to clean. DaeMon partitions the monolithic CSV into line-aligned chunks, pushes micro-task manifests across volunteer nodes, applies an intensive multi-stage cleaning pipeline on edge nodes, and atomically aggregates cleaned slices into a unified master deliverable with an automated **Cleaning Audit Report**.

```
[Raw Dirty CSV] 
       │
       ▼ (Orchestrator Line-Aligned Chunking + MinIO Staging)
┌────────────────────────────────────────────────────────┐
│ Chunk 0 (Rows 1-50k)   Chunk 1 (Rows 50k-100k)  ...    │
└──────────────┬─────────────────────────┬───────────────┘
               │                         │
               ▼                         ▼
        [Worker Node 1]           [Worker Node 2]
     (Deduplicate, Clean,      (Deduplicate, Clean,
      Impute, Redact PII)       Impute, Redact PII)
               │                         │
               └────────────┬────────────┘
                            │ (Clean Slices + Audit JSONs)
                            ▼
              [State Aggregator & Concatenator]
                            │
                            ▼
  [Clean Master CSV] + [Cleaning Audit Report JSON]
```

---

## 2. Technical Architecture & Component Breakdown

### Task 1.1: Line-Preserving CSV Partitioning Engine (`orchestrator/core/csv_splitter.py`)
- **Challenge:** Naive byte-splitting cuts across CSV rows, corrupting mid-line quotes and fields.
- **Solution:** A streaming, line-aware partitioner that:
  1. Reads and buffers the CSV header line.
  2. Splits the remaining rows into $N$ roughly equal row-count chunks without loading the entire multi-GB file into RAM.
  3. Prepends the identical header row to every chunk file (`chunk_{i}.csv`).
  4. Streams each chunk directly to MinIO at `{job_id}/chunks/chunk_{i}.csv`.
  5. Publishes micro-task manifests to RabbitMQ with explicit chunk URLs (eliminating the monolithic download bottleneck).

### Task 1.2: High-Throughput Worker Cleaning Strategy (`worker/strategies/csv_cleaning.py`)
Worker nodes execute a 6-stage vectorized tabular cleaning pipeline:
1. **Header Normalization:** Strips leading/trailing whitespace, converts column names to snake_case, removes non-alphanumeric special characters.
2. **Missing & Sentinel Value Sanitization:** Detects empty cells and standard sentinel null strings (`"NA"`, `"N/A"`, `"null"`, `"None"`, `"?"`, `"-"`, `"\x00"`). Imputes default values or drops rows exceeding configurable null thresholds.
3. **Exact & Near-Duplicate Row Deduplication:** Fast hash-based row deduplication.
4. **Data Type Coercion & Whitespace Trimming:** Trims cell whitespaces, normalizes numeric columns, formats timestamps into standard ISO-8601 (`YYYY-MM-DD HH:MM:SS`).
5. **PII Masking & Privacy Scrubbing (Regex):** Redacts email addresses (`[REDACTED_EMAIL]`), phone numbers (`[REDACTED_PHONE]`), and sensitive identifier sequences.
6. **Telemetry & Audit Generation:** Generates a granular audit payload for the slice:
   - `input_rows`, `retained_rows`, `duplicates_dropped`, `null_cells_repaired`, `pii_redacted`, `duration_seconds`, `throughput_rows_per_sec`.
   - Writes `cleaned_chunk_{i}.csv` and `audit_{i}.json` and uploads both to MinIO.
   - Cleans temporary worker directories in a `finally:` block.

### Task 1.3: Orchestrator State Aggregator & Deliverable Concatenator (`orchestrator/core/aggregator.py`)
- Listens for 100% completion of all CSV chunks.
- Downloads `cleaned_chunk_{i}.csv` files in strict chronological chunk sequence.
- Streams clean rows into `cleaned_master_{job_id}.csv` (omitting duplicate headers from subsequent chunks).
- Performs a secondary global deduplication pass across boundary slices.
- Aggregates all worker audit JSONs into a consolidated **Master Data Audit Report**:
  - `total_input_rows`, `total_clean_rows`, `retention_rate_pct`, `total_duplicates_removed`, `total_nulls_imputed`, `total_pii_masked`, `total_cleaning_time_seconds`, `effective_cluster_throughput_rows_per_sec`.
- Packages the master CSV + audit report into a downloadable ZIP in MinIO and marks `status="completed"`.

### Task 1.4: Next.js Dashboard Adaptation (`dashboard/`)
- **Submit Modal:**
  - Dedicated "Structured CSV Cleaning" pipeline option.
  - Configurable cleaning toggles: `Deduplicate Rows`, `Drop / Impute Nulls`, `Redact Sensitive PII`, `Normalize Timestamps`.
- **Live Terminal & Telemetry:**
  - Real-time worker event feed: e.g. `[NODE-B4] Cleaned chunk 3/10 (50,000 rows in 1.1s: 1,240 duplicates dropped, 310 PII masked)`.
  - Master Audit Summary Card upon completion with one-click "Download Cleaned CSV Dataset".

### Task 1.5: Dirty CSV Benchmark Dataset Generator (`generate_dirty_csv.py`)
- Creates a realistic, messy test dataset (e.g. 100,000 to 500,000 rows of user/transaction records) containing:
  - 10% duplicate rows.
  - 15% null and missing values in various formats (`"N/A"`, `""`, `"null"`).
  - Unformatted phone numbers and personal emails.
  - Inconsistent date formats (`"01/12/2024"`, `"2024-12-01"`).
  - Dirty trailing whitespace and broken encoding characters.

---

## 3. Verification & Acceptance Criteria
- [ ] Uploading a 200,000-row dirty CSV splits cleanly into $N$ valid CSV chunks with identical headers.
- [ ] Worker processes chunks without memory leaks or uncleaned temp files.
- [ ] Duplicate rows are removed; PII emails and phone numbers are redacted.
- [ ] Output `cleaned_master.csv` has valid syntax, correct row counts, and no duplicate headers.
- [ ] `cleaning_audit_summary.json` accurately tallies all dropped nulls, duplicates, and cluster throughput.
- [ ] Download button delivers the pristine master CSV and audit report.

