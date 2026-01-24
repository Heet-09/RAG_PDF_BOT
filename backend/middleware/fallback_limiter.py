# backend/middleware/fallback_limiter.py
import time
from middleware.fallback_store import FALLBACK_STORE

def fallback_rate_limit(key: str, limit: int, window: int):
    now = time.time()
    timestamps = FALLBACK_STORE[key]

    print(f"[RateLimiter] Key={key}")
    print(f"[RateLimiter] Now={now}")
    print(f"[RateLimiter] Existing timestamps(before cleanup)={list(timestamps)}")

    # remove old timestamps
    while timestamps and timestamps[0] <= now - window:
        removed = timestamps.popleft()
        print(f"[RateLimiter] Removed old timestamp={removed}")

    print(f"[RateLimiter] Timestamps(after cleanup)={list(timestamps)}")
    print(f"[RateLimiter] Count={len(timestamps)}, Limit={limit}")

    if len(timestamps) >= limit:
        retry_after = int(window - (now - timestamps[0]))
        print(f"[RateLimiter] LIMIT HIT → retry_after={retry_after}s")
        return False, retry_after

    timestamps.append(now)
    print(f"[RateLimiter] Allowed → appended timestamp={now}")
    print(f"[RateLimiter] Final timestamps={list(timestamps)}")

    return True, None
