from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from fastapi import HTTPException, status
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(
        self,
        request: RegisterRequest,
    ):
        # Check if email already exists
        existing_user = await self.repository.get_by_email(
            request.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )

        # Create user object
        user = User(
            full_name=request.full_name,
            email=request.email,
            password_hash=hash_password(request.password),
        )

        return await self.repository.create(user)

    async def login(
        self,
        request: LoginRequest,
    ):
        user = await self.repository.get_by_email(
            request.email
        )

        if not user:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            )

        if not verify_password(
            request.password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password.")

        access_token = create_access_token(
            {
                "sub": str(user.id)
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }