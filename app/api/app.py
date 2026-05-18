from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import admin_router, public_router
from app.infrastructure.database import init_db


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def create_app() -> FastAPI:
    init_db(seed=True)

    fastapi_app = FastAPI(
        title="NEO-SYNC API",
        version="2.0.0",
        description="Layered FastAPI backend for cyberpunk maintenance station diploma project.",
    )

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_app.include_router(public_router)
    fastapi_app.include_router(admin_router)
    fastapi_app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return fastapi_app
