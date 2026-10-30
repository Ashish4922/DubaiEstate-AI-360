"""Main API Router aggregating versioned route handlers.

Day 1 establishes this routing skeleton.
Day 2 will include the health check endpoint: /api/v1/health
Day 3 will include the transactions endpoints: /api/v1/transactions
"""

from fastapi import APIRouter

api_router = APIRouter()

# Future versioned routers will be included here:
# e.g.:
# from app.api.v1.endpoints import health, transactions
# api_router.include_router(health.router, prefix="/health", tags=["Health"])
# api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
