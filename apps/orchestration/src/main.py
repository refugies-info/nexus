"""
Nexus Orchestration Service - FastAPI Application Entry Point

This module initializes and configures the FastAPI application for the Nexus
pipeline orchestration service. It sets up middleware, routes, and health checks.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Nexus Orchestration Service")
    yield
    # Shutdown
    logger.info("Shutting down Nexus Orchestration Service")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Nexus Orchestration API",
        description="Pipeline orchestration service for Nexus AI pipeline",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for monitoring and load balancers."""
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "nexus-orchestration",
                "version": "0.1.0",
            },
        )

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Nexus Orchestration API",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
        }

    logger.info("FastAPI application created successfully")
    return app


# Create application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
