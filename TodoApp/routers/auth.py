from fastapi import APIRouter, Body, Depends
from models import Users
from schemas import CreateUserRequest
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from starlette import status

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

