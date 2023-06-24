from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.post.models import Post
from src.post.schemas import PostGet, PostCreate
from src.post.schemas import Post as PostSchema


class PostDB:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(self, title: str, text: str,
                          author_id: int) -> Post:
        new_post = Post(title=title, text=text, author_id=author_id)
        self.session.add(new_post)
        await self.session.flush()
        return new_post

    async def get_all_post(self):
        stmt = select(Post)
        return await self.session.scalars(stmt)

    async def get_current_post(self, id: int):
        stmt = select(Post).where(Post.id == id)
        return await self.session.scalar(stmt)

    async def edit_post(self, body: PostCreate, post_id: int):
        stmt = (update(Post).
                where(Post.id == post_id).
                values(body.dict(exclude_unset=True)).
                returning(Post))
        return await self.session.execute(stmt)

    async def delete_post(self, post_id: int):
        stmt = delete(Post).where(Post.id == post_id)
        return await self.session.execute(stmt)


class PostBL:
    @staticmethod
    async def create_post(body: Post,
                          author_id: int,
                          session: AsyncSession) -> PostGet:
        async with session.begin():
            connect = PostDB(session=session)
            post = await connect.create_post(title=body.title,
                                             text=body.text,
                                             author_id=author_id)
            return PostGet(
                id=post.id,
                title=post.title,
                text=post.text,
                author_id=post.author_id,
                can_edit=True
            )

    @staticmethod
    async def get_post(post_id: int, session: AsyncSession,
                       user_id: int, is_admin: bool) -> PostGet:
        async with session.begin():
            connect = PostDB(session=session)
            result = await connect.get_current_post(id=post_id)
            if result:
                if user_id == result.author_id or is_admin is True:
                    return PostGet(
                        id=result.id,
                        title=result.title,
                        text=result.text,
                        author_id=result.author_id,
                        can_edit=True
                    )
                else:
                    return PostGet(
                        id=result.id,
                        title=result.title,
                        text=result.text,
                        author_id=result.author_id,
                        can_edit=False
                    )
            else:
                raise HTTPException(status_code=400, detail={
                    "status": "Incorrect request",
                    "data": None,
                    "detail": 'does not exist'
                })

    @staticmethod
    async def get_all_posts(user_id: int, is_admin: bool,
                            session: AsyncSession) -> list[PostGet]:
        async with session.begin():
            connect = PostDB(session=session)
            data = await connect.get_all_post()
            result = []
            if data:
                for post in data:
                    if user_id == post.author_id or is_admin is True:
                        result.append(PostGet(
                            id=post.id,
                            title=post.title,
                            text=post.text,
                            author_id=post.author_id,
                            can_edit=True
                        ))
                    else:
                        result.append(PostGet(
                            id=post.id,
                            title=post.title,
                            text=post.text,
                            author_id=post.author_id,
                            can_edit=False
                        ))
                return result
            else:
                raise HTTPException(status_code=503, detail={
                    "status": "Service Unavailable",
                    "detail": "Try again later"
                })

    @staticmethod
    async def edit_post(post_id: int, user_id: int, is_admin: bool,
                        body: PostSchema,
                        session: AsyncSession) -> PostGet:
        async with session.begin():
            connect = PostDB(session=session)
            data = await connect.get_current_post(id=post_id)
            if data:
                if data.author_id == user_id or is_admin is True:
                    new_data = PostCreate(
                        title=body.title,
                        text=body.text,
                        author_id=data.author_id,
                    )
                    await connect.edit_post(body=new_data,
                                            post_id=post_id)
                    result = await connect.get_current_post(id=post_id)
                    return PostGet(
                        id=result.id,
                        title=result.title,
                        text=result.text,
                        author_id=result.author_id,
                        can_edit=True
                    )
                else:
                    raise HTTPException(status_code=403, detail={
                        "status": "Access denied",
                        "data": None,
                        "detail": "Forbidden"
                    })
            else:
                raise HTTPException(status_code=400, detail={
                    "status": "Incorrect request",
                    "data": None,
                    "detail": 'does not exist'
                })

    @staticmethod
    async def delete_post(post_id: int, user_id: int,
                          is_admin: bool, session: AsyncSession) -> dict:
        async with session.begin():
            connect = PostDB(session=session)
            post_data = await connect.get_current_post(id=post_id)
            if post_data:
                if post_data.author_id == user_id or is_admin is True:
                    result = await connect.delete_post(post_id=post_id)
                    return {"status": "Access done",
                            "data": PostGet(
                                id=post_data.id,
                                title=post_data.title,
                                text=post_data.text,
                                author_id=post_data.author_id,
                                can_edit=True,
                            ),
                            "detail": result}
                else:
                    raise HTTPException(status_code=403, detail={
                        "status": "Access denied",
                        "data": None,
                        "detail": "Forbidden"
                    })
            else:
                raise HTTPException(status_code=400, detail={
                    "status": "Incorrect request",
                    "data": None,
                    "detail": 'does not exist'
                })
