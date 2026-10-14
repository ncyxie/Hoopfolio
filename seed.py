from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine
from models import (
    Watchlist,
    WatchlistEntry,
    ScoutingReport,
    TargetType,
    EntryStatus,
    Priority,
)


with Session(engine) as session:
    # Patikrinama, ar demonstraciniai duomenys jau egzistuoja.
    statement = select(Watchlist.id)
    statement = statement.where(Watchlist.name == "Demo - Bendras stebėjimas")
    existing = session.scalar(statement)

    if existing is not None:
        print("Demonstraciniai duomenys jau įkelti.")

    else:
        # --------------------------------------------------
        # 1. STEBĖJIMO SĄRAŠAI
        # --------------------------------------------------

        watchlists = [
            Watchlist(
                name="Demo - Bendras stebėjimas",
                purpose="Stebėti skirtingus žaidėjus ir komandas",
                owner_name="Skautas A",
            ),
            Watchlist(
                name="Demo - Eurolygos komandos",
                purpose="Analizuoti Eurolygos komandų žaidimą",
                owner_name="Skautas B",
            ),
            Watchlist(
                name="Demo - Perspektyvūs aukštaūgiai",
                purpose="Ieškoti jaunų vidurio puolėjų",
                owner_name="Skautas A",
            ),
            Watchlist(
                name="Demo - Komandinė gynyba",
                purpose="Vertinti komandų gynybines sistemas",
                owner_name="Skautas C",
            ),
            Watchlist(
                name="Demo - Atakuojantys gynėjai",
                purpose="Stebėti rezultatyvius gynėjus",
                owner_name="Skautas B",
            ),
        ]

        session.add_all(watchlists)
        session.flush()  # Sąrašų ID reikalingi stebimiems objektams susieti.

        # --------------------------------------------------
        # 2. STEBIMI ŽAIDĖJAI IR KOMANDOS
        # --------------------------------------------------

        # Kiekvienas stebimas objektas susiejamas su sąrašu per watchlist_id.
        # watchlists[0].id – pirmojo sąrašo ID duomenų bazėje.
        entries = [
            WatchlistEntry(
                watchlist_id=watchlists[0].id,
                target_type=TargetType.player,
                target_name="Lukas Valaitis",
                status=EntryStatus.watching,
                priority=Priority.high,
                context="Vertinti perdavimus ir aikštės matymą",
            ),
            WatchlistEntry(
                watchlist_id=watchlists[0].id,
                target_type=TargetType.team,
                target_name="Vilniaus Sakalai",
                status=EntryStatus.new,
                priority=Priority.medium,
                context="Analizuoti komandinį puolimą",
            ),
            WatchlistEntry(
                watchlist_id=watchlists[0].id,
                target_type=TargetType.player,
                target_name="Dominykas Petrauskas",
                status=EntryStatus.watching,
                priority=Priority.low,
                context="Stebėti individualią gynybą",
            ),
            WatchlistEntry(
                watchlist_id=watchlists[0].id,
                target_type=TargetType.team,
                target_name="Kauno Perkūnas",
                status=EntryStatus.closed,
                priority=Priority.low,
                context="Pirminė komandos analizė baigta",
            ),
            WatchlistEntry(
                watchlist_id=watchlists[1].id,
                target_type=TargetType.team,
                target_name="Kauno Žalgiris",
                status=EntryStatus.watching,
                priority=Priority.high,
                context="Stebėti puolimo derinius",
            ),
            WatchlistEntry(
                watchlist_id=watchlists[1].id,
                target_type=TargetType.team,
                target_name="FC Barcelona",
                status=EntryStatus.new,
                priority=Priority.medium,
                context="Analizuoti žaidimą prieš zoninę gynybą",
            ),
            WatchlistEntry(
                watchlist_id=watchlists[2].id,
                target_type=TargetType.player,
                target_name="Nojus Rimkus",
                status=EntryStatus.watching,
                priority=Priority.high,
                context="Vertinti kovą dėl atšokusių kamuolių",
            ),
            WatchlistEntry(
                watchlist_id=watchlists[3].id,
                target_type=TargetType.team,
                target_name="Vilniaus Rytas",
                status=EntryStatus.watching,
                priority=Priority.high,
                context="Analizuoti perimetro gynybą",
            ),
            WatchlistEntry(
                watchlist_id=watchlists[3].id,
                target_type=TargetType.team,
                target_name="Kauno Žalgiris",
                status=EntryStatus.new,
                priority=Priority.medium,
                context="Stebėti gynybinius keitimus",
            ),
            WatchlistEntry(
                watchlist_id=watchlists[4].id,
                target_type=TargetType.player,
                target_name="Matas Jankauskas",
                status=EntryStatus.watching,
                priority=Priority.medium,
                context="Vertinti metimą ir prasiveržimus",
            ),
        ]

        session.add_all(entries)
        session.flush()  # Stebimų objektų ID reikalingi ataskaitoms susieti.

        # --------------------------------------------------
        # 3. SKAUTAVIMO ATASKAITOS
        # --------------------------------------------------

        # Kiekviena ataskaita susiejama su stebimu objektu per entry_id.
        # entries[0].id – pirmojo stebimo objekto ID duomenų bazėje.
        reports = [
            ScoutingReport(
                entry_id=entries[0].id,
                scout_name="Skautas A",
                observation_date=date(2026, 9, 10),
                strengths="Tikslūs perdavimai ir geras aikštės matymas",
                weaknesses="Nestabili individuali gynyba",
                insights="Gerai valdo rungtynių tempą",
                conclusion="Verta tęsti stebėjimą",
                statistics_note="Demonstracinė perdavimų analizė",
                offense_rating=8,
                defense_rating=6,
            ),
            ScoutingReport(
                entry_id=entries[0].id,
                scout_name="Skautas B",
                observation_date=date(2026, 9, 18),
                strengths="Greiti sprendimai puolime",
                weaknesses="Kartais skuba atakuodamas",
                insights="Gerai žaidžia du prieš du",
                conclusion="Perspektyvus įžaidėjas",
                statistics_note="Demonstracinė puolimo situacijų analizė",
                offense_rating=9,
                defense_rating=6,
            ),
            ScoutingReport(
                entry_id=entries[0].id,
                scout_name="Skautas A",
                observation_date=date(2026, 10, 2),
                strengths="Geras kamuolio valdymas",
                weaknesses="Trūksta fizinės jėgos gynyboje",
                insights="Pastebimas sprendimų priėmimo progresas",
                conclusion="Rekomenduojama stebėti toliau",
                statistics_note="Demonstracinė žaidimo tempo analizė",
                offense_rating=8,
                defense_rating=7,
            ),
            ScoutingReport(
                entry_id=entries[1].id,
                scout_name="Skautas C",
                observation_date=date(2026, 9, 12),
                strengths="Geras komandinis puolimas",
                weaknesses="Silpna greitų atakų gynyba",
                insights="Komanda dažnai išnaudoja kraštus",
                conclusion="Reikia gerinti gynybinį balansą",
                statistics_note="Demonstracinis komandinių veiksmų vertinimas",
                offense_rating=8,
                defense_rating=5,
            ),
            ScoutingReport(
                entry_id=entries[2].id,
                scout_name="Skautas B",
                observation_date=date(2026, 9, 15),
                strengths="Aktyvi gynyba ir greitos rankos",
                weaknesses="Nestabilus metimas iš toli",
                insights="Naudingas spaudžiant varžovus",
                conclusion="Tinka gynybinio gynėjo vaidmeniui",
                statistics_note="Demonstracinė gynybos analizė",
                offense_rating=6,
                defense_rating=8,
            ),
            ScoutingReport(
                entry_id=entries[3].id,
                scout_name="Skautas A",
                observation_date=date(2026, 9, 20),
                strengths="Geras kamuolio judėjimas",
                weaknesses="Sunkumai ginantis baudos aikštelėje",
                insights="Komanda dažnai kuria laisvus metimus",
                conclusion="Puolimas stipresnis už gynybą",
                statistics_note="Demonstracinė komandos analizė",
                offense_rating=7,
                defense_rating=5,
            ),
            ScoutingReport(
                entry_id=entries[4].id,
                scout_name="Skautas B",
                observation_date=date(2026, 9, 24),
                strengths="Geras puolimo organizavimas",
                weaknesses="Pasitaiko klaidų ginantis perimetre",
                insights="Efektyviai naudojami užtvarų deriniai",
                conclusion="Komanda verta tolesnės analizės",
                statistics_note="Demonstracinė Eurolygos komandos analizė",
                offense_rating=8,
                defense_rating=7,
            ),
            ScoutingReport(
                entry_id=entries[6].id,
                scout_name="Skautas A",
                observation_date=date(2026, 9, 27),
                strengths="Gera kova dėl atšokusių kamuolių",
                weaknesses="Ribotas metimo nuotolis",
                insights="Sėkmingai saugo baudos aikštelę",
                conclusion="Perspektyvus gynybinis aukštaūgis",
                statistics_note="Demonstracinė aukštaūgio analizė",
                offense_rating=6,
                defense_rating=9,
            ),
            ScoutingReport(
                entry_id=entries[8].id,
                scout_name="Skautas C",
                observation_date=date(2026, 10, 1),
                strengths="Gera pagalba komandos draugams",
                weaknesses="Kartais vėluoja gynybiniai keitimai",
                insights="Efektyvūs dvigubinimai",
                conclusion="Reikia gerinti komunikaciją",
                statistics_note="Demonstracinė komandinės gynybos analizė",
                offense_rating=7,
                defense_rating=8,
            ),
            ScoutingReport(
                entry_id=entries[9].id,
                scout_name="Skautas B",
                observation_date=date(2026, 10, 5),
                strengths="Geras metimas ir greitas pirmas žingsnis",
                weaknesses="Silpnesnė gynyba prieš fiziškus varžovus",
                insights="Geba susikurti metimo situacijas",
                conclusion="Perspektyvus atakuojantis gynėjas",
                statistics_note="Demonstracinė individualaus puolimo analizė",
                offense_rating=9,
                defense_rating=6,
            ),
        ]

        session.add_all(reports)

        # Patvirtinamas visų demonstracinių įrašų įrašymas.
        session.commit()

        print("Demonstraciniai duomenys sėkmingai įkelti!")
        print("Sukurti 5 sąrašai, 10 objektų ir 10 ataskaitų.")
