from fastapi import FastAPI
from src.user.routers import app as user_router
from src.post.routers import app as post_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(user_router, prefix='/user', tags=['user'])
app.include_router(post_router, prefix='/post', tags=['post'])
#
# {
#   "email": "test1@g.com",
#   "username": "test1",
#   "password": "123"
# }