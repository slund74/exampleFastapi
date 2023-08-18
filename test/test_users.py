
from app import schemas
import pytest
from jose import JWTError, jwt
from app.config import settings




def test_create_user(client):
    res = client.post("/users/", json={"email": "hello@gmail.com", "password": "password123"})
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "hello@gmail.com"
    assert res.status_code == 201

def test_login_user(client, test_user):
    res = client.post("/login", json={"email": test_user['email'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id: str = payload.get("user_id")
    assert id == test_user['id']
    login_res.token_type =="bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 403),
    ('sanjeev@gmail.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, 'password123', 422),
    ('sanjeev@gmail.com', None, 422)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", json={"email": email, "password": password})

    assert res.status_code == status_code
    #assert res.json().get('detail') == 'Invalid Credentials'