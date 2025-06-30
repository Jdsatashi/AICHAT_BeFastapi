import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.conf import settings
from src.conf.settings import ALLOW_ORIGIN, HOST, PORT, WORKERS, LOG_LEVEL, RELOAD_ENABLED
from src.dependencies.middlewares import PermissionMiddleware
from src.routers import routes
from src.utils.api_path import RoutePaths


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.scripts.migrate_tables import create_tables
    await create_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
    # dependencies=[Depends(user_auth)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PermissionMiddleware)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/")
def test_error():
    raise ValueError("-- This is the test error --")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected Server Error"}
    )


app.include_router(routes.router, prefix=RoutePaths.API_PREFIX)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        workers=WORKERS,
        log_level=LOG_LEVEL,
        reload=RELOAD_ENABLED,
        proxy_headers=True,
    )