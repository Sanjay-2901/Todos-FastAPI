from fastapi import FastAPI

import models
from routers import auth, todos
from database import engine

app = FastAPI()

app.include_router(auth.router)
app.include_router(todos.router)

models.Base.metadata.create_all(bind=engine)
