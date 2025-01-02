from fastapi import FastAPI,APIRouter
from api.api import task_router
from auth.auth import router
app = FastAPI()

app.include_router(router, tags=["auth"])
app.include_router(task_router,tags=["tasks"])
