from fastapi import FastAPI

import models
from routers import admin, auth, todos, users
from database import engine

app = FastAPI()

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)


models.Base.metadata.create_all(bind=engine)
