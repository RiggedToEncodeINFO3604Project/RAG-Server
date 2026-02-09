"""
Route map:
    GET  /api/health   →  liveness probe (Render healthCheckPath)
    GET  /api/status   →  lightweight status check for mobile apps
    POST /api/chat     →  { message, history } → { answer, matchedSections }
    GET  /*            →  serve index.html (SPA catch-all)

"""

import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator

from .gemini_client import chat

# Load environment variables from .env
load_dotenv(Path(__file__).resolve().parent / ".env")

# Logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("skedulelt.server")

# Paths 
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Environment Configuration 
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8081,http://localhost:19000,http://localhost:19006,http://localhost:8000"
).split(",")

ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]
log.info(f"Configured ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")

# FastAPI app 
app = FastAPI(
    title="Skedulelt RAG API",
    description="Long-Context RAG chatbot for Skedulelt mobile app",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
    expose_headers=["Content-Length"],
)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"
    log.info(f"→ {request.method} {request.url.path} from {client_host}")
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    log.info(f"← {request.method} {request.url.path} completed in {process_time:.0f}ms [{response.status_code}]")
    return response

# Mount Static Files 
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    log.info(f"Mounted static files from {STATIC_DIR}")

# Pydantic Schemas 

class HistoryTurn(BaseModel):
    role: str
    text: str = Field(..., max_length=2000)
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant']:
            raise ValueError('role must be "user" or "assistant"')
        return v

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: list[HistoryTurn] = Field(default=[], max_items=50)
    
    @validator('message')
    def validate_message(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('message cannot be empty')
        return v
    
    @validator('history')
    def validate_history_length(cls, v):
        if len(v) > 50:
            raise ValueError('History cannot exceed 50 messages')
        return v

class ChatResponse(BaseModel):
    answer: str
    matchedSections: list[str]

# Routes 

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "model": "gemini-1.5-flash",
        "approach": "long-context-stateless",
        "timestamp": time.time(),
    }

@app.get("/api/status")
async def status():
    return {"status": "online", "timestamp": time.time()}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest):
    history_dicts = [{"role": t.role, "text": t.text} for t in body.history]
    
    try:
        log.info(f"Processing message: {body.message[:50]}...")
        result = await chat(history_dicts, body.message)
        log.info(f"Response generated ({len(result.answer)} chars)")
        return ChatResponse(answer=result.answer, matchedSections=result.matched_sections)
    
    except Exception as e:
        error_msg = str(e)
        log.error(f"Chat error: {error_msg}", exc_info=True)
        
        if any(x in error_msg.lower() for x in ["429", "quota", "rate limit"]):
            log.warning("Rate limit hit")
            raise HTTPException(status_code=429, detail={"error": "rate_limit", "message": "Too many requests. Please wait.", "retry_after": 60})
        
        if any(x in error_msg.lower() for x in ["api key", "authentication", "unauthorized"]):
            log.error("API key error")
            raise HTTPException(status_code=500, detail={"error": "configuration", "message": "Server error. Contact support."})
        
        if any(x in error_msg.lower() for x in ["overloaded", "unavailable", "timeout"]):
            log.warning("Gemini unavailable")
            raise HTTPException(status_code=503, detail={"error": "service_unavailable", "message": "AI service busy. Try again."})
        
        if any(x in error_msg.lower() for x in ["safety", "blocked", "violation"]):
            log.warning("Safety filter")
            raise HTTPException(status_code=400, detail={"error": "content_blocked", "message": "Message blocked by filters."})
        
        raise HTTPException(status_code=500, detail={"error": "internal_server_error", "message": "Unexpected error."})

@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    log.warning(f"Validation error: {exc}")
    return JSONResponse(status_code=422, content={"error": "validation_error", "message": "Invalid request.", "details": exc.errors() if hasattr(exc, 'errors') else str(exc)})

_INDEX_HTML: str | None = None

def _read_index() -> str:
    global _INDEX_HTML
    if _INDEX_HTML is None:
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            _INDEX_HTML = index_path.read_text(encoding="utf-8")
        else:
            _INDEX_HTML = "<h1>API Server</h1><p>Use POST /api/chat</p>"
    return _INDEX_HTML

@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    return HTMLResponse(content=_read_index())

@app.on_event("startup")
async def startup_event():
    log.info("=" * 60)
    log.info("Skedulelt RAG API Server Starting")
    log.info("=" * 60)
    log.info(f"Model: gemini-1.5-flash")
    log.info(f"Approach: Long Context, stateless, queued")
    log.info(f"CORS Origins: {ALLOWED_ORIGINS}")
    log.info(f"Static files: {STATIC_DIR.exists()}")
    log.info("=" * 60)
