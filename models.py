from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, CheckConstraint, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TargetType(str, Enum):
    player = "player"
    team = "team"


class EntryStatus(str, Enum):
    new = "new"
    watching = "watching"
    closed = "closed"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    purpose = Column(Text, nullable=False)
    owner_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"

    id = Column(Integer, primary_key=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False)
    target_type = Column(SqlEnum(TargetType, name="target_type_enum"), nullable=False)
    target_name = Column(String(100), nullable=False)
    status = Column(SqlEnum(EntryStatus, name="entry_status_enum"), nullable=False)
    priority = Column(SqlEnum(Priority, name="priority_enum"), nullable=False)
    context = Column(Text, nullable=True)


class ScoutingReport(Base):
    __tablename__ = "scouting_reports"

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("watchlist_entries.id"), nullable=False)

    scout_name = Column(String(100), nullable=False)
    observation_date = Column(Date, nullable=False)

    strengths = Column(Text, nullable=False)
    weaknesses = Column(Text, nullable=False)
    insights = Column(Text, nullable=False)
    conclusion = Column(Text, nullable=False)
    statistics_note = Column(Text, nullable=True)

    offense_rating = Column(Integer, nullable=False)
    defense_rating = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("offense_rating BETWEEN 1 AND 10"),
        CheckConstraint("defense_rating BETWEEN 1 AND 10"),
    )
