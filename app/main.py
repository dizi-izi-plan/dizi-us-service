from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse

from app.api.v1 import v1_router
from app.api.v2 import v2_router
from app.core.error import AppBaseError
from app.core.logger import setup_logging, get_logger
from app.core.redis_conf import broker, redis_service

setup_logging()
logger = get_logger(__name__)


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


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")


@app.get("/health")
async def health():
    return {"status": "ok_v1"}
