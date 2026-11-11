# backend/app/auth/schemas.py
"""Pydantic models for authentication and user data.
These models are used in request/response bodies.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    student = "student"
    staff = "staff"
    admin = "admin"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None
    role: Role = Role.student


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[Role] = None
