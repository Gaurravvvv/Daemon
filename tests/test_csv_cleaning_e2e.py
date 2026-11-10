import os
import sys
import csv
import json
import shutil
import tempfile

# Add project root, orchestrator, and worker to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "orchestrator"))
sys.path.insert(0, os.path.join(BASE_DIR, "worker"))

from core.csv_splitter import CSVSplitter
from strategies.csv_cleaning import CSVCleaningStrategy

def test_csv_pipeline_e2e():
    print("==================================================")
    print("   RUNNING END-TO-END CSV CLEANING PIPELINE TEST  ")
    print("==================================================")

    test_dir = tempfile.mkdtemp(prefix="daemon_test_csv_")

    try:
        # 1. Create a synthetic dirty CSV
        dirty_csv_path = os.path.join(test_dir, "dirty_input.csv")
        headers = ["Customer ID (#)", " Full Name ", "Email Address", "Phone Number", "Signup Date", "Spend ($)"]
        rows = [
            ["CUST-001", " Alice Smith ", "alice@example.com", "555-0199", "15/08/2024", "$120.50"],
            ["CUST-001", " Alice Smith ", "alice@example.com", "555-0199", "15/08/2024", "$120.50"], # Exact duplicate
            ["CUST-002", "Bob Jones", "N/A", "(800) 555-1212", "2023-01-05", "null"],             # Sentinel nulls
            ["CUST-003", "Charlie Brown", "charlie.b@corp.org", "987-654-3210", "None", "-"],       # Sentinel nulls + PII
            ["CUST-004", "Diana Prince", "?", "555-999-0000", "05/12/2022", "$3,500.00"],
            ["CUST-002", "Bob Jones", "N/A", "(800) 555-1212", "2023-01-05", "null"],             # Duplicate 2
        ]

        with open(dirty_csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"Created dirty test CSV with {len(rows)} data rows (2 duplicates, multiple sentinel nulls, emails, phones).")

        # 2. Test Streaming Partitioner
        # Mock MinIO upload_bytes for testing
        from services.storage import storage
        original_upload_bytes = storage.upload_bytes
        uploaded_chunks = {}

        def mock_upload_bytes(data: bytes, object_name: str, content_type: str = "text/csv") -> str:
            uploaded_chunks[object_name] = data
            return f"minio://daemon-jobs/{object_name}"

        storage.upload_bytes = mock_upload_bytes

        tasks = CSVSplitter.partition_csv(
            job_id="test-job-101",
            csv_file_path=dirty_csv_path,
            split_count=2,
            rules={
                "deduplicate": True,
                "clean_headers": True,
                "standardize_nulls": True,
                "redact_pii": True,
                "standardize_dates": True,
                "null_threshold_pct": 80
            }
        )

        assert len(tasks) == 2, f"Expected 2 partitioned chunks, got {len(tasks)}"
        print(f"✓ Splitter verified: Successfully created {len(tasks)} row-aligned chunks.")

        # 3. Test Worker Cleaning Strategy on each chunk
        # Mock worker storage download and upload
        import strategies.csv_cleaning as csv_strat_mod
        original_worker_download = csv_strat_mod.storage.download_data
        original_worker_upload = csv_strat_mod.storage.upload_result

        def mock_worker_download(bucket, object_name, file_path):
            if object_name in uploaded_chunks:
                with open(file_path, "wb") as f:
                    f.write(uploaded_chunks[object_name])
                return file_path
            return None

        cleaned_files = {}
        def mock_worker_upload(bucket, file_path, object_name):
            with open(file_path, "rb") as f:
                cleaned_files[object_name] = f.read()
            return f"minio://{bucket}/{object_name}"

        csv_strat_mod.storage.download_data = mock_worker_download
        csv_strat_mod.storage.upload_result = mock_worker_upload

        worker_results = []
        for task in tasks:
            res = CSVCleaningStrategy.execute(task)
            assert res["status"] == "success"
            worker_results.append(res)
            print(f"✓ Worker cleaned chunk {task['chunk_index']}: {res['retained_rows']} rows retained, {res['duplicates_removed']} dups, {res['pii_masked']} PII scrubbed.")

        # 4. Verify Content of Cleaned Chunks
        total_worker_retained = sum(r["retained_rows"] for r in worker_results)
        total_worker_dups = sum(r["duplicates_removed"] for r in worker_results)
        total_pii = sum(r["pii_masked"] for r in worker_results)

        assert total_worker_retained == 5, f"Expected 5 clean rows across isolated worker chunks, got {total_worker_retained}"
        assert total_worker_dups == 1, f"Expected 1 intra-chunk dropped duplicate, got {total_worker_dups}"
        assert total_pii >= 4, f"Expected at least 4 PII redactions (emails/phones), got {total_pii}"

        # 5. Verify Aggregator Master Stitching & Cross-Chunk Deduplication
        import hashlib
        global_seen_hashes = set()
        master_rows = []
        master_dups = total_worker_dups
        
        for task in tasks:
            chunk_file_key = f"test-job-101/results/cleaned_chunk_{task['chunk_index']}.csv"
            chunk_csv = cleaned_files[chunk_file_key].decode("utf-8")
            lines = [l for l in chunk_csv.splitlines() if l.strip()]
            for line in lines[1:]: # Skip header
                row_hash = hashlib.md5(line.strip().encode("utf-8")).hexdigest()
                if row_hash in global_seen_hashes:
                    master_dups += 1
                    continue
                global_seen_hashes.add(row_hash)
                master_rows.append(line)

        assert len(master_rows) == 4, f"Expected exactly 4 unique master rows after cross-chunk deduplication, got {len(master_rows)}"
        assert master_dups == 2, f"Expected exactly 2 total duplicates eliminated, got {master_dups}"
        print(f"✓ Master Aggregation verified: Exactly {len(master_rows)} unique rows retained, {master_dups} total duplicates eliminated.")

        # Inspect first cleaned chunk content
        first_clean_csv_bytes = cleaned_files["test-job-101/results/cleaned_chunk_0.csv"]
        first_clean_text = first_clean_csv_bytes.decode("utf-8")
        lines = first_clean_text.splitlines()

        # Verify Header Normalization
        clean_header = lines[0]
        assert "customer_id" in clean_header
        assert "full_name" in clean_header
        assert "email_address" in clean_header
        print("✓ Headers verified: Converted to snake_case successfully:", clean_header)

        # Verify PII Scrubbing
        assert "[REDACTED_EMAIL]" in first_clean_text, "Failed to redact email address"
        assert "[REDACTED_PHONE]" in first_clean_text, "Failed to redact phone number"
        print("✓ PII Redaction verified: Email and phone numbers replaced with redact tags.")

        # Verify Sentinel Nulls
        assert "N/A" not in first_clean_text
        assert "null" not in first_clean_text.lower().split(",")
        print("✓ Sentinel Nulls verified: All 'N/A' and 'null' values standardized to empty cells.")

        print("==================================================")
        print("   ALL CSV CLEANING PIPELINE TESTS PASSED! (100%) ")
        print("==================================================")

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    test_csv_pipeline_e2e()
