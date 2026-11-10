---
phase_id: "02-unstructured-data-cleaning"
title: "Distributed Unstructured Data (Text / JSONL) Cleaning Engine"
milestone: "Milestone-ETL"
status: "planned"
date: "2026-11-08"
target_data_type: "Unstructured (JSONL / Text / Web Scrapes for LLMs)"
---

# Phase 2: Distributed Unstructured Data (Text / JSONL) Cleaning Engine

## 1. Executive Summary & Goal
Extend DaeMon's distributed preprocessing capabilities to **unstructured text corpora** (JSONL, TXT, raw web-scraped HTML/Markdown) for LLM pre-training and RAG pipeline ingestion.

Training modern LLMs requires clean, high-signal text corpora. Raw web scrapes (e.g. Common Crawl) are filled with boilerplate, cookie banners, navigation links, repetitive character loops, and sensitive credentials. Phase 2 partitions text streams, applies heuristic and regex-based quality filtering on edge nodes, and produces clean token-ready documents.

---

## 2. Technical Architecture & Component Breakdown

### Task 2.1: Document-Aware Unstructured Splitter (`orchestrator/core/text_splitter.py`)
- Slices massive JSONL files by line count, or raw text documents by paragraph/document delimiters (`\n\n\n` or `<|endoftext|>`).
- Ensures individual documents are never split across chunk boundaries.
- Uploads chunked text documents to MinIO under `{job_id}/chunks/chunk_{i}.jsonl`.

### Task 2.2: Worker Unstructured Text Sanitization Strategy (`worker/strategies/text_cleaning.py`)
Worker nodes execute a 6-stage NLP cleaning pipeline:
1. **HTML & Boilerplate Removal:** Strips tags (`<script>`, `<style>`, `<div>`), decoding HTML entities (`&amp;` $\to$ `&`).
2. **Noise & Navigation Filter:** Removes common web noise patterns (e.g., `"Click here to accept cookies"`, `"All rights reserved"`).
3. **Unicode & Mojibake Normalization:** Standardizes UTF-8 encoding (NFC normalization) and strips non-printable ASCII control characters.
4. **Heuristic Quality Filtering:** Drops low-quality documents based on:
   - Minimum word count threshold ($<30$ words).
   - High symbol-to-word ratio (e.g. garbled code or binary dumps).
   - Character repetition loops (e.g., `"aaaaaaaa..."`, `"- - - - -"`).
5. **PII & Credential Scrubbing:** Redacts API keys, JWT bearer tokens, IP addresses, and email addresses.
6. **Token & Compression Telemetry:** Emits metrics on characters cleaned, documents filtered out, and estimated token savings.

### Task 2.3: Orchestrator State Aggregator & Corpus Reassembly (`orchestrator/core/aggregator.py`)
- Concatenates clean JSONL chunks into a unified master training corpus `cleaned_corpus_{job_id}.jsonl`.
- Compiles an unstructured audit summary:
  - `total_documents_ingested`, `documents_retained`, `low_quality_docs_dropped`, `total_characters_removed`, `estimated_token_count`.
- Packages the final clean corpus and audit report into `{job_id}_corpus_deliverable.zip`.

### Task 2.4: Dashboard Preview & Quality Inspection (`dashboard/`)
- Side-by-side "Dirty vs Clean" document preview in the UI inspection tab.
- Distribution charts of document lengths and dropped noise categories.

### Task 2.5: Unstructured Dirty Benchmark Corpus Generator (`generate_dirty_text.py`)
- Generates a sample JSONL corpus containing raw web scrapes, boilerplate noise, invalid encodings, and synthetic PII for testing.

