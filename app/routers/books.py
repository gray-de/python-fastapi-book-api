from fastapi import APIRouter, Depends, Query
from app import crud
from app.models import BookRead
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db import get_session

router = APIRouter(prefix="/books", tags=["books"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=list[BookRead])
async def read_books(session: SessionDep,
                     limit: Annotated[int, Query(100, ge=1, le=1000)],
                     offset: Annotated[int, Query(0, ge=0)],
                     genre: Annotated[str | None, Query()] = None):
    books = await crud.read_books(session, genre=genre,
                                  limit=limit, offset=offset)
    return books
