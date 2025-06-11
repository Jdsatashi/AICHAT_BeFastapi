from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

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
    dependencies=[Depends(user_auth)],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(routes.router, prefix="/comepass/api/v1")
