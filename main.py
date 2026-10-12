from contextlib import asynccontextmanager

from fastapi import FastAPI

import database.models  # noqa: F401
from database.db import Base, engine
from routes.contacts import router as contacts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Contacts API",
    description="REST API для зберігання та управління контактами",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(contacts_router)
