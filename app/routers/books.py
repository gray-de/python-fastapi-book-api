from fastapi import APIRouter, Depends, Query, Path
from app import crud
from app.models import BookRead, BookCreate, BookUpdate
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db import get_session
from redis.asyncio import Redis
import json
from fastapi.responses import JSONResponse, Response

router = APIRouter(prefix="/books", tags=["books"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=None)
async def read_books(session: SessionDep,
                     limit: Annotated[int, Query(ge=1, le=1000)] = 100,
                     offset: Annotated[int, Query(ge=0)] = 0,
                     genre: Annotated[str | None, Query()] = None):

    books = await crud.read_books(session, genre=genre, offset=offset, limit=limit)
    books_data = [book.model_dump() for book in books]
    json_str = json.dumps(books_data)

    return Response(content=json_str, media_type="application/json")


@router.get("/{book_id}", response_model=BookRead)
async def read_book(session: SessionDep,
                    book_id: Annotated[int, Path(ge=0)]):
    book = await crud.get_book(session=session, book_id=book_id)
    return book


@router.post("/", response_model=BookRead, status_code=201)
async def create_book(session: SessionDep, book: BookCreate):
    book = await crud.create_book(session=session, book=book)
    return book


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session)):
    success = await crud.delete_book(session, book_id)
    return None


@router.put("/{book_id}", response_model=BookRead)
async def update_book(session: SessionDep,
                      book_id: Annotated[int, Path(ge=0)],
                      book_update: BookUpdate):
    updated_book = await crud.update_book(session=session, book_id=book_id,
                                          book_update=book_update)
    return updated_book
