from sqlmodel import SQLModel
from datetime import datetime
from pydantic import BaseModel
from typing import Generic, TypeVar, List

class CampaignCreate(SQLModel):
    name: str | None = None
    due_date: datetime | None = None
    
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str  # Must be "access_token" for OAuth2
    token_type: str

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    data: T
    
    




