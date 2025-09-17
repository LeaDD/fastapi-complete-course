from TodoApp.routers.admin import get_db, get_current_user
from TodoApp.tests import conftest
from TodoApp.models import Todos
from fastapi import status

conftest.app.dependency_overrides[get_db] = conftest.override_get_db
conftest.app.dependency_overrides[get_current_user] = conftest.override_get_current_user

def test_admin_read_all_authenticated(test_todo):
    response = conftest.client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    # assert response.json() == [{"complete": False, "title": "Learn to code", "description": "Need to learn everyday", "priority": 5, "owner_id": 1}]

def test_admin_delete_todo(test_todo):
    response = conftest.client.delete("/admin/todo/1")
    assert response.status_code == 204

    db = conftest.TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_admin_delete_todo_not_found():
    response = conftest.client.delete("/admin/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

