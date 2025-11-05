from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.config.database import get_db, db_config

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    database: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        database="unknown",
        version="1.0.0"
    )


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check including database connectivity."""
    health_info = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": {"status": "healthy", "message": "API is running"},
            "database": {"status": "unknown", "message": "Database status unknown"}
        }
    }
    
    # Check database connectivity
    if db_config.session_factory:
        try:
            async with db_config.session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    health_info["services"]["database"] = {
                        "status": "healthy",
                        "message": "Database connection successful"
                    }
        except Exception as e:
            health_info["services"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
            health_info["status"] = "degraded"
    else:
        health_info["services"]["database"] = {
            "status": "unavailable",
            "message": "Database not initialized"
        }
        health_info["status"] = "degraded"
    
    return health_info