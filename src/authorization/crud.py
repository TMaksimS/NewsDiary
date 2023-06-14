from datetime import datetime, timedelta
from typing import Any
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from jose import jwt, JWSError
from redis import Redis

from src.user.models import User
from src.user.schemas import UserGet
from src.security import Hasher
from src.config import ALGORITHM, SECRET_KEY
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.authorization.schemas import TokenData
from src.redisdata import connect as redis_session


class AuthDB:
    """Class created for interaction methods of SQLDataBase"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.scalar(stmt)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "data": None,
                "details": "Incorrect Username"
            })


class AuthRedis:
    """Class created for interaction methods of RedisDataBase"""

    def __init__(self, session: Redis):
        self.database = redis_session

    def get_user_by_refresh_token(self, refresh_token: str) -> list[str | bytes | Any]:
        if self.database.get(refresh_token):
            return self.database.get(refresh_token)
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")

    def delete_refresh_token(self, refresh_token: str) -> None:
        self.database.delete(refresh_token)
        return None


class Token:
    """Class created for verify and make JWT strategy for access token
    and refresh token, initialization and refresh access token"""

    secret_key: str = SECRET_KEY
    algorithm: str = ALGORITHM
    live: int = ACCESS_TOKEN_EXPIRE_MINUTES

    @staticmethod
    def create_access_token(data: UserGet,
                            expires_delta: timedelta | None = None) -> str:
        to_encode = {
            "user_id": data.id,
            "username": data.username,
            "is_admin": data.is_admin,
        }
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, Token.secret_key, Token.algorithm)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: UserGet, head: datetime = datetime.now(),
                             database: Redis = redis_session) -> dict:
        refresh_token = {
            "head": str(Hasher.get_hash_password(str(head))),
            "body": UserGet(
                id=data.id,
                username=data.username,
                email=data.email,
                is_active=data.is_active,
                is_admin=data.is_admin,
            ).json()
        }
        database.set(name=refresh_token["head"],
                     value=refresh_token["body"],
                     ex=int(timedelta(days=7).total_seconds()))
        return refresh_token

    @staticmethod
    def decode_token(token: str) -> TokenData | None:
        result = jwt.decode(token=token, key=Token.secret_key,
                            algorithms=Token.algorithm)
        return TokenData(
            id=result.get("user_id"),
            username=result.get("username"),
            is_admin=result.get("is_admin"),
        )

    @staticmethod
    def create_token_by_refresh_token(refresh_token: str) \
            -> str | HTTPException:
        data = redis_session.get(refresh_token)
        if data:
            return Token.create_access_token(UserGet(**json.loads(data)))
        else:
            raise HTTPException(status_code=401, detail={
                "status": "error",
                "data": None,
                "detail": 'Unauthorized'
            })

    @staticmethod
    def verify_token(request: Request) \
            -> list:
        get_cookies = [request.cookies.get("access_token"),
                       request.cookies.get("refresh_token")]
        if get_cookies[0] is None:
            if get_cookies[1]:
                access_token = Token.create_token_by_refresh_token(
                    get_cookies[1])
                response = {"message": "New token has been created",
                            "access_token": access_token}
                return [access_token, response]
            else:
                raise HTTPException(status_code=401, detail={
                    "status": "Access denied",
                    "data": None,
                    "detail": 'Unauthorized'
                })
        else:
            try:
                Token.decode_token(get_cookies[0])

                return [get_cookies[0], None]
            except JWSError:
                raise HTTPException(status_code=401, detail={
                    "status": "Access denied",
                    "data": None,
                    "detail": "Invalid token",
                })

    @staticmethod
    def response(body_response: dict, body_token: dict) -> JSONResponse:

        """The method is used to help create
         the response handler and automatically set the cookie."""

        if body_token:
            body = {"token_response": body_token,
                    "body_response": body_response}
            response = JSONResponse(content=body, status_code=200)
            response.set_cookie("access_token",
                                body_token["access_token"],
                                max_age=1800)
            return response
        else:
            return JSONResponse(content=body_response, status_code=200)


class AuthBL:

    """Class created for interaction a FastAPI handlers"""

    @staticmethod
    async def verify_user_by_data(username: str, password: str,
                                  session: AsyncSession) -> UserGet | None:
        connect = AuthDB(session=session)
        data = await connect.get_user_by_username(username=username)
        if Hasher.verify_password(password, data.password):
            return UserGet(
                id=data.id,
                username=data.username,
                email=data.email,
                is_active=data.is_active,
                is_admin=data.is_admin,
            )
        else:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "data": None,
                "details": "Incorrect password"
            })

    @staticmethod
    async def delete_session(request: Request) -> JSONResponse:
        response = JSONResponse(content={
            "message": "Session has been delete",
            "data": None,
            "detail": "All cookies delete",
        })
        connect = AuthRedis(session=redis_session)
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token:
            connect.database.delete(refresh_token)
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response
