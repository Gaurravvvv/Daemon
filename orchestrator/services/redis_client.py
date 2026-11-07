import os
import logging
import time
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class RedisManager:
    """
    Manages sliding-window ephemeral worker heartbeat leases.
    Uses Redis TTL (15s lease with 5s worker heartbeat).
    Falls back gracefully to memory/Mongo if Redis is temporarily unreachable.
    """
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        self.client = None
        self._memory_leases: Dict[str, float] = {}
        self.lease_ttl = 15  # seconds

    def connect(self):
        try:
            import redis
            self.client = redis.Redis.from_url(self.redis_url, decode_responses=True)
            self.client.ping()
            logger.info("Successfully connected to Redis for heartbeat leasing.")
        except Exception as e:
            logger.warning(f"Could not connect to Redis ({e}). Operating in in-memory fallback lease mode.")
            self.client = None

    def renew_lease(self, worker_id: str, pool_id: str = "public_pool") -> bool:
        """Set / renew worker lease with 15s expiration."""
        key = f"worker:{worker_id}:lease"
        val = f"{pool_id}:{int(time.time())}"
        if self.client:
            try:
                self.client.set(key, val, ex=self.lease_ttl)
                self.client.sadd("active_workers_set", worker_id)
                return True
            except Exception as e:
                logger.warning(f"Redis renew_lease failed ({e}), falling back to memory.")
                self.client = None
        
        self._memory_leases[worker_id] = time.time() + self.lease_ttl
        return True

    def is_worker_alive(self, worker_id: str) -> bool:
        key = f"worker:{worker_id}:lease"
        if self.client:
            try:
                return bool(self.client.exists(key))
            except Exception:
                self.client = None
        
        exp = self._memory_leases.get(worker_id, 0)
        return time.time() < exp

    def get_active_workers(self) -> List[str]:
        """Return list of worker_ids that currently hold a valid lease."""
        active = []
        if self.client:
            try:
                workers = self.client.smembers("active_workers_set")
                for w in workers:
                    if self.client.exists(f"worker:{w}:lease"):
                        active.append(w)
                    else:
                        self.client.srem("active_workers_set", w)
                return active
            except Exception:
                self.client = None
        
        now = time.time()
        for w, exp in list(self._memory_leases.items()):
            if now < exp:
                active.append(w)
            else:
                self._memory_leases.pop(w, None)
        return active

redis_manager = RedisManager()

