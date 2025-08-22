from fastapi import Body, FastAPI, Path, Query, HTTPException
from book import Book
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=20000101, lt=20300101)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A description of a book",
                "rating": 5,
                "published_date": 2029
            }
        }
    }

BOOKS = [
    Book(1, "Computer Science Pro", "codingwithroby", "A very nice book", 5, 20250101),
    Book(2, "Be fast with FastAPI", "codingwithroby", "A great book", 5, 20240101),
    Book(3, "Master endpoints", "codingwithroby", "An awesome book", 5, 20230101),
    Book(4, "HP1", "Author 1", "Book description", 4, 20220101),
    Book(5, "HP2", "Author 2", "Book description", 3, 20210101),
    Book(6, "HP3", "Author 3", "Book description", 2, 20200101)
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found.")
   
@app.get("/books/by-date/", status_code=status.HTTP_200_OK)
async def books_by_date(published_date: int = Query(gt=20000101, lt=20300101)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)

    return books_to_return
        
@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    
    return books_to_return

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1    

    return book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = Book(**book.model_dump())
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found.")

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_deleted = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_deleted = True
            break
    if not book_deleted:
        raise HTTPException(status_code=404, detail="Item not found.")