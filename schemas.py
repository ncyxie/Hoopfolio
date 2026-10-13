
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from models import TargetType, EntryStatus, Priority


# --------------------------------------------------
# WATCHLISTS - STEBĖJIMO SĄRAŠAI
# --------------------------------------------------


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

    # HATEOAS - nuorodos į sąrašą ir jo stebimus objektus
    @computed_field(alias="_links")
    @property
    def links(self) -> dict[str, str]:
        return {
            "self": f"/watchlists/{self.id}",
            "entries": f"/watchlists/{self.id}/entries"
        }


# --------------------------------------------------
# WATCHLIST ENTRIES - STEBIMI ŽAIDĖJAI IR KOMANDOS
# --------------------------------------------------


class WatchlistEntryCreate(BaseModel):
    target_type: TargetType
    target_name: str = Field(min_length=1, max_length=100)
    status: EntryStatus
    priority: Priority
    context: str | None = None


class WatchlistEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    watchlist_id: int
    target_type: TargetType
    target_name: str
    status: EntryStatus
    priority: Priority
    context: str | None

    # HATEOAS - nuorodos į objektą, jo sąrašą ir ataskaitas
    @computed_field(alias="_links")
    @property
    def links(self) -> dict[str, str]:
        entry_url = f"/watchlists/{self.watchlist_id}/entries/{self.id}"

        return {
            "self": entry_url,
            "watchlist": f"/watchlists/{self.watchlist_id}",
            "reports": f"{entry_url}/reports"
        }


# --------------------------------------------------
# SCOUTING REPORTS - SKAUTAVIMO ATASKAITOS
# --------------------------------------------------


class ScoutingReportCreate(BaseModel):
    scout_name: str = Field(min_length=1, max_length=100)
    observation_date: date

    strengths: str = Field(min_length=1)
    weaknesses: str = Field(min_length=1)
    insights: str = Field(min_length=1)
    conclusion: str = Field(min_length=1)
    statistics_note: str | None = None

    offense_rating: int = Field(ge=1, le=10)
    defense_rating: int = Field(ge=1, le=10)


class ScoutingReportResponse(ScoutingReportCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entry_id: int

    # Reikalingas HATEOAS adresams, bet JSON atskirai nerodomas
    watchlist_id: int = Field(exclude=True)

    # Bendras įvertinimas apskaičiuojamas, DB jo nesaugome
    @computed_field
    @property
    def overall_rating(self) -> float:
        return (self.offense_rating + self.defense_rating) / 2

    # HATEOAS - nuorodos į ataskaitą, objektą ir sąrašą
    @computed_field(alias="_links")
    @property
    def links(self) -> dict[str, str]:
        entry_url = f"/watchlists/{self.watchlist_id}/entries/{self.entry_id}"

        return {
            "self": f"{entry_url}/reports/{self.id}",
            "entry": entry_url,
            "watchlist": f"/watchlists/{self.watchlist_id}"
        }
