from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
import itertools
import threading
import time
from typing import Dict, Tuple

app = FastAPI(title="Reverse Proxy")

# nodurile DW din rețeaua docker
DW_SERVERS = [
    "http://dw1:8001",
    "http://dw2:8001",
]

_rr_iter = itertools.cycle(DW_SERVERS)

CacheValue = Tuple[float, int, Dict[str, str], bytes]
cache: Dict[str, CacheValue] = {}
cache_lock = threading.Lock()
CACHE_TTL = 30.0  # secunde

client = httpx.AsyncClient(timeout=5.0)


def make_cache_key(method: str, path: str, query: str) -> str:
    if method != "GET":
        return ""
    return f"{method}:{path}:{query}"


@app.middleware("http")
async def proxy_handler(request: Request, call_next):
    method = request.method
    path = request.url.path
    query = request.url.query
    body = await request.body()
    now = time.time()

    cache_key = make_cache_key(method, path, query)

    # 1. Cache HIT
    if cache_key:
        with cache_lock:
            if cache_key in cache:
                exp, code, headers, data = cache[cache_key]
                if exp > now:
                    print(f"[PROXY] Cache HIT {path}?{query}")
                    return Response(
                        content=data,
                        status_code=code,
                        headers=headers,
                    )

    # 2. Alegem backend în round-robin
    backend = next(_rr_iter)
    url = backend + path
    if query:
        url += f"?{query}"

    print(f"[PROXY] Forward {method} {path}?{query} -> {backend}")

    try:
        resp = await client.request(
            method,
            url,
            content=body,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )
    except Exception as e:
        print(f"[PROXY] Backend error: {e}")
        return Response(f"Backend error: {e}", status_code=502)

    data = resp.content
    status = resp.status_code
    headers = dict(resp.headers)

    # 3. Cache save pentru GET 200
    if cache_key and status == 200:
        with cache_lock:
            cache[cache_key] = (
                now + CACHE_TTL,
                status,
                headers,
                data,
            )

    # 4. Invalidare cache la scriere
    if method in ("POST", "PUT", "DELETE"):
        with cache_lock:
            cache.clear()
        print("[PROXY] Cache cleared on write")

    return Response(content=data, status_code=status, headers=headers)
