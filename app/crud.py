from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import Book, BookCreate, BookUpdate
from fastapi import HTTPException


async def read_books(
        session: AsyncSession,
        genre: str,
        limit: int = 100,
        offset: int = 0,
):
    statement = select(Book)
    if genre:
        statement = statement.where(Book.genre == genre)
    statement = statement.offset(offset).limit(limit)
    result = await session.exec(statement)
    return result.all()


async def get_book(session: AsyncSession,
                   book_id: int):
    book = await session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


async def create_book(session: AsyncSession,
                      book: BookCreate):
    validated_book = Book.model_validate(book)
    session.add(validated_book)
    await session.commit()
    await session.refresh(validated_book)
    return validated_book


async def delete_book(session: AsyncSession, book_id: int):
    db_book = await get_book(session, book_id)
    if db_book:
        await session.delete(db_book)
        await session.commit()
        return True
    return False


async def update_book(session: AsyncSession,
                      book_id: int,
                      book_update: BookUpdate):
    db_book = await session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_book, key, value)
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book
