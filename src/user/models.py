from typing import List, Optional

from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.post.models import Post


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False,
                                          unique=True)
    is_admin: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    posts: Mapped[List["Post"]] = relationship(back_populates="user", )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, " \
               f"password={self.password!r}, username={self.username!r}," \
               f"is_admin={self.is_admin!r}, is_active={self.is_active!r}"
