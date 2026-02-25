from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.core.logger import setup_logging, logger
from app.core.config import settings
from app.core.error import AppBaseError
from app.api.auth import router as auth_router
from app.core.redis_conf import redis_service, broker

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_service.init()
    if not broker.is_worker_process:
        await broker.startup()
    yield
    await redis_service.close()
    if not broker.is_worker_process:
        await broker.shutdown()

app = FastAPI(title="Dizi US Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppBaseError)
async def app_base_error_handler(request: Request, exc: AppBaseError):
    error_data = exc.http()
    logger.error(f"Error {error_data.status_code}: {error_data.detail}")
    return JSONResponse(
        status_code=error_data.status_code,
        content={"error": error_data.detail}
    )

app.include_router(auth_router, prefix=settings.api.prefix)

@app.get("/health")
async def health():
    return {"status": "ok"}
