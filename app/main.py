# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db import engine
from app.routers import books


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

app = FastAPI(title="Book API", version="1.0.0", lifespan=lifespan)
app.include_router(books.router)
