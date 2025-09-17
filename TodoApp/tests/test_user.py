from TodoApp.tests import conftest
from TodoApp.routers.user import get_db, get_current_user
from fastapi import status

conftest.app.dependency_overrides[get_db] = conftest.override_get_db
conftest.app.dependency_overrides[get_current_user] = conftest.override_get_current_user

def test_return_user(test_user):
    response = conftest.client.get("user")
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["username"] == "codingwithrobytest"
    assert user_data["email"] == "codingwithrobytest@email.com"
    assert user_data["first_name"] == "Eric"
    assert user_data["last_name"] == "Roby"
    assert user_data["phone_number"] == "(111)-111-1111"

def test_change_password_success(test_user):
    response = conftest.client.put("/user/password", json={"password": "testpassword", "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid_current_password(test_user):
    response = conftest.client.put("/user/password", json={"password": "wrongpassword", "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error on password change."}

def test_update_phone_number(test_user):
    response = conftest.client.put("/user/phone_number", json="2222222222")
    assert response.status_code == status.HTTP_204_NO_CONTENT

