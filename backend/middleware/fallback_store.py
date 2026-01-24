# backend/middleware/fallback_store.py
import time
from collections import defaultdict, deque

FALLBACK_STORE = defaultdict(deque)
