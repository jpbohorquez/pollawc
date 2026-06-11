from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class UserGroupLink(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    group_id: UUID = Field(foreign_key="group.id", primary_key=True)
    role: str = Field(default="member")
    joined_at: datetime = Field(default_factory=datetime.utcnow)

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    predictions: List["Prediction"] = Relationship(back_populates="user")

class Group(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    invite_code: str = Field(unique=True, index=True)
    creator_id: UUID = Field(foreign_key="user.id")
    
    config: "GroupConfiguration" = Relationship(back_populates="group")
    predictions: List["Prediction"] = Relationship(back_populates="group")

class GroupConfiguration(SQLModel, table=True):
    group_id: UUID = Field(foreign_key="group.id", primary_key=True)
    
    pts_result_gr: int = Field(default=5)
    pts_result_ko: int = Field(default=10)
    pts_goals_gr: int = Field(default=2)
    pts_goals_ko: int = Field(default=4)
    pts_diff_gr: int = Field(default=1)
    pts_diff_ko: int = Field(default=2)
    
    group: Group = Relationship(back_populates="config")

class Match(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    team1: str
    team2: str
    group_name: Optional[str] = None
    stadium: Optional[str] = None
    start_at: datetime
    phase: str = Field(default="group") # group, knockout
    
    actual_goals1: Optional[int] = None
    actual_goals2: Optional[int] = None
    is_finished: bool = Field(default=False)
    
    predictions: List["Prediction"] = Relationship(back_populates="match")

class Prediction(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    match_id: UUID = Field(foreign_key="match.id")
    group_id: UUID = Field(foreign_key="group.id")
    
    predicted_goals1: int
    predicted_goals2: int
    points_earned: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="predictions")
    match: Match = Relationship(back_populates="predictions")
    group: Group = Relationship(back_populates="predictions")
