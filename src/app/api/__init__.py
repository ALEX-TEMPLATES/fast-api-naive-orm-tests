from fastapi import APIRouter

from .example import router as example_router

api_router = APIRouter()
api_router.include_router(example_router, prefix="/examples", tags=["examples"])

__all__ = ["api_router"]
