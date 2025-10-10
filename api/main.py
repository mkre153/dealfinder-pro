"""
DealFinder Pro - FastAPI Backend
Exposes autonomous property search agents as REST API for Next.js frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from api.routes import agents, chat, properties
from modules.agent_manager import get_agent_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    """
    # Startup
    logger.info("Starting DealFinder Pro API")

    # Initialize agent manager (starts background scheduler)
    agent_manager = get_agent_manager()
    logger.info(f"Agent manager initialized with {len(agent_manager.active_agents)} active agents")

    yield

    # Shutdown
    logger.info("Shutting down DealFinder Pro API")


# Create FastAPI app
app = FastAPI(
    title="DealFinder Pro API",
    description="Autonomous property search agents powered by AI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local Next.js dev
        "http://localhost:3001",
        "https://dealfinder.app",  # Production domain
        "https://*.vercel.app",    # Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])
app.include_router(properties.router, prefix="/api/properties", tags=["Properties"])


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "DealFinder Pro API",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    agent_manager = get_agent_manager()
    system_status = agent_manager.get_system_status()

    return {
        "status": "healthy",
        "scheduler_running": system_status["scheduler_running"],
        "active_agents": system_status["active_agents"],
        "total_matches": system_status["total_matches"]
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
