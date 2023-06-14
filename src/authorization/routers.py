from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from logging import getLogger

from src.database import get_db
from src.authorization.crud import AuthBL
from src.authorization.crud import Token
from src.user.schemas import UserGet, UserCreate
from src.user.crud import UserBL

app = APIRouter()

logger = getLogger(__name__)


@app.post('/login')
async def login(password: str, username: str,
                session: AsyncSession = Depends(get_db)):
    result = await AuthBL.verify_user_by_data(password=password,
                                              username=username,
                                              session=session)
    if result:
        access_token = Token.create_access_token(result)
        refresh_token = Token.create_refresh_token(result)
        response = JSONResponse(content={
            "data": jsonable_encoder(result),
            "access_token": access_token,
            "refresh_token": refresh_token["head"]
        }, status_code=200)

        response.set_cookie(key="access_token",
                            value=access_token,
                            max_age=1800)
        response.set_cookie(key="refresh_token",
                            value=refresh_token["head"],
                            max_age=int(timedelta(days=7).total_seconds()),
                            )
        return response
    else:
        return HTTPException(status_code=401, detail={
            "status": "error",
            "data": None,
            "detail": 'Unauthorized'
        })


@app.post("/logout")
async def logout(request: Request):
    return await AuthBL.delete_session(request)


@app.post("/register", response_model=UserGet)
async def create_user(body: UserCreate,
                      session: AsyncSession = Depends(get_db)) -> UserGet:
    try:
        return await UserBL.create_user(body, session)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")

