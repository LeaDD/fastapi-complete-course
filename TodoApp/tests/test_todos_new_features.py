import pytest
from fastapi.testclient import TestClient
from TodoApp.main import app
from TodoApp.database import SessionLocal
from TodoApp.models import Users, Todos
from TodoApp.routers.todos import get_current_user, get_db
from TodoApp.tests import conftest

# Override dependencies to use test database
conftest.app.dependency_overrides[get_db] = conftest.override_get_db
conftest.app.dependency_overrides[get_current_user] = conftest.override_get_current_user

client = TestClient(app)

def test_toggle_todo_completion_success(test_todo):
    """Test successfully toggling a todo's completion status"""
    # Initially false
    response = client.patch(f"/todos/todo/{test_todo.id}/toggle")
    assert response.status_code == 200
    data = response.json()
    assert data["complete"] == True
    assert data["id"] == test_todo.id
    assert "successfully" in data["message"]
    
    # Toggle again to true
    response = client.patch(f"/todos/todo/{test_todo.id}/toggle")
    assert response.status_code == 200
    data = response.json()
    assert data["complete"] == False

def test_toggle_todo_completion_not_found():
    """Test toggling a non-existent todo"""
    response = client.patch("/todos/todo/999/toggle")
    assert response.status_code == 404

def test_get_todo_stats_success(test_user):
    """Test getting todo statistics"""
    # Override the mocked user to use the actual test user's ID
    def override_get_current_user_with_test_user():
        return {"username": test_user.username, "user_id": test_user.id, "user_role": test_user.role}
    
    conftest.app.dependency_overrides[get_current_user] = override_get_current_user_with_test_user
    
    db = conftest.TestingSessionLocal()
    try:
        # Create multiple test todos
        todos_data = [
            {"title": "Todo 1", "description": "Desc 1", "priority": 1, "complete": True, "owner_id": test_user.id},
            {"title": "Todo 2", "description": "Desc 2", "priority": 2, "complete": False, "owner_id": test_user.id},
            {"title": "Todo 3", "description": "Desc 3", "priority": 3, "complete": True, "owner_id": test_user.id},
        ]
        
        for todo_data in todos_data:
            todo = Todos(**todo_data)
            db.add(todo)
        db.commit()
        
        response = client.get("/todos/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_todos"] == 3
        assert data["completed_todos"] == 2
        assert data["pending_todos"] == 1
        assert data["completion_rate"] == 66.67
    finally:
        db.close()
        # Reset to original override
        conftest.app.dependency_overrides[get_current_user] = conftest.override_get_current_user

def test_get_todo_stats_empty(test_user):
    """Test getting stats when user has no todos"""
    # Override the mocked user to use the actual test user's ID
    def override_get_current_user_with_test_user():
        return {"username": test_user.username, "user_id": test_user.id, "user_role": test_user.role}
    
    conftest.app.dependency_overrides[get_current_user] = override_get_current_user_with_test_user
    
    db = conftest.TestingSessionLocal()
    try:
        # Clean up all todos for test user
        db.query(Todos).filter(Todos.owner_id == test_user.id).delete()
        db.commit()
        
        response = client.get("/todos/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_todos"] == 0
        assert data["completed_todos"] == 0
        assert data["pending_todos"] == 0
        assert data["completion_rate"] == 0
    finally:
        db.close()
        # Reset to original override
        conftest.app.dependency_overrides[get_current_user] = conftest.override_get_current_user

