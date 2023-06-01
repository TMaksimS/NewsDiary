from typing import AsyncGenerator, Generator
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs, async_sessionmaker
from src.config import DB_USER, DB_PORT, DB_PASS, DB_NAME, DB_HOST


SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass

#
# async def get_db() -> Generator:
#     try:
#         session: AsyncSession = async_session_maker()
#         yield session
#     finally:
#         await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session_maker() as session:
            yield session
    finally:
        await session.close()

# async def get_db() -> AsyncSession:
#     async with async_session_maker() as session:
#         yield session