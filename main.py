from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database import engine
from models import Watchlist, WatchlistEntry, ScoutingReport, TargetType, EntryStatus, Priority
from schemas import (
    WatchlistCreate,
    WatchlistResponse,
    WatchlistEntryCreate,
    WatchlistEntryResponse,
    ScoutingReportCreate,
    ScoutingReportResponse,
)


app = FastAPI(title="Hoopfolio API")


# --------------------------------------------------
# PRADINIS API METODAS
# --------------------------------------------------

@app.get("/")
def home():
    return {"message": "Hoopfolio API veikia"}


# --------------------------------------------------
# WATCHLISTS - STEBĖJIMO SĄRAŠAI
# --------------------------------------------------

# 1. Gauti sąrašus, filtruoti pagal pavadinimą ir puslapiuoti
@app.get("/watchlists", response_model=list[WatchlistResponse])
def get_watchlists(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    name: str | None = None,
):
    with Session(engine) as session:
        statement = select(Watchlist)

        if name is not None:
            statement = statement.where(Watchlist.name.ilike(f"%{name}%"))

        statement = statement.order_by(Watchlist.id)
        statement = statement.offset((page - 1) * per_page)
        statement = statement.limit(per_page)

        return session.scalars(statement).all()


# 2. Sukurti naują sąrašą
@app.post("/watchlists", response_model=WatchlistResponse, status_code=201)
def create_watchlist(data: WatchlistCreate):
    with Session(engine) as session:
        new_watchlist = Watchlist(
            name=data.name,
            purpose=data.purpose,
            owner_name=data.owner_name,
        )

        session.add(new_watchlist)
        session.commit()
        session.refresh(new_watchlist)

        return new_watchlist


# 3. Gauti vieną sąrašą
@app.get("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist(watchlist_id: int):
    with Session(engine) as session:
        watchlist = session.get(Watchlist, watchlist_id)

        if watchlist is None:
            raise HTTPException(status_code=404, detail="Stebėjimo sąrašas nerastas")

        return watchlist


# 4. Atnaujinti sąrašą
@app.put("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
def update_watchlist(watchlist_id: int, data: WatchlistCreate):
    with Session(engine) as session:
        watchlist = session.get(Watchlist, watchlist_id)

        if watchlist is None:
            raise HTTPException(status_code=404, detail="Stebėjimo sąrašas nerastas")

        watchlist.name = data.name
        watchlist.purpose = data.purpose
        watchlist.owner_name = data.owner_name

        session.commit()
        session.refresh(watchlist)
        return watchlist


# 5. Ištrinti sąrašą
@app.delete("/watchlists/{watchlist_id}", status_code=204)
def delete_watchlist(watchlist_id: int):
    with Session(engine) as session:
        watchlist = session.get(Watchlist, watchlist_id)

        if watchlist is None:
            raise HTTPException(status_code=404, detail="Stebėjimo sąrašas nerastas")

        # Negalima trinti sąrašo, kuriame dar yra stebimų objektų.
        statement = select(WatchlistEntry.id)
        statement = statement.where(WatchlistEntry.watchlist_id == watchlist_id)
        entry_id = session.scalar(statement.limit(1))

        if entry_id is not None:
            raise HTTPException(
                status_code=409,
                detail="Negalima ištrinti sąrašo, kuriame yra stebimų objektų",
            )

        session.delete(watchlist)
        session.commit()


# --------------------------------------------------
# WATCHLIST ENTRIES - STEBIMI ŽAIDĖJAI IR KOMANDOS
# --------------------------------------------------

# 1. Gauti sąrašo stebimus objektus
@app.get("/watchlists/{watchlist_id}/entries", response_model=list[WatchlistEntryResponse])
def get_watchlist_entries(
    watchlist_id: int,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    target_type: TargetType | None = None,
    status: EntryStatus | None = None,
    priority: Priority | None = None,
):
    with Session(engine) as session:
        watchlist = session.get(Watchlist, watchlist_id)

        if watchlist is None:
            raise HTTPException(status_code=404, detail="Stebėjimo sąrašas nerastas")

        # Imame tik tuos objektus, kurie priklauso nurodytam sąrašui.
        statement = select(WatchlistEntry)
        statement = statement.where(WatchlistEntry.watchlist_id == watchlist_id)

        if target_type is not None:
            statement = statement.where(WatchlistEntry.target_type == target_type)

        if status is not None:
            statement = statement.where(WatchlistEntry.status == status)

        if priority is not None:
            statement = statement.where(WatchlistEntry.priority == priority)

        statement = statement.order_by(WatchlistEntry.id)
        statement = statement.offset((page - 1) * per_page)
        statement = statement.limit(per_page)

        return session.scalars(statement).all()


# 2. Pridėti žaidėją arba komandą į sąrašą
@app.post(
    "/watchlists/{watchlist_id}/entries",
    response_model=WatchlistEntryResponse,
    status_code=201,
)
def create_watchlist_entry(watchlist_id: int, data: WatchlistEntryCreate):
    with Session(engine) as session:
        watchlist = session.get(Watchlist, watchlist_id)

        if watchlist is None:
            raise HTTPException(status_code=404, detail="Stebėjimo sąrašas nerastas")

        new_entry = WatchlistEntry(
            watchlist_id=watchlist_id,
            target_type=data.target_type,
            target_name=data.target_name,
            status=data.status,
            priority=data.priority,
            context=data.context,
        )

        session.add(new_entry)
        session.commit()
        session.refresh(new_entry)
        return new_entry


# 3. Gauti vieną stebimą objektą
@app.get(
    "/watchlists/{watchlist_id}/entries/{entry_id}",
    response_model=WatchlistEntryResponse,
)
def get_watchlist_entry(watchlist_id: int, entry_id: int):
    with Session(engine) as session:
        entry = session.get(WatchlistEntry, entry_id)

        # Tikriname ne tik ID, bet ir ar objektas priklauso šiam sąrašui.
        if entry is None or entry.watchlist_id != watchlist_id:
            raise HTTPException(status_code=404, detail="Stebimas objektas šiame sąraše nerastas")

        return entry


# 4. Atnaujinti stebimą objektą
@app.put(
    "/watchlists/{watchlist_id}/entries/{entry_id}",
    response_model=WatchlistEntryResponse,
)
def update_watchlist_entry(watchlist_id: int, entry_id: int, data: WatchlistEntryCreate):
    with Session(engine) as session:
        entry = session.get(WatchlistEntry, entry_id)

        if entry is None or entry.watchlist_id != watchlist_id:
            raise HTTPException(status_code=404, detail="Stebimas objektas šiame sąraše nerastas")

        entry.target_type = data.target_type
        entry.target_name = data.target_name
        entry.status = data.status
        entry.priority = data.priority
        entry.context = data.context

        session.commit()
        session.refresh(entry)
        return entry


# 5. Ištrinti stebimą objektą
@app.delete("/watchlists/{watchlist_id}/entries/{entry_id}", status_code=204)
def delete_watchlist_entry(watchlist_id: int, entry_id: int):
    with Session(engine) as session:
        entry = session.get(WatchlistEntry, entry_id)

        if entry is None or entry.watchlist_id != watchlist_id:
            raise HTTPException(status_code=404, detail="Stebimas objektas šiame sąraše nerastas")

        # Negalima trinti objekto, kuris turi ataskaitų.
        statement = select(ScoutingReport.id)
        statement = statement.where(ScoutingReport.entry_id == entry_id)
        report_id = session.scalar(statement.limit(1))

        if report_id is not None:
            raise HTTPException(
                status_code=409,
                detail="Negalima ištrinti objekto, kuris turi skautavimo ataskaitų",
            )

        session.delete(entry)
        session.commit()


# --------------------------------------------------
# SCOUTING REPORTS - SKAUTAVIMO ATASKAITOS
# --------------------------------------------------

# 1. Gauti objekto ataskaitas
@app.get(
    "/watchlists/{watchlist_id}/entries/{entry_id}/reports",
    response_model=list[ScoutingReportResponse],
)
def get_scouting_reports(
    watchlist_id: int,
    entry_id: int,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    scout_name: str | None = None,
):
    with Session(engine) as session:
        entry = session.get(WatchlistEntry, entry_id)

        if entry is None or entry.watchlist_id != watchlist_id:
            raise HTTPException(status_code=404, detail="Stebimas objektas šiame sąraše nerastas")

        statement = select(ScoutingReport)
        statement = statement.where(ScoutingReport.entry_id == entry_id)

        if scout_name is not None:
            statement = statement.where(ScoutingReport.scout_name.ilike(f"%{scout_name}%"))

        statement = statement.order_by(ScoutingReport.id)
        statement = statement.offset((page - 1) * per_page)
        statement = statement.limit(per_page)

        reports = session.scalars(statement).all()

        # watchlist_id gavome iš URL, o ataskaitoje jo nėra.
        # Pridedame jį tik atsakymui, kad veiktų _links nuorodos.
        for report in reports:
            report.watchlist_id = watchlist_id

        return reports


# 2. Sukurti naują skautavimo ataskaitą
@app.post(
    "/watchlists/{watchlist_id}/entries/{entry_id}/reports",
    response_model=ScoutingReportResponse,
    status_code=201,
)
def create_scouting_report(watchlist_id: int, entry_id: int, data: ScoutingReportCreate):
    with Session(engine) as session:
        entry = session.get(WatchlistEntry, entry_id)

        if entry is None or entry.watchlist_id != watchlist_id:
            raise HTTPException(status_code=404, detail="Stebimas objektas šiame sąraše nerastas")

        new_report = ScoutingReport(
            entry_id=entry_id,
            scout_name=data.scout_name,
            observation_date=data.observation_date,
            strengths=data.strengths,
            weaknesses=data.weaknesses,
            insights=data.insights,
            conclusion=data.conclusion,
            statistics_note=data.statistics_note,
            offense_rating=data.offense_rating,
            defense_rating=data.defense_rating,
        )

        session.add(new_report)
        session.commit()
        session.refresh(new_report)

        # Pridedame sąrašo ID tik atsakymo nuorodoms (ne DB lentelei).
        new_report.watchlist_id = watchlist_id
        return new_report


# 3. Gauti vieną ataskaitą
@app.get(
    "/watchlists/{watchlist_id}/entries/{entry_id}/reports/{report_id}",
    response_model=ScoutingReportResponse,
)
def get_scouting_report(watchlist_id: int, entry_id: int, report_id: int):
    with Session(engine) as session:
        entry = session.get(WatchlistEntry, entry_id)

        if entry is None or entry.watchlist_id != watchlist_id:
            raise HTTPException(status_code=404, detail="Stebimas objektas šiame sąraše nerastas")

        report = session.get(ScoutingReport, report_id)

        if report is None or report.entry_id != entry_id:
            raise HTTPException(status_code=404, detail="Skautavimo ataskaita nerasta")

        # Šio ID reikia atsakymo _links nuorodoms.
        report.watchlist_id = watchlist_id
        return report


# 4. Atnaujinti ataskaitą
@app.put(
    "/watchlists/{watchlist_id}/entries/{entry_id}/reports/{report_id}",
    response_model=ScoutingReportResponse,
)
def update_scouting_report(
    watchlist_id: int,
    entry_id: int,
    report_id: int,
    data: ScoutingReportCreate,
):
    with Session(engine) as session:
        entry = session.get(WatchlistEntry, entry_id)

        if entry is None or entry.watchlist_id != watchlist_id:
            raise HTTPException(status_code=404, detail="Stebimas objektas šiame sąraše nerastas")

        report = session.get(ScoutingReport, report_id)

        if report is None or report.entry_id != entry_id:
            raise HTTPException(status_code=404, detail="Skautavimo ataskaita nerasta")

        report.scout_name = data.scout_name
        report.observation_date = data.observation_date
        report.strengths = data.strengths
        report.weaknesses = data.weaknesses
        report.insights = data.insights
        report.conclusion = data.conclusion
        report.statistics_note = data.statistics_note
        report.offense_rating = data.offense_rating
        report.defense_rating = data.defense_rating

        session.commit()
        session.refresh(report)

        # Šio ID reikia atsakymo _links nuorodoms.
        report.watchlist_id = watchlist_id
        return report


# 5. Ištrinti ataskaitą
@app.delete(
    "/watchlists/{watchlist_id}/entries/{entry_id}/reports/{report_id}",
    status_code=204,
)
def delete_scouting_report(watchlist_id: int, entry_id: int, report_id: int):
    with Session(engine) as session:
        entry = session.get(WatchlistEntry, entry_id)

        if entry is None or entry.watchlist_id != watchlist_id:
            raise HTTPException(status_code=404, detail="Stebimas objektas šiame sąraše nerastas")

        report = session.get(ScoutingReport, report_id)

        if report is None or report.entry_id != entry_id:
            raise HTTPException(status_code=404, detail="Skautavimo ataskaita nerasta")

        session.delete(report)
        session.commit()


# --------------------------------------------------
# DASHBOARD - SKAUTAVIMO SUVESTINĖ
# --------------------------------------------------

@app.get("/dashboard")
def get_dashboard():
    with Session(engine) as session:
        # SQL užklausa suskaičiuoja, kiek kiekvienas sąrašas turi
        # stebimų objektų ir kiek tie objektai turi ataskaitų.
        statement = select(
            Watchlist.id,
            Watchlist.name,
            func.count(func.distinct(WatchlistEntry.id)).label("entries_count"),
            func.count(ScoutingReport.id).label("reports_count"),
        )
        statement = statement.outerjoin(
            WatchlistEntry,
            WatchlistEntry.watchlist_id == Watchlist.id,
        )
        statement = statement.outerjoin(
            ScoutingReport,
            ScoutingReport.entry_id == WatchlistEntry.id,
        )
        statement = statement.group_by(Watchlist.id, Watchlist.name)
        statement = statement.order_by(Watchlist.id)

        rows = session.execute(statement).all()

        # Paprastas ciklas vietoje sutrumpintų Python išraiškų.
        total_entries = 0
        total_reports = 0
        watchlists = []

        for row in rows:
            total_entries += row.entries_count
            total_reports += row.reports_count

            watchlists.append({
                "id": row.id,
                "name": row.name,
                "entries_count": row.entries_count,
                "reports_count": row.reports_count,
            })

        return {
            "total_watchlists": len(rows),
            "total_entries": total_entries,
            "total_reports": total_reports,
            "watchlists": watchlists,
        }
