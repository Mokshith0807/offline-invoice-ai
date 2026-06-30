import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.database import init_db, cleanup_connection
from app.api.routes import router
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_dirs()
    logger = setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    logger.info(f"Upload dir: {settings.upload_dir}")
    logger.info(f"Database dir: {settings.database_dir}")
    logger.info(f"Models dir: {settings.models_dir}")
    yield
    cleanup_connection()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

frontend_dist = Path(__file__).resolve().parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    logger.info(f"Serving frontend from {frontend_dist}")
else:
    logger.info("Frontend dist not found — API-only mode")

    @app.get("/")
    async def root():
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/health",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        workers=1,
    )
