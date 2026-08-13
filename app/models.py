from sqlmodel import SQLModel, Field


class BookBase(SQLModel):
    title: str = Field(index=True)
    author: str = Field(index=True)
    year: int
    genre: str


class Book(BookBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class BookRead(BookBase):
    id: int


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    genre: str | None = None
