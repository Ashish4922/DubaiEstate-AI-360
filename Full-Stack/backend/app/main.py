"""DubaiEstate AI 360 - Full Stack backend (Day 1 skeleton).

Day 2 adds /health, Day 3 adds /api/transactions.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGIN

app = FastAPI(title="DubaiEstate AI 360 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["GET"],
    allow_headers=["*"],
)
