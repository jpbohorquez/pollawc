from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class MatchRead(BaseModel):
    id: UUID
    team1: str
    team2: str
    group_name: Optional[str] = None
    stadium: Optional[str] = None
    start_at: datetime
    phase: str
    actual_goals1: Optional[int] = None
    actual_goals2: Optional[int] = None
    is_finished: bool
    is_locked: bool
