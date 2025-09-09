import time
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine
from app.models import models
from app.api.endpoints import data_extraction, eazybi, llm, analysis
from app.api.dependencies import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 5
RETRY_DELAY = 10  # seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting IT Operations Analytics API...")
    
    # Create tables with retry logic
    for i in range(MAX_RETRIES):
        try:
            models.Base.metadata.create_all(bind=engine)
            logger.info("Database tables created")
            break
        except OperationalError as e:
            logger.error(f"Database connection failed: {e}")
            if i < MAX_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error("Could not connect to the database. Exiting.")
                raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down IT Operations Analytics API...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="IT Operations Analytics with AI-powered insights",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    data_extraction.router, 
    prefix=f"{settings.API_V1_STR}/data", 
    tags=["data"]
)
app.include_router(
    eazybi.router, 
    prefix=f"{settings.API_V1_STR}/eazybi", 
    tags=["eazybi"]
)
app.include_router(
    llm.router, 
    prefix=f"{settings.API_V1_STR}/llm", 
    tags=["llm"]
)
app.include_router(
    analysis.router, 
    prefix=f"{settings.API_V1_STR}", 
    tags=["analysis"]
)


@app.get("/")
async def root():
    return {"message": "IT Operations Analytics API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "it-ops-analytics"}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)