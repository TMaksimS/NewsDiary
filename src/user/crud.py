from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, and_

from src.user.schemas import UserGet, UserCreate
from src.user.models import User
from src.security import Hasher


class UserDB:
    """The DataBase logic, creating for Business logic"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, email: str, username: str,
                          password: str) -> User:
        new_user = User(email=email, username=username, password=password)
        self.session.add(new_user)
        await self.session.flush()
        return new_user

    async def delete_user(self, user_id: int) -> Union[int, None]:
        stmt = (update(User)
                .where(and_(User.id == user_id, User.is_active == True))
                .values(is_active=False)
                .returning(User.id))
        result = await self.session.execute(stmt)
        deleted_user_id_row = result.first()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def update_user(self, user_id: int) -> Union[int, None]:
        pass


class UserBL:
    """The business logic for routers, uses functions from UserDB"""

    @staticmethod
    async def create_user(body: UserCreate, session: AsyncSession) -> UserGet:
        async with session.begin():
            userdb = UserDB(session=session)
            user = await userdb.create_user(email=body.email,
                                            username=body.username,
                                            password=Hasher.get_hash_password(body.password))
            return UserGet(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                is_admin=user.is_admin,
            )

    @staticmethod
    async def delete_user():
        pass
