from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

import time
import os

from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.config.env_config import env_namespace

logger = get_logger("api.app")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="GDIF API",
        description="General Data Intelligence Framework API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Use SECRET_KEY from env_namespace
    secret_key = env_namespace.SECRET_KEY or os.getenv("SESSION_SECRET_KEY", "development-session-key")
    app.add_middleware(SessionMiddleware, secret_key=secret_key)

    class TimingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            start_time = time.time()
            response: Response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            logger.info(f"{request.method} {request.url} - {process_time:.4f}s")
            return response

    app.add_middleware(TimingMiddleware)

    try:
        from data_intelligence_system.api.routers import (
            etl_router,
            analysis_router,
            reports_router,
            dashboard_router,
        )

        app.include_router(etl_router.router, prefix="/etl", tags=["ETL"])
        app.include_router(analysis_router.router, prefix="/analysis", tags=["Analysis"])
        app.include_router(reports_router.router, prefix="/reports", tags=["Reports"])
        app.include_router(dashboard_router.router, prefix="/dashboard", tags=["Dashboard"])

        logger.info("✅ Routers registered successfully.")
    except ImportError as e:
        logger.warning(f"⚠️ Failed to import Routers: {e}")

    logger.info("🚀 FastAPI application created and configured.")
    return app


app = create_app()
