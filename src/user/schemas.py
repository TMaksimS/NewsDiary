from pydantic import BaseModel
from src.post.schemas import PostGet


class User(BaseModel):
    email: str
    username: str


class UserCreate(User):
    password: str


class UserGet(User):
    id: int
    is_admin: bool
    is_active: bool
    # posts: list[PostGet] = []

    class Config:
        orm_mode = True
