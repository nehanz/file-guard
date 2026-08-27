import pytest
from app.schemas.user import UserCreate
from pydantic import ValidationError

def test_user_password_validation():
    # Should fail due to missing uppercase
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", email="test@test.com", password="password1!")
        
    # Should fail due to missing special char
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", email="test@test.com", password="Password123")
        
    # Should pass
    user = UserCreate(username="testuser", email="test@test.com", password="Password123!")
    assert user.username == "testuser"
    
def test_user_wallet_validation():
    # Should fail due to invalid format
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", email="test@test.com", password="Password123!", wallet_address="invalid")
        
    # Should pass
    user = UserCreate(
        username="testuser", 
        email="test@test.com", 
        password="Password123!", 
        wallet_address="0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
    )
    assert user.wallet_address == "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
