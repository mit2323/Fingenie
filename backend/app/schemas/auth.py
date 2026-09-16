from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="User's full name",
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="User password",
    )


class LoginRequest(BaseModel):
    email: EmailStr

    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"