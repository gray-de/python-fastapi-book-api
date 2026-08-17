# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from typing import AsyncGenerator

from ..main import app
from ..db import get_session

# URL тестовой базы данных PostgreSQL (предварительно созданной)
TEST_DATABASE_URL = "postgresql+asyncpg://admin:password_12345@localhost:5432/book_db_test"


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    # Создаём асинхронный движок для тестовой БД
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        pool_size=5,
        max_overflow=10,
    )
    test_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False)

    # Пересоздаём таблицы перед каждым тестом
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    # Переопределяем зависимость сессии БД
    async def override_get_session():
        async with test_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # Создаём тестовый клиент
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Очистка после теста
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()
    app.dependency_overrides.clear()
