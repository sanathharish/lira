from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lira.api")

app = FastAPI(title="Lira API", version="0.1")

# Allow Next.js frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}