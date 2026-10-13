
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from models import TargetType, EntryStatus, Priority


# --------------------------------------------------
# WATCHLISTS - STEBĖJIMO SĄRAŠAI
# --------------------------------------------------


# Duomenys, kuriuos klientas pateikia kurdamas arba atnaujindamas sąrašą
class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    purpose: str = Field(min_length=1)
    owner_name: str = Field(min_length=1, max_length=100)


# Duomenys, kuriuos API grąžina apie stebėjimo sąrašą
class WatchlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    purpose: str
    owner_name: str
    created_at: datetime


# --------------------------------------------------
# WATCHLIST ENTRIES - STEBIMI ŽAIDĖJAI IR KOMANDOS
# --------------------------------------------------


# Duomenys, kuriuos klientas pateikia apie stebimą objektą
class WatchlistEntryCreate(BaseModel):
    target_type: TargetType
    target_name: str = Field(min_length=1, max_length=100)
    status: EntryStatus
    priority: Priority
    context: str | None = None


# Duomenys, kuriuos API grąžina apie stebimą objektą
class WatchlistEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    watchlist_id: int
    target_type: TargetType
    target_name: str
    status: EntryStatus
    priority: Priority
    context: str | None


# --------------------------------------------------
# SCOUTING REPORTS - SKAUTAVIMO ATASKAITOS
# --------------------------------------------------


# Duomenys, kuriuos klientas pateikia kurdamas arba atnaujindamas ataskaitą
class ScoutingReportCreate(BaseModel):
    scout_name: str = Field(min_length=1, max_length=100)
    observation_date: date

    strengths: str = Field(min_length=1)
    weaknesses: str = Field(min_length=1)
    insights: str = Field(min_length=1)
    conclusion: str = Field(min_length=1)
    statistics_note: str | None = None

    # Puolimo ir gynybos įvertinimai turi būti nuo 1 iki 10
    offense_rating: int = Field(ge=1, le=10)
    defense_rating: int = Field(ge=1, le=10)


# Duomenys, kuriuos API grąžina apie skautavimo ataskaitą
class ScoutingReportResponse(ScoutingReportCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entry_id: int

    # Bendrą įvertinimą apskaičiuojame, todėl DB atskirai nesaugome
    @computed_field
    @property
    def overall_rating(self) -> float:
        return (self.offense_rating + self.defense_rating) / 2
