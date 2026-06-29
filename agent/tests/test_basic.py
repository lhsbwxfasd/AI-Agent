import pytest
from app.models.user import User, UserCreate, UserLogin
from app.services.auth_service import auth_service


def test_user_model():
    user_data = {
        "id": 1,
        "username": "test",
        "email": "test@example.com",
        "hashed_password": "hashed123",
        "preferred_model": "deepseek-chat"
    }
    user = User(**user_data)
    assert user.username == "test"
    assert user.preferred_model == "deepseek-chat"


def test_password_hashing():
    password = "test123"
    hashed = auth_service.get_password_hash(password)
    assert auth_service.verify_password(password, hashed)
    assert not auth_service.verify_password("wrong", hashed)


def test_default_user():
    user = auth_service.get_user("admin")
    assert user is not None
    assert user.username == "admin"
    assert user.preferred_model == "deepseek-chat"


def test_authenticate_user():
    user = auth_service.authenticate_user("admin", "admin123")
    assert user is not None
    assert user.username == "admin"
    
    wrong_user = auth_service.authenticate_user("admin", "wrongpassword")
    assert wrong_user is None


def test_token_creation():
    token = auth_service.create_access_token(data={"sub": "admin"})
    assert token is not None
    
    token_data = auth_service.verify_token(token)
    assert token_data is not None
    assert token_data.username == "admin"


def test_default_model():
    model = auth_service.get_user_preferred_model("admin")
    assert model == "deepseek-chat"
    
    model = auth_service.get_user_preferred_model("nonexistent")
    assert model == "deepseek-chat"
