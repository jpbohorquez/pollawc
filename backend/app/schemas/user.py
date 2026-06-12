from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_superuser: bool

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
