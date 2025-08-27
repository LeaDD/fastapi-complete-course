from fastapi import APIRouter, Body, Depends
from models import Users
from schemas import CreateUserRequest, Token
from passlib.context import CryptContext
from typing import Annotated, cast
from sqlalchemy.orm import Session
from database import SessionLocal
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime, timezone

load_dotenv()

secret_key = cast(str, os.getenv("SECRET_KEY"))
algorithm = cast(str, os.getenv("ALGORITHM"))

router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A type alias for dependency injection: Session provided by get_db()
db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, secret_key, algorithm=algorithm)

@router.post("/auth/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest = Body(...)):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role = create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )

    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency
                                 ):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return 'Failed authentication'
    token=create_access_token(user.username, user.id, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}