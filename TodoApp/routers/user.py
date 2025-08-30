from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Body
from models import Users
from schemas import UserVerifcation
from database import SessionLocal
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A type alias for dependency injection: Session provided by get_db()
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    return db.query(Users).filter(Users.id == user.get("user_id")).first()
    

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerifcation = Body(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    user_model = db.query(Users).filter(Users.id == user.get("user_id")).first()
    
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password): # type: ignore
        raise HTTPException(status_code=401, detail="Error on password change.")

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password) # type: ignore
    db.add(user_model)
    db.commit()
    
    