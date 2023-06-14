from pydantic import BaseModel


class Post(BaseModel):
    title: str
    text: str


class PostCreate(Post):
    author_id: int


class PostGet(Post):
    id: int
    author_id: int

    class Config:
        orm_mode = True
