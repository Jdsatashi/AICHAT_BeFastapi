import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from starlette.responses import JSONResponse

from src.conf import settings
from src.dependencies.auth import user_auth
from src.routers import routes


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


app.include_router(routes.router, prefix="/comepass/api/v1")
