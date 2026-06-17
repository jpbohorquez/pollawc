from pydantic import BaseModel
from typing import List
from uuid import UUID

class LeaderboardEntry(BaseModel):
    user_id: UUID
    username: str
    full_name: str | None
    avatar_url: str | None
    total_points: int
    predictions_count: int
    exact_matches_count: int

class LeaderboardRead(BaseModel):
    group_id: UUID
    entries: List[LeaderboardEntry]
