from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class GroupCreate(BaseModel):
    name: str

class GroupRead(BaseModel):
    id: UUID
    name: str
    invite_code: str
    creator_id: UUID

class GroupJoin(BaseModel):
    invite_code: str

class GroupConfigurationRead(BaseModel):
    group_id: UUID
    pts_result_gr: int
    pts_result_ko: int
    pts_goals_gr: int
    pts_goals_ko: int
    pts_diff_gr: int
    pts_diff_ko: int

class GroupConfigurationUpdate(BaseModel):
    pts_result_gr: Optional[int] = None
    pts_result_ko: Optional[int] = None
    pts_goals_gr: Optional[int] = None
    pts_goals_ko: Optional[int] = None
    pts_diff_gr: Optional[int] = None
    pts_diff_ko: Optional[int] = None
