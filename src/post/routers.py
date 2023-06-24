from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from logging import getLogger
from fastapi.encoders import jsonable_encoder

from src.post.schemas import PostGet, PostCreate, Post
from src.database import get_db
from src.post.crud import PostBL
from src.authorization.crud import Token

logger = getLogger(__name__)

app = APIRouter()


@app.post("", response_model=PostGet)
async def create_post(request: Request,
                      body: Post,
                      session: AsyncSession = Depends(get_db)):
    user = Token.verify_token(request=request)
    user_data = Token.decode_token(user[0])
    result = await PostBL.create_post(body=body,
                                      author_id=user_data.id,
                                      session=session)
    return Token.response(body_response=jsonable_encoder(result),
                          body_token=user[1])


@app.get("")
async def get_all_posts(request: Request,
                        session: AsyncSession = Depends(get_db)):
    user = Token.verify_token(request=request)
    user_data = Token.decode_token(user[0])
    data = await PostBL.get_all_posts(session=session,
                                      user_id=user_data.id,
                                      is_admin=user_data.is_admin)
    return Token.response(body_response=jsonable_encoder(data),
                          body_token=user[1])


@app.get("/{task_id}")
async def get_current_post(task_id: int, request: Request,
                           session: AsyncSession = Depends(get_db)):
    user = Token.verify_token(request=request)
    user_data = Token.decode_token(user[0])
    data = await PostBL.get_post(post_id=task_id, session=session,
                                 user_id=user_data.id,
                                 is_admin=user_data.is_admin)
    return Token.response(body_response=jsonable_encoder(data),
                          body_token=user[1])


@app.put("/{task_id}", response_model=PostCreate)
async def edit_post(request: Request, task_id: int,
                    body: Post,
                    session: AsyncSession = Depends(get_db)):
    user = Token.verify_token(request=request)
    user_data = Token.decode_token(user[0])
    result = await PostBL.edit_post(post_id=task_id,
                                    user_id=user_data.id,
                                    is_admin=user_data.is_admin,
                                    body=body,
                                    session=session)
    return Token.response(body_response=jsonable_encoder(result),
                          body_token=user[1])


@app.delete("/{task_id}")
async def delete_post(request: Request, task_id: int,
                      session: AsyncSession = Depends(get_db)):
    user = Token.verify_token(request=request)
    user_data = Token.decode_token(user[0])
    result = await PostBL.delete_post(post_id=task_id,
                                      user_id=user_data.id,
                                      is_admin=user_data.is_admin,
                                      session=session)
    return Token.response(body_response=jsonable_encoder(result),
                          body_token=user[1])


