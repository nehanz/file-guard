from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Request
from app.core.exceptions import ValidationException, NotFoundException, AppException
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.models.token import RefreshToken
from app.repositories.user import UserRepository
from app.repositories.token import RefreshTokenRepository
from app.schemas.user import UserCreate, UserLogin, ChangePassword, Token


class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def register_user(self, user_in: UserCreate) -> User:
        # Check if username or email already exists
        if await self.user_repo.get_by_email(user_in.email):
            raise ValidationException("Email already registered")
        if await self.user_repo.get_by_username(user_in.username):
            raise ValidationException("Username already taken")

        # Create user
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password
        
        user_model = User(**user_data)
        return await self.user_repo.create(user_model)

    async def authenticate_user(self, login_data: UserLogin, request: Request) -> Token:
        # Login supports username or email
        user = await self.user_repo.get_by_email(login_data.username)
        if not user:
            user = await self.user_repo.get_by_username(login_data.username)
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise AppException("Incorrect email or password", status_code=401)
        
        if not user.is_active:
            raise AppException("Inactive user", status_code=400)

        # Generate tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        
        # Save refresh token to DB
        from app.core.config import settings
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        client_ip = request.client.host if request.client else ""
        user_agent = request.headers.get("user-agent", "")
        
        await self.token_repo.create(RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            ip_address=client_ip,
            user_agent=user_agent
        ))

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def logout(self, user_id: str) -> None:
        await self.token_repo.revoke_all_for_user(user_id)

    async def refresh_token(self, refresh_token: str) -> Token:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AppException("Invalid token type", status_code=401)
        except ValueError as e:
            raise AppException(str(e), status_code=401)
            
        token_record = await self.token_repo.get_by_token(refresh_token)
        if not token_record or token_record.is_revoked:
            raise AppException("Token is revoked or invalid", status_code=401)
            
        if token_record.expires_at < datetime.now(timezone.utc):
            raise AppException("Token has expired", status_code=401)

        user_id = payload.get("sub")
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active:
            raise AppException("User not found or inactive", status_code=401)
            
        # Revoke the old refresh token
        await self.token_repo.update(token_record.id, {"is_revoked": True})
        
        # Create new tokens
        new_access_token = create_access_token(subject=user_id)
        new_refresh_token = create_refresh_token(subject=user_id)
        
        from app.core.config import settings
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        await self.token_repo.create(RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=expires_at,
            ip_address=token_record.ip_address,
            user_agent=token_record.user_agent
        ))
        
        return Token(access_token=new_access_token, refresh_token=new_refresh_token)

    async def change_password(self, user_id: str, password_data: ChangePassword) -> None:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")
            
        if not verify_password(password_data.current_password, user.hashed_password):
            raise AppException("Incorrect current password", status_code=400)
            
        hashed_password = get_password_hash(password_data.new_password)
        await self.user_repo.update(user.id, {"hashed_password": hashed_password})
        
        # Revoke all refresh tokens on password change
        await self.token_repo.revoke_all_for_user(user.id)
