# main.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from api.routes import router
from database.seed import create_tables, seed_data
from rag.ingest import ingest_lease, get_collection
import traceback
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
try:
    create_tables()
    seed_data()
except Exception as e:
    logger.warning(f"Database setup warning: {e}")

# RAG setup
try:
    collection = get_collection()
    if collection.count() == 0:
        print("ChromaDB empty — ingesting lease PDF...")
        ingest_lease()
        print("Lease ingestion complete.")
    else:
        print(f"ChromaDB ready — {collection.count()} chunks loaded.")
except Exception as e:
    logger.warning(f"RAG setup warning: {e}")

app = FastAPI(title="Property Management Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = traceback.format_exc()
    logger.error(f"Unhandled error: {error_detail}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": error_detail}
    )

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return FileResponse("static/index.html")