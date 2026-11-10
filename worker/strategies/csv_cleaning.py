import os
import csv
import re
import time
import json
import shutil
import tempfile
import hashlib
import logging
from typing import Dict, Any, List, Set, Tuple
from storage import storage

logger = logging.getLogger(__name__)

# Common sentinel null representations in real-world messy data
SENTINEL_NULLS = {
    "na", "n/a", "null", "none", "?", "-", "--", "nil", "nan", 
    "\\n", "\\x00", "undefined", "#n/a", "unknown", "n.a."
}

# Compiled regex patterns for PII detection
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
SSN_CC_REGEX = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{3}-\d{2}-\d{4}\b')

# Date formats matching
DATE_REGEX_1 = re.compile(r'^\s*(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\s*$')
DATE_REGEX_2 = re.compile(r'^\s*(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})\s*$')

def _normalize_header_name(header: str, idx: int) -> str:
    """Convert arbitrary header name to clean snake_case."""
    cleaned = header.strip().lower()
    cleaned = re.sub(r'[^\w\s]', '_', cleaned)
    cleaned = re.sub(r'\s+', '_', cleaned)
    cleaned = re.sub(r'_+', '_', cleaned).strip('_')
    return cleaned if cleaned else f"column_{idx}"


class CSVCleaningStrategy:
    """
    High-Performance, Schema-Agnostic Tabular Cleaning Engine.
    Executes universal header normalization, sentinel null replacement,
    row deduplication, PII masking, and data normalization across arbitrary CSV datasets.
    """

    @staticmethod
    def execute(task_payload: dict) -> dict:
        task_id = task_payload.get("task_id", "unknown")
        job_id = task_payload.get("job_id", "unknown")
        chunk_index = task_payload.get("chunk_index", 0)
        raw_data_url = task_payload.get("raw_data_url", "")
        rules = task_payload.get("rules", {})

        do_dedup = rules.get("deduplicate", True)
        do_clean_headers = rules.get("clean_headers", True)
        do_nulls = rules.get("standardize_nulls", True)
        do_pii = rules.get("redact_pii", True)
        do_dates = rules.get("standardize_dates", True)
        null_thresh_pct = rules.get("null_threshold_pct", 80)

        logger.info(f"[CSVCleaningStrategy] Starting task {task_id} for job {job_id} (chunk {chunk_index})")

        if not raw_data_url.startswith("minio://"):
            raise ValueError(f"Invalid raw_data_url format: {raw_data_url}")

        parts = raw_data_url.replace("minio://", "").split("/", 1)
        bucket = parts[0]
        object_name = parts[1]

        temp_dir = os.path.join(tempfile.gettempdir(), "daemon_worker")
        os.makedirs(temp_dir, exist_ok=True)
        local_chunk_path = os.path.join(temp_dir, f"{task_id}_in.csv")
        local_clean_path = os.path.join(temp_dir, f"{task_id}_clean.csv")
        local_audit_path = os.path.join(temp_dir, f"{task_id}_audit.json")

        try:
            downloaded = storage.download_data(bucket, object_name, local_chunk_path)
            if not downloaded:
                raise Exception("Failed to download CSV chunk from MinIO")

            start_time = time.time()
            input_row_count = 0
            retained_row_count = 0
            duplicates_removed = 0
            null_cells_cleaned = 0
            pii_masked = 0
            corrupt_rows_dropped = 0
            normalized_columns = []

            seen_row_hashes: Set[str] = set()

            with open(local_chunk_path, "r", encoding="utf-8", errors="replace") as in_f, \
                 open(local_clean_path, "w", encoding="utf-8", newline="") as out_f:

                reader = csv.reader(in_f)
                writer = csv.writer(out_f)

                # 1. Process Header Row
                try:
                    raw_header = next(reader)
                except StopIteration:
                    raw_header = []

                if do_clean_headers:
                    normalized_columns = [_normalize_header_name(h, idx) for idx, h in enumerate(raw_header)]
                else:
                    normalized_columns = [h.strip() for h in raw_header]

                writer.writerow(normalized_columns)
                num_columns = len(normalized_columns)

                # 2. Row-by-Row Stream Cleaning Pipeline
                for row in reader:
                    input_row_count += 1
                    if not row or all(cell.strip() == "" for cell in row):
                        corrupt_rows_dropped += 1
                        continue

                    # Ensure row length matches header
                    if len(row) < num_columns:
                        row.extend([""] * (num_columns - len(row)))
                    elif len(row) > num_columns:
                        row = row[:num_columns]

                    # Stage A: Check Row Deduplication
                    if do_dedup:
                        row_hash = hashlib.md5("||".join(c.strip() for c in row).encode("utf-8")).hexdigest()
                        if row_hash in seen_row_hashes:
                            duplicates_removed += 1
                            continue
                        seen_row_hashes.add(row_hash)

                    cleaned_row = []
                    empty_cells_count = 0

                    for cell in row:
                        cell_val = cell.strip()

                        # Stage B: Sentinel Null Standardization
                        if do_nulls and cell_val.lower() in SENTINEL_NULLS:
                            cell_val = ""
                            null_cells_cleaned += 1

                        if not cell_val:
                            empty_cells_count += 1
                            cleaned_row.append("")
                            continue

                        # Stage C: PII Scrubbing
                        if do_pii:
                            if EMAIL_REGEX.search(cell_val):
                                cell_val = EMAIL_REGEX.sub("[REDACTED_EMAIL]", cell_val)
                                pii_masked += 1
                            if PHONE_REGEX.search(cell_val):
                                cell_val = PHONE_REGEX.sub("[REDACTED_PHONE]", cell_val)
                                pii_masked += 1
                            if SSN_CC_REGEX.search(cell_val):
                                cell_val = SSN_CC_REGEX.sub("[REDACTED_ID]", cell_val)
                                pii_masked += 1

                        # Stage D: Date Standardization
                        if do_dates and len(cell_val) <= 25:
                            m1 = DATE_REGEX_1.match(cell_val)
                            if m1:
                                d, m, y = m1.groups()
                                cell_val = f"{y.zfill(4)}-{m.zfill(2)}-{d.zfill(2)}"
                            else:
                                m2 = DATE_REGEX_2.match(cell_val)
                                if m2:
                                    y, m, d = m2.groups()
                                    cell_val = f"{y.zfill(4)}-{m.zfill(2)}-{d.zfill(2)}"

                        cleaned_row.append(cell_val)

                    # Stage E: Null Threshold Filter
                    if num_columns > 0:
                        empty_pct = (empty_cells_count / num_columns) * 100.0
                        if empty_pct >= null_thresh_pct:
                            corrupt_rows_dropped += 1
                            continue

                    writer.writerow(cleaned_row)
                    retained_row_count += 1

            elapsed = round(time.time() - start_time, 3)
            throughput = int(input_row_count / max(elapsed, 0.001))

            # 3. Create Audit Metrics Report
            audit_metrics = {
                "task_id": task_id,
                "job_id": job_id,
                "chunk_index": chunk_index,
                "input_rows": input_row_count,
                "retained_rows": retained_row_count,
                "duplicates_removed": duplicates_removed,
                "null_cells_cleaned": null_cells_cleaned,
                "pii_masked": pii_masked,
                "corrupt_rows_dropped": corrupt_rows_dropped,
                "duration_seconds": elapsed,
                "throughput_rows_per_sec": throughput,
                "columns_cleaned": len(normalized_columns),
                "column_names": normalized_columns
            }

            with open(local_audit_path, "w", encoding="utf-8") as af:
                json.dump(audit_metrics, af, indent=2)

            # 4. Upload outputs to MinIO
            clean_object_key = f"{job_id}/results/cleaned_chunk_{chunk_index}.csv"
            audit_object_key = f"{job_id}/results/audit_chunk_{chunk_index}.json"

            clean_url = storage.upload_result(bucket, local_clean_path, clean_object_key)
            audit_url = storage.upload_result(bucket, local_audit_path, audit_object_key)

            logger.info(
                f"[CSVCleaningStrategy] Chunk {chunk_index} finished in {elapsed}s: "
                f"{input_row_count} in -> {retained_row_count} out ({duplicates_removed} dups, "
                f"{null_cells_cleaned} nulls, {pii_masked} PII) at {throughput} rows/s"
            )

            return {
                "task_id": task_id,
                "status": "success",
                "clean_url": clean_url,
                "audit_url": audit_url,
                "input_rows": input_row_count,
                "retained_rows": retained_row_count,
                "duplicates_removed": duplicates_removed,
                "null_cells_cleaned": null_cells_cleaned,
                "pii_masked": pii_masked,
                "duration": elapsed,
                "throughput": throughput
            }

        finally:
            # Prevent worker disk leaks
            for p in (local_chunk_path, local_clean_path, local_audit_path):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

