from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.responses.health import HealthResponse
from app.services import health as health_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
) -> HealthResponse:
    """Return service health status.

    Args:
        db: Injected async database session.
        response: FastAPI response object used to set status code.

    Returns:
        HealthResponse: Current health status including infrastructure checks.
    """
    result = await health_service.get_health(db)
    if result.status != "ok":
        response.status_code = 503
    return result
