from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from logging import getLogger

from src.post.schemas import PostGet, PostCreate
from src.database import get_db
from src.post.crud import PostBL

logger = getLogger(__name__)

app = APIRouter()


@app.post('/', response_model=PostGet)
async def create_post(body: PostCreate, session: AsyncSession = Depends(get_db)):
    try:
        return await PostBL._create_post(body, session)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
