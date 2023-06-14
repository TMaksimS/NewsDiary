from sqlalchemy.ext.asyncio import AsyncSession

from src.post.models import Post
from src.post.schemas import PostGet, PostCreate


class PostDB:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(self, title: str, text: str, author_id: int) -> Post:
        new_post = Post(title=title, text=text, author_id=author_id)
        self.session.add(new_post)
        await self.session.flush()
        return new_post


class PostBL:
    @staticmethod
    async def _create_post(body: PostCreate,
                           session: AsyncSession) -> PostGet:
        async with session.begin():
            postdb = PostDB(session=session)
            post = await postdb.create_post(title=body.title, text=body.text,
                                            author_id=body.author_id)
            return PostGet(
                id=post.id,
                title=post.title,
                text=post.text,
                author_id=post.author_id
            )