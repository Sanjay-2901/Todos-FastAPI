from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session


from .auth import get_current_user
from models import Todos
from database import SessionLocal

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(current_user: user_dependency, db: db_dependency):
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Permission denied for the user")

    return db.query(Todos).all()


@router.delete("/todo/{todoId}", status_code=status.HTTP_200_OK)
async def delete_todo(current_user: user_dependency, db: db_dependency, todoId: int):
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Permission denied for the user")

    todo = db.query(Todos).filter(Todos.id == todoId).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()
