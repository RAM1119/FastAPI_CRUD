from sqlmodel import SQLModel, Field
from datetime import datetime

class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(), index=True)
    
class User(SQLModel, table = True):
    user_id : int | None = Field(default = None, primary_key = True)
    username : str = Field(unique = True, index = True)
    password : str = Field(default=None)