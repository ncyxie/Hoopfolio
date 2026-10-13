from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine
from models import Watchlist, WatchlistEntry
from schemas import WatchlistCreate, WatchlistResponse


app = FastAPI(title="Hoopfolio API")


@app.get("/")
def home():
    return {"message": "Hoopfolio API veikia"}


@app.get("/watchlists", response_model=list[WatchlistResponse])
def get_watchlists():
    with Session(engine) as session:
        statement = select(Watchlist).order_by(Watchlist.id)
        watchlists = session.scalars(statement).all()

        return watchlists


@app.post("/watchlists", response_model=WatchlistResponse, status_code=201)
def create_watchlist(watchlist: WatchlistCreate):
    with Session(engine) as session:
        new_watchlist = Watchlist(
            name=watchlist.name,
            purpose=watchlist.purpose,
            owner_name=watchlist.owner_name
        )

        session.add(new_watchlist)
        session.commit()
        session.refresh(new_watchlist)

        return new_watchlist


@app.get("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist(watchlist_id: int):
    with Session(engine) as session:
        watchlist = session.get(Watchlist, watchlist_id)

        if watchlist is None:
            raise HTTPException(
                status_code=404,
                detail="Stebėjimo sąrašas nerastas"
            )

        return watchlist


@app.put("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
def update_watchlist(watchlist_id: int, data: WatchlistCreate):
    with Session(engine) as session:
        watchlist = session.get(Watchlist, watchlist_id)

        if watchlist is None:
            raise HTTPException(
                status_code=404,
                detail="Stebėjimo sąrašas nerastas"
            )

        watchlist.name = data.name
        watchlist.purpose = data.purpose
        watchlist.owner_name = data.owner_name

        session.commit()
        session.refresh(watchlist)

        return watchlist


@app.delete("/watchlists/{watchlist_id}", status_code=204)
def delete_watchlist(watchlist_id: int):
    with Session(engine) as session:
        watchlist = session.get(Watchlist, watchlist_id)

        if watchlist is None:
            raise HTTPException(
                status_code=404,
                detail="Stebėjimo sąrašas nerastas"
            )

        entry_id = session.scalar(
            select(WatchlistEntry.id)
            .where(WatchlistEntry.watchlist_id == watchlist_id)
            .limit(1)
        )

        if entry_id is not None:
            raise HTTPException(
                status_code=409,
                detail="Negalima ištrinti sąrašo, kuriame yra stebimų objektų"
            )

        session.delete(watchlist)
        session.commit()