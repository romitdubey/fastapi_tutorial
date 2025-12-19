from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db


@asynccontextmanager
async def life_span(app:FastAPI):
    
    print(f"Server is starting...")
    await init_db()
    yield
    print(f"server is been stopped...")

version = "v1"

app = FastAPI(
    version = version,
    title="Book Management API",
    description="An API to manage a collection of books.",
    lifespan = life_span
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])