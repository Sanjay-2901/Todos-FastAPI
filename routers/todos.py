from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session

from .auth import get_current_user
from models import Todos
from database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    priority: int = Field(gt=0, lt=5)
    description: str = Field(min_length=3, max_length=10)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(current_user: user_dependency, db: db_dependency):
    if current_user is None:
        raise HTTPException(status_code=401, status="User not Authenticated")
    return db.query(Todos).filter(Todos.owner_id == current_user.get("id")).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    current_user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    todo = (
        db.query(Todos)
        .filter((Todos.id == todo_id) & (Todos.owner_id == current_user.get("id")))
        .first()
    )
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def add_todo(
    current_user: user_dependency, db: db_dependency, todo_request: TodoRequest
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    todo_model = Todos(**todo_request.model_dump(), owner_id=current_user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(
    db: db_dependency,
    current_user: user_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")

    todo_model = (
        db.query(Todos)
        .filter((Todos.id == todo_id) & (Todos.owner_id == current_user.get("id")))
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    todo_model.owner_id = current_user.get("id")

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(
    current_user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")

    todo_model = (
        db.query(Todos)
        .filter((Todos.id == todo_id) & (Todos.owner_id == current_user.get("id")))
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo_model)
    db.commit()
