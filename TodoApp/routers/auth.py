from fastapi import APIRouter, Body, Depends, HTTPException
from models import Users
from schemas import CreateUserRequest, Token
from passlib.context import CryptContext
from typing import Annotated, cast
from sqlalchemy.orm import Session
from database import SessionLocal
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime, timezone

load_dotenv()

secret_key = cast(str, os.getenv("SECRET_KEY"))
algorithm = cast(str, os.getenv("ALGORITHM"))

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


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

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, secret_key, algorithm=algorithm)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get('sub') # type: ignore
        user_id: int = payload.get("id") # type: ignore
        user_role: str = payload.get("role") # type: ignore
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user.")
        return {"username": username, "user_id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

@router.post("/", status_code=status.HTTP_201_CREATED)
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user.")
    token=create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}