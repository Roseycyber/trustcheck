"""
TrustCheck API.

Thin HTTP layer over risk_engine.py and safe_verify.py. Deliberately
thin: almost all the logic that matters lives in the dependency-free
modules so it can be unit tested directly. This file's job is request
validation and JSON shaping only.
"""

import os
import time
from collections import defaultdict, deque
from dataclasses import asdict
from typing import Deque, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .domain import Category
from .risk_engine import assess_content
from .safe_verify import build_safe_verify

app = FastAPI(
    title="TrustCheck API",
    description=(
        "Situation-based scam checking with conservative, three-state "
        "verdicts and official-source verification guidance. "
        "This API never returns a result confirming something is safe "
        "or genuine - see docs/SAFETY_PRINCIPLES.md in the repo."
    ),
    version="0.1.0",
)

# CORS: driven by TRUSTCHECK_ALLOWED_ORIGINS (comma-separated). The
# default "*" is for local development only - set explicit origins in
# any real deployment. Kept out of code so tightening it doesn't need
# a code change.
_allowed_origins = [
    origin.strip()
    for origin in os.environ.get("TRUSTCHECK_ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

# Rate limiting: simple in-memory sliding window per client IP.
# Deliberately dependency-free and honest about its limits: it protects
# a single process against casual abuse (added after a security review
# noted an unauthenticated, CPU-doing endpoint with no limiter). It is
# NOT sufficient for multi-worker or multi-instance deployments - use a
# shared store (e.g. Redis) or an upstream gateway limiter for that.
RATE_LIMIT_REQUESTS = int(os.environ.get("TRUSTCHECK_RATE_LIMIT", "30"))
RATE_LIMIT_WINDOW_SECONDS = 60
_request_log: Dict[str, Deque[float]] = defaultdict(deque)


@app.middleware("http")
async def rate_limit_check_endpoint(request: Request, call_next):
    if request.url.path == "/api/check":
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = _request_log[client_ip]
        while window and now - window[0] > RATE_LIMIT_WINDOW_SECONDS:
            window.popleft()
        if len(window) >= RATE_LIMIT_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        "Too many checks in a short time - please wait a "
                        "minute and try again."
                    )
                },
            )
        window.append(now)
    return await call_next(request)


class CheckRequestBody(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The message, offer, or link text the user is unsure about.",
    )
    category: Optional[Category] = Field(
        default=Category.OTHER,
        description="What the content is about: job, bank, healthcare, brand, or other.",
    )


class SafeVerifyEntryOut(BaseModel):
    label: str
    value: str


class SafeVerifyOut(BaseModel):
    heading: str
    instructions: str
    entries: List[SafeVerifyEntryOut]
    disclaimer: str


class CheckResponseBody(BaseModel):
    verdict: str
    verdict_label: str
    reasons: List[str]
    safe_verify: SafeVerifyOut


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/check", response_model=CheckResponseBody)
def check_content(payload: CheckRequestBody) -> CheckResponseBody:
    verdict, verdict_label, reasons = assess_content(payload.content, payload.category)
    safe_verify = build_safe_verify(payload.content, payload.category)

    return CheckResponseBody(
        verdict=verdict.value,
        verdict_label=verdict_label,
        reasons=reasons,
        safe_verify=SafeVerifyOut(**asdict(safe_verify)),
    )
