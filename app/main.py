from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.dependencies import initialize_agents, shutdown_agents
from app.controllers import financial_manager_controller, health

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Financial Agent API...")
    await initialize_agents()
    logger.info("✅ Financial Agent API started successfully")

    yield

    logger.info("🛑 Shutting down Financial Agent API...")
    await shutdown_agents()
    logger.info("✅ Financial Agent API shutdown complete")


app = FastAPI(
    title=settings.app_name,
    description="Unified Financial Analysis Agent API with FastAPI and PydanticAI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(financial_manager_controller.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {
        "message": "Financial Agent API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/info")
async def info():
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug,
        "available_agents": ["financial_manager"]
    }