---
task_id: 20261107-fill-daemon-gaps
title: "Fill Core Implementation Gaps in DaeMon Grid"
date: "2026-11-07"
status: complete
---

# Quick Plan: Fill All Core Implementation Gaps

## Objectives
1. Fix form parameter alignment (`split_count` vs `max_workers`) ensuring user-defined partition counts are respected.
2. Fix worker error handling so failures are properly retried and recorded without falsely reporting 100% progress.
3. Wire `MatrixMultiplicationStrategy` into `worker/consumer.py` for real GPU/CPU matrix multiplication.
4. Implement `CryptoSearchStrategy` in `worker/strategies/crypto_strategy.py` for parallel SHA-256 pre-image & PoW nonce searches.
5. Implement worker temporary storage cleanup (`shutil.rmtree` in `finally:` blocks) to prevent disk space leaks.
6. Build real result aggregator & deliverable stitcher in `orchestrator/core/aggregator.py`.
7. Implement sliding-window Redis heartbeat leasing (`RedisManager`) and active node registry with sub-15s TTL churn recovery.
8. Deduplicate worker node announcements on the live event stream.
9. Fix `docker-compose.yml` to use named volumes (`minio_data`) instead of hardcoded host drive paths.
10. Update Next.js dashboard to show live active node counts and strategy alignment.

