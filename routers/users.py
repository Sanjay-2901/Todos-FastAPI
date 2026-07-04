from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from models import Users
from routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/details")
async def get_user_details(current_user: user_dependency, db: db_dependency):
    user = db.query(Users).filter(Users.id == current_user.get("id")).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "name": user.first_name + " " + user.last_name,
        "email": user.email,
        "role": user.role,
    }


@router.patch("/change_password", status_code=status.HTTP_200_OK)
async def change_password(
    db: db_dependency,
    current_user: Annotated[dict, Depends(get_current_user)],
    change_password_request: ChangePasswordRequest,
):
    user_details = db.query(Users).filter(Users.id == current_user.get("id")).first()

    if user_details is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt_context.verify(
        change_password_request.current_password, user_details.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Invalid current password")

    if bcrypt_context.verify(
        change_password_request.new_password, user_details.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password and new password cannot be the same",
        )

    user_details.hashed_password = bcrypt_context.hash(
        change_password_request.new_password
    )

    db.add(user_details)
    db.commit()
