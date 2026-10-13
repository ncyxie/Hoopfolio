from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    purpose: str = Field(min_length=1)
    owner_name: str = Field(min_length=1, max_length=100)


class WatchlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    purpose: str
    owner_name: str
    created_at: datetime