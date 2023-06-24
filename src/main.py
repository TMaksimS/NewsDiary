from fastapi import FastAPI

from src.user.routers import app as user_router
from src.post.routers import app as post_router
from src.authorization.routers import app as auth_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(user_router, prefix='/user', tags=['user'])
app.include_router(post_router, prefix='/tasks', tags=['task'])
app.include_router(auth_router, prefix='/auth', tags=['auth'])