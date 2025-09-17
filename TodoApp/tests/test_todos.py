
from TodoApp.routers.todos import get_current_user, get_db
from fastapi import status
from TodoApp.models import Todos
from TodoApp.tests import conftest

conftest.app.dependency_overrides[get_db] = conftest.override_get_db
conftest.app.dependency_overrides[get_current_user] = conftest.override_get_current_user

def test_read_all_authenticated(test_todo):
    response = conftest.client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    todo = data[0]
    print(todo)
    assert todo["title"] == "Learn to code"
    assert todo["description"] == "Need to learn everyday"
    assert todo["priority"] == 5
    assert todo["complete"] is False
    assert todo["owner_id"] == 1
    assert todo["id"] == 1

def test_read_one_authenticated(test_todo):
    response = conftest.client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    
    todo = response.json()
    assert todo["title"] == "Learn to code"
    assert todo["description"] == "Need to learn everyday"
    assert todo["priority"] == 5
    assert todo["complete"] is False
    assert todo["owner_id"] == 1

def test_read_one_authenticated_not_found():
    response = conftest.client.get("/todos/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found."}

def test_create_todo(test_todo):
    request_data = {
        "title": "New Todo!",
        "description": "New todo description",
        "priority": 5,
        "complete": False
    }

    response = conftest.client.post("/todos/todo/", json=request_data)
    assert response.status_code == 201

    db = conftest.TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model is not None, "Todo with id=2 was not found in the database"
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.complete == request_data.get("complete")

def test_update_todo(test_todo):
    request_data = {
        "title": "Change the title of the Todo!",
        "description": "Need to learn everyday",
        "priority": 5,
        "complete": False
    }

    response = conftest.client.put("/todos/todo/1", json=request_data)
    assert response.status_code == 204

    db = conftest.TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is not None, "Todo with id=1 was not found in the database after update"
    assert model.title == "Change the title of the Todo!"

def test_update_todo_not_found(test_todo):
    request_data = {
        "title": "Change the title of the Todo!",
        "description": "Need to learn everyday",
        "priority": 5,
        "complete": False
    }

    response = conftest.client.put("/todos/todo/999", json=request_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

def test_delete_todo(test_todo):
    response = conftest.client.delete("/todos/todo/1")
    assert response.status_code == 204

    db = conftest.TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_todo_not_found():
    response = conftest.client.delete("/todos/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


# Run with pytest -s TodoApp/tests/test_todos.py to check all registered routes
def test_debug_paths():
    oas = conftest.client.get("/openapi.json").json()
    print(sorted((p, list(ops.keys())) for p, ops in oas["paths"].items()))
    assert oas  # forces pytest to show the print

