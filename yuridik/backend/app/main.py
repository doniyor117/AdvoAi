"""
Imtiyoz-AI FastAPI Main Application
Production-ready async backend for the RAG-based legal assistant.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.routers import chat, scout
from app.models.schemas import HealthResponse


# Global state for shared resources
class AppState:
    """Application state container for shared resources."""
    chroma_client = None
    chroma_collection = None
    rag_engine = None
    scout_status_queue: asyncio.Queue = None


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifecycle manager for FastAPI application.
    Initializes ChromaDB and other resources on startup.
    """
    settings = get_settings()
    print(f"🚀 Starting {settings.app_name}...")
    
    # Initialize ChromaDB
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        app_state.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        app_state.chroma_collection = app_state.chroma_client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"description": "Uzbek legal documents for entrepreneur privileges"}
        )
        
        doc_count = app_state.chroma_collection.count()
        print(f"✅ ChromaDB initialized with {doc_count} documents")
        
    except Exception as e:
        print(f"⚠️ ChromaDB initialization warning: {e}")
    
    # Initialize status queue for Scout Agent
    app_state.scout_status_queue = asyncio.Queue()
    print("✅ Scout status queue initialized")
    
    # Check LLM API key
    if not settings.active_api_key:
        print(f"⚠️ Warning: No API key found for {settings.llm_provider}")
    else:
        print(f"✅ LLM provider: {settings.llm_provider} ({settings.llm_model})")
    
    print(f"🎯 {settings.app_name} is ready!")
    
    yield
    
    # Cleanup on shutdown
    print(f"👋 Shutting down {settings.app_name}...")


# Create FastAPI application
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered smart assistant for Uzbek entrepreneur privileges and subsidies",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Check application health and status."""
    doc_count = 0
    if app_state.chroma_collection:
        try:
            doc_count = app_state.chroma_collection.count()
        except Exception:
            pass
    
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version="1.0.0",
        document_count=doc_count,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name}!",
        "description": "AI-powered assistant for entrepreneur privileges in Uzbekistan",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(scout.router, prefix="/api/scout", tags=["Scout Agent"])


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={"error": str(exc), "type": type(exc).__name__}
        )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# Export app_state for use in routers
def get_app_state() -> AppState:
    """Get the application state."""
    return app_state
