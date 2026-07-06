"""
TrustCheck API.

Thin HTTP layer over risk_engine.py and safe_verify.py. Deliberately
thin: almost all the logic that matters lives in the dependency-free
modules so it can be unit tested directly. This file's job is request
validation and JSON shaping only.
"""

from dataclasses import asdict
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Permissive CORS for local development against the Vite dev server.
# Tighten this to explicit origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
