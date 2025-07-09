import azure.functions as func
from dotenv import load_dotenv
load_dotenv()
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from WrapperFunction.api.v1 import assets, assets_metadata
from WrapperFunction.db.session import SessionLocal, test_direct_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Testing database connection...")
    if not test_direct_connection():
        logger.error("Failed to connect to database during startup")
        raise Exception("Database connection failed during startup")
    logger.info("Database connection successful")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(lifespan=lifespan)
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(assets_metadata.router, prefix="/api/v1/assets_metadata", tags=["Assets Metadata"])
