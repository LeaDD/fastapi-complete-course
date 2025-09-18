from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from TodoApp.database import Base
from TodoApp.main import app
from TodoApp.models import Todos, Users
import pytest
from TodoApp.routers.auth import bcrypt_context
from jose import jwt
from datetime import timedelta, datetime, timezone
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass = StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "codingwithrobytest", "user_id": 1, "user_role": "admin"}

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    user = Users(
        username="codingwithrobytest",
        email="codingwithrobytest@email.com",
        first_name="Eric",
        last_name="Roby",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        phone_number="(111)-111-1111"
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()

@pytest.fixture
def auth_headers(test_user):
    """Generate authentication headers for test user"""
    secret_key = os.getenv("SECRET_KEY", "test-secret-key")
    algorithm = os.getenv("ALGORITHM", "HS256")
    
    token = jwt.encode(
        {"sub": test_user.username, "id": test_user.id, "role": test_user.role, "exp": (datetime.now(timezone.utc) + timedelta(minutes=20))},
        secret_key,
        algorithm=algorithm
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_new(test_user_new):
    """Generate authentication headers for new test user"""
    secret_key = os.getenv("SECRET_KEY", "test-secret-key")
    algorithm = os.getenv("ALGORITHM", "HS256")
    
    token = jwt.encode(
        {"sub": test_user_new.username, "id": test_user_new.id, "role": test_user_new.role, "exp": (datetime.now(timezone.utc) + timedelta(minutes=20))},
        secret_key,
        algorithm=algorithm
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_user_new():
    """Create a new test user for authentication (different from existing test_user)"""
    db = TestingSessionLocal()
    try:
        # Clean up any existing test user and their todos first
        existing_user = db.query(Users).filter(Users.username == "testuser").first()
        if existing_user:
            # Delete todos first due to foreign key constraint
            db.query(Todos).filter(Todos.owner_id == existing_user.id).delete()
            db.query(Users).filter(Users.username == "testuser").delete()
            db.commit()
        
        # Create new test user
        test_user = Users(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            hashed_password=bcrypt_context.hash("testpassword"),
            is_active=True,
            role="user"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        return test_user
    finally:
        db.close()

@pytest.fixture
def test_todo_new(test_user_new):
    """Create a test todo for the new test user"""
    db = TestingSessionLocal()
    try:
        # Clean up any existing test todos
        db.query(Todos).filter(Todos.owner_id == test_user_new.id).delete()
        db.commit()
        
        # Create new test todo
        test_todo = Todos(
            title="Test Todo",
            description="Test Description",
            priority=1,
            complete=False,
            owner_id=test_user_new.id
        )
        db.add(test_todo)
        db.commit()
        db.refresh(test_todo)
        return test_todo
    finally:
        db.close()