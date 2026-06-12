from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MatchUpdateResult(BaseModel):
    actual_goals1: int
    actual_goals2: int
    is_finished: bool = True

class MatchCreateAdmin(BaseModel):
    team1: str
    team2: str
    group_name: Optional[str] = None
    stadium: Optional[str] = None
    start_at: datetime
    phase: str = "knockout" # Por defecto para nuevos partidos de admin
