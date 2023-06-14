from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from logging import getLogger

from src.user.schemas import UserCreate, UserGet
from src.user.crud import UserBL
from src.database import get_db


logger = getLogger(__name__)

app = APIRouter()


@app.post("/", response_model=UserGet)
async def create_user(body: UserCreate,
                      session: AsyncSession = Depends(get_db)) -> UserGet:
    try:
        return await UserBL.create_user(body, session)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
