from jose import jwt, JWTError
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
from passlib.context import (
    CryptContext,
)  # pip install passlib | pip install bycrypt==4.0.1
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from models import Users
from database import SessionLocal

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "HelloWorld"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


class CreateUserRequest(BaseModel):
    role: str
    email: str
    password: str
    user_name: str = Field(min_length=3, max_length=10)
    last_name: str = Field(min_length=3, max_length=10)
    first_name: str = Field(min_length=3, max_length=10)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(user_name: str, password: str, db: db_dependency):
    user = db.query(Users).filter(user_name == Users.username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": username, "id": user_id, "role": role, "exp": expires}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        return {"username": username, "id": user_id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        role=create_user_request.role,
        email=create_user_request.email,
        username=create_user_request.user_name,
        is_active=True,
        last_name=create_user_request.last_name,
        first_name=create_user_request.first_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )

    db.add(create_user_model)
    db.commit()


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user",
        )

    token = create_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(minutes=20),
    )
    return {"access_token": token, "token_type": "bearer"}
