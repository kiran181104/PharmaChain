"""
Drug Traceability System - FastAPI Backend
Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth_router, drugs_router, verification_router, audit_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting Drug Traceability System Backend...")
    await connect_to_mongo()
    logger.info("Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Drug Traceability System Backend...")
    await close_mongo_connection()
    logger.info("Backend shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Drug Traceability System API",
    description="""
    Blockchain-based drug verification and traceability system API.
    
    ## Features
    
    * **User Management**: Register users with role-based access control
    * **Drug Registration**: Register drugs with composition validation
    * **Ownership Transfer**: Transfer drug ownership through supply chain
    * **Drug Verification**: Verify drug authenticity and traceability
    * **Audit & Monitoring**: Regulator dashboard for system oversight
    
    ## Roles
    
    * MANUFACTURER - Can register new drugs
    * DISTRIBUTOR - Can receive and transfer drugs
    * PHARMACY - Can receive and verify drugs (end of chain)
    * CONSUMER - Can only verify drugs
    * REGULATOR - Can audit all records (read-only)
    
    ## Security
    
    * Blockchain-based immutable records
    * SHA-256 composition hashing
    * MetaMask wallet authentication
    * Role-based access control
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(drugs_router)
app.include_router(verification_router)
app.include_router(audit_router)


@app.get("/")
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "status": "online",
        "service": "Drug Traceability System API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    from app.database import get_database
    
    db = get_database()
    db_status = "connected" if db else "disconnected"
    dataset_count = 0
    
    if db:
        try:
            dataset_count = await db.drug_composition_dataset.count_documents({})
        except Exception as e:
            logger.warning(f"Could not count dataset documents: {str(e)}")
    
    return {
        "status": "healthy" if db and dataset_count > 0 else "degraded" if db else "critical",
        "database": db_status,
        "drug_dataset_seeded": dataset_count > 0,
        "drug_dataset_count": dataset_count,
        "blockchain": "available",
        "note": "If database is disconnected, check MONGODB_URL environment variable. If dataset_count is 0, call POST /api/drugs/dataset/seed to initialize."
    }


@app.get("/init-check")
async def initialization_check():
    """
    Detailed initialization check for debugging deployment issues
    """
    from app.database import get_database, database
    from app.config import settings
    
    db = get_database()
    
    check_result = {
        "timestamp": datetime.utcnow().isoformat(),
        "app_version": "1.0.0",
        "database": {
            "connected": db is not None,
            "mongodb_url_set": bool(settings.MONGODB_URL),
            "mongodb_url_preview": settings.MONGODB_URL[:30] + "..." if settings.MONGODB_URL else "NOT SET",
            "database_name": settings.MONGODB_DB_NAME,
            "client_available": database.client is not None
        }
    }
    
    if db:
        try:
            dataset_count = await db.drug_composition_dataset.count_documents({})
            datasets = await db.drug_composition_dataset.find({}).to_list(1)
            check_result["dataset"] = {
                "count": dataset_count,
                "sample": datasets[0].get("drugName") if datasets else None
            }
        except Exception as e:
            check_result["dataset"] = {
                "error": str(e)
            }
    else:
        check_result["dataset"] = {
            "count": 0,
            "error": "Database not connected"
        }
    
    return check_result


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
