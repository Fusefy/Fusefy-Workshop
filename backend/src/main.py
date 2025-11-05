from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.agents.ocr import router as ocr_router
from src.api.claims import router as claims_router
from src.api.health import router as health_router
from src.config.database import close_db, init_db
from src.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.
    
    Handles database initialization on startup and cleanup on shutdown.
    """
    # Startup: Initialize database
    print("🚀 Starting Claims Reimbursement System...")
    await init_db()
    
    yield
    
    # Shutdown: Close database connections
    try:
        await close_db()
        print("Database connections closed")
    except Exception as e:
        print(f"Error closing database connections: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    description="A FastAPI backend for claims reimbursement processing with PostgreSQL support",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api")
app.include_router(claims_router, prefix="/api/v1", tags=["claims"])
app.include_router(ocr_router, tags=["agents"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Claims API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )