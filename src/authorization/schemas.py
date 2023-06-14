from pydantic import BaseModel


class TokenData(BaseModel):
    id: int
    username: str
    is_admin: bool
