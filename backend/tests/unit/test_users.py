import pytest
from app.schemas.user import UserUpdate, UserAdminUpdate
from pydantic import ValidationError

def test_user_update_validation():
    # Should fail due to invalid wallet format
    with pytest.raises(ValidationError):
        UserUpdate(wallet_address="invalid_wallet")
        
    # Should pass
    user_update = UserUpdate(wallet_address="0x71C7656EC7ab88b098defB751B7401B5f6d8976F")
    assert user_update.wallet_address == "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
    
def test_admin_user_update_validation():
    # Admin can change active status and role
    update = UserAdminUpdate(
        username="newname",
        is_active=False,
        role="admin"
    )
    assert update.username == "newname"
    assert update.is_active is False
    assert update.role == "admin"
