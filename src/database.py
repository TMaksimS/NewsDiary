from typing import AsyncGenerator

from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs

from src.config import DB_USER, DB_PORT, DB_PASS, DB_NAME, DB_HOST

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@" \
                          f"{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session_maker() as session:
            yield session
    finally:
        await session.close()
