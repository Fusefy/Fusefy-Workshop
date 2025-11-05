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
    import os
    import platform
    import time
    
    # Get version (fallback to default if not available)
    try:
        from src import __version__
        app_version = __version__
    except ImportError:
        app_version = "1.0.0"
    
    # Start time tracking (in real implementation, this would be stored when app starts)
    start_time = time.time()
    
    database_status = "unknown"
    database_message = "Database status unknown"
    overall_status = "healthy"
    
    # Check database connectivity
    if db_config.session_factory:
        try:
            async with db_config.session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    database_status = "healthy"
                    database_message = "Database connection successful"
        except Exception as e:
            database_status = "unhealthy"
            database_message = f"Database connection failed: {str(e)}"
            overall_status = "degraded"
    else:
        database_status = "unavailable"
        database_message = "Database not initialized"
        overall_status = "degraded"
    
    health_info = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": app_version,
        "database": {
            "status": database_status,
            "message": database_message
        },
        "system": {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count()
        },
        "uptime_seconds": int(time.time() - start_time),
        "services": {
            "api": {"status": "healthy", "message": "API is running"},
            "database": {
                "status": database_status,
                "message": database_message
            }
        }
    }
    
    return health_info