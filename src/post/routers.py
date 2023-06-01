from fastapi import APIRouter, Depends, HTTPException
from src.post.schemas import PostGet, PostCreate
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.post.crud import PostBL
from sqlalchemy.exc import IntegrityError
from logging import getLogger

logger = getLogger(__name__)

app = APIRouter()


@app.post('/', response_model=PostGet)
async def create_post(body: PostCreate, session: AsyncSession = Depends(get_db)):
    try:
        return await PostBL._create_post(body, session)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
