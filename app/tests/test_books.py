# tests/test_books.py
import pytest


@pytest.mark.asyncio
async def test_create_book(async_client):
    payload = {
        "title": "Test Book",
        "author": "Tester",
        "year": 2024,
        "genre": "fiction"
    }
    response = await async_client.post("/books/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Tester"
    assert data["year"] == 2024
    assert data["genre"] == "fiction"
    assert "id" in data
    assert isinstance(data["id"], int)


@pytest.mark.asyncio
async def test_get_books_empty(async_client):
    response = await async_client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_books_after_create(async_client):
    await async_client.post("/books/", json={
        "title": "Book 1", "author": "Author 1", "year": 2020, "genre": "drama"
    })
    response = await async_client.get("/books/")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 1
    assert books[0]["title"] == "Book 1"


@pytest.mark.asyncio
async def test_get_book_by_id(async_client):
    post_resp = await async_client.post("/books/", json={
        "title": "Book to Get", "author": "Author", "year": 2021, "genre": "sci-fi"
    })
    book_id = post_resp.json()["id"]
    response = await async_client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Book to Get"


@pytest.mark.asyncio
async def test_get_book_not_found(async_client):
    response = await async_client.get("/books/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_update_book(async_client):
    post_resp = await async_client.post("/books/", json={
        "title": "Old Title", "author": "Old Author", "year": 2019, "genre": "mystery"
    })
    book_id = post_resp.json()["id"]
    update_payload = {"title": "New Title", "year": 2022}
    response = await async_client.put(f"/books/{book_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["year"] == 2022
    # Проверяем, что остальные поля не изменились
    assert data["author"] == "Old Author"
    assert data["genre"] == "mystery"


@pytest.mark.asyncio
async def test_update_book_not_found(async_client):
    response = await async_client.put("/books/9999", json={"title": "No"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_book(async_client):
    post_resp = await async_client.post("/books/", json={
        "title": "To Delete", "author": "Someone", "year": 2018, "genre": "horror"
    })
    book_id = post_resp.json()["id"]
    del_resp = await async_client.delete(f"/books/{book_id}")
    assert del_resp.status_code == 204
    get_resp = await async_client.get(f"/books/{book_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_book_not_found(async_client):
    response = await async_client.delete("/books/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_filter_by_genre(async_client):
    await async_client.post("/books/", json={
        "title": "Fantasy Book", "author": "A", "year": 2020, "genre": "fantasy"
    })
    await async_client.post("/books/", json={
        "title": "Sci-Fi Book", "author": "B", "year": 2021, "genre": "sci-fi"
    })
    response = await async_client.get("/books/?genre=fantasy")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 1
    assert books[0]["genre"] == "fantasy"


@pytest.mark.asyncio
async def test_pagination(async_client):
    for i in range(5):
        await async_client.post("/books/", json={
            "title": f"Book {i}", "author": "Author", "year": 2020 + i, "genre": "test"
        })
    response = await async_client.get("/books/?limit=2&offset=0")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 2

    response2 = await async_client.get("/books/?limit=2&offset=2")
    assert response2.status_code == 200
    books2 = response2.json()
    assert len(books2) == 2

    # Проверяем, что записи разные
    assert books[0]["id"] != books2[0]["id"]
