# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db import engine
from app.routers import books

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Db crerated successfully")
    except Exception as e:
        logger.info(f"Failed to create db: {e}")
        raise

    yield
    await engine.dispose()
    logger.info("Db connection closed")

app = FastAPI(title="Book API", version="1.0.0", lifespan=lifespan)
app.include_router(books.router)
