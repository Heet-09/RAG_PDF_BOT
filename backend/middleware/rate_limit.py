# backend/middleware/rate_limit.py
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from rate_limit_config import RATE_LIMITS
from middleware.fallback_limiter import fallback_rate_limit



class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        ip = request.client.host
        user_id = request.headers.get("x-user-id")

        print(
            f"\n[RATE LIMIT] Incoming request | "
            f"PATH={path} | IP={ip} | USER_ID={user_id}"
        )

        # ───────────── Load config ─────────────
        config = RATE_LIMITS.get(path, RATE_LIMITS["default"])
        limit = config["limit"]
        window = config["window"]

        print(
            f"[RATE LIMIT] Config | "
            f"LIMIT={limit} | WINDOW={window}s"
        )

        # ───────────── Build key ─────────────
        if user_id:
            key = f"rate:user:{user_id}:{path}"
            print(f"[RATE LIMIT] Key type | USER → {key}")
        else:
            key = f"rate:ip:{ip}:{path}"
            print(f"[RATE LIMIT] Key type | IP → {key}")

        # ───────────────── Redis path ─────────────────
        try:
            print("[RATE LIMIT] Redis path → INCR")

            count = redis_client.incr(key)

            if count == 1:
                redis_client.expire(key, window)
                print(
                    f"[RATE LIMIT] New window started | "
                    f"KEY={key} | TTL={window}s"
                )

            ttl = redis_client.ttl(key)

            print(
                f"[RATE LIMIT] Redis state | "
                f"COUNT={count} | TTL={ttl}s"
            )

            if count > limit:
                print(
                    f"[RATE LIMIT] BLOCKED ❌ (Redis) | "
                    f"COUNT={count} > LIMIT={limit}"
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many requests",
                        "retry_after": ttl
                    },
                    headers={"Retry-After": str(ttl)}
                )

        # ─────────────── FALLBACK PATH ───────────────
        except Exception as e:
            print(
                f"[RATE LIMIT] Redis error ⚠️ | "
                f"{type(e).__name__}: {e}"
            )
            print("[RATE LIMIT] Switching to FALLBACK limiter")

            allowed, retry_after = fallback_rate_limit(
                key, limit, window
            )

            if not allowed:
                print(
                    f"[RATE LIMIT] BLOCKED ❌ (Fallback) | "
                    f"RETRY_AFTER={retry_after}s"
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many requests (fallback)",
                        "retry_after": retry_after
                    },
                    headers={"Retry-After": str(retry_after)}
                )

            print("[RATE LIMIT] Fallback ALLOWED ✅")

        print("[RATE LIMIT] ALLOWED ✅")
        return await call_next(request)
