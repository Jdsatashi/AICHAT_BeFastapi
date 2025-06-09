from fastapi import FastAPI

from src.conf import settings
from src.db.database import Base, engine
from src.routers import routes

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(routes.router)
