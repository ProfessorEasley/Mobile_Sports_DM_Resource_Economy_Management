from fastapi import FastAPI
from controllers.economy_controller import router as economy_router
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Economy Management API started successfully!")
    logger.info("📊 Available endpoints:")
    logger.info("   POST /api/v1/wallet/simulate - One-week wallet simulation")
    logger.info("   GET /api/v1/wallet/health - Economy health monitoring")
    logger.info("   GET /api/v1/wallet/health/history - Health analysis history")
    logger.info("   GET /api/v1/wallet/health/summary - Health status summary")
    logger.info("   GET /api/v1/wallet/simulate/browser - Browser-friendly wallet simulation")
    logger.info("   GET /health - API health check")
    logger.info("🌐 Server running at: http://localhost:8000")
    logger.info("📖 API docs available at: http://localhost:8000/docs")
    
    yield
    
    # Shutdown
    logger.info("🛑 Economy Management API shutting down...")

app = FastAPI(
    title="Economy Management API",
    description="API for wallet simulation and health monitoring",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(economy_router, prefix="/api/v1", tags=["economy"])

# Add health check endpoint
@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "service": "economy-api"}
