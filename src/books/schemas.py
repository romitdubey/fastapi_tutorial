from pydantic import BaseModel
from datetime import datetime
import uuid

class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    languge: str
    created_at: datetime
    updated_at: datetime

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    languge: str


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    languge: str