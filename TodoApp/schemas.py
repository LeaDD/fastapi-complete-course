from pydantic import BaseModel, Field

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class UserVerifcation(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str