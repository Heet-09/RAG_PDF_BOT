# backend/rate_limit_config.py
RATE_LIMITS = {
    "/auth/login": {"limit": 5, "window": 60},
    "/auth/signup": {"limit": 3, "window": 60},

    "/ask": {"limit": 1, "window": 3600},
    "/upload": {"limit": 5, "window": 3600},

    "default": {"limit": 60, "window": 60},
}
