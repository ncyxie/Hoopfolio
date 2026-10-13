
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
    Priority
)


with Session(engine) as session:

    # Patikriname, ar demonstraciniai duomenys jau buvo įkelti
    existing = session.scalar(
        select(Watchlist.id)
        .where(Watchlist.name == "Demo - Bendras stebėjimas")
    )

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
                owner_name="Skautas A"
            ),
            Watchlist(
                name="Demo - Eurolygos komandos",
                purpose="Analizuoti Eurolygos komandų žaidimą",
                owner_name="Skautas B"
            ),
            Watchlist(
                name="Demo - Perspektyvūs aukštaūgiai",
                purpose="Ieškoti jaunų vidurio puolėjų",
                owner_name="Skautas A"
            ),
            Watchlist(
                name="Demo - Komandinė gynyba",
                purpose="Vertinti komandų gynybines sistemas",
                owner_name="Skautas C"
            ),
            Watchlist(
                name="Demo - Atakuojantys gynėjai",
                purpose="Stebėti rezultatyvius gynėjus",
                owner_name="Skautas B"
            )
        ]

        session.add_all(watchlists)
        session.flush()

        # --------------------------------------------------
        # 2. STEBIMI ŽAIDĖJAI IR KOMANDOS
        # --------------------------------------------------

        # Pirmas skaičius nurodo sąrašą iš watchlists
        entries_data = [
            (0, TargetType.player, "Lukas Valaitis",
             EntryStatus.watching, Priority.high,
             "Vertinti perdavimus ir aikštės matymą"),

            (0, TargetType.team, "Vilniaus Sakalai",
             EntryStatus.new, Priority.medium,
             "Analizuoti komandinį puolimą"),

            (0, TargetType.player, "Dominykas Petrauskas",
             EntryStatus.watching, Priority.low,
             "Stebėti individualią gynybą"),

            (0, TargetType.team, "Kauno Perkūnas",
             EntryStatus.closed, Priority.low,
             "Pirminė komandos analizė baigta"),

            (1, TargetType.team, "Kauno Žalgiris",
             EntryStatus.watching, Priority.high,
             "Stebėti puolimo derinius"),

            (1, TargetType.team, "FC Barcelona",
             EntryStatus.new, Priority.medium,
             "Analizuoti žaidimą prieš zoninę gynybą"),

            (2, TargetType.player, "Nojus Rimkus",
             EntryStatus.watching, Priority.high,
             "Vertinti kovą dėl atšokusių kamuolių"),

            (3, TargetType.team, "Vilniaus Rytas",
             EntryStatus.watching, Priority.high,
             "Analizuoti perimetro gynybą"),

            (3, TargetType.team, "Kauno Žalgiris",
             EntryStatus.new, Priority.medium,
             "Stebėti gynybinius keitimus"),

            (4, TargetType.player, "Matas Jankauskas",
             EntryStatus.watching, Priority.medium,
             "Vertinti metimą ir prasiveržimus")
        ]

        entries = []

        for list_index, target_type, target_name, status, priority, context in entries_data:
            entry = WatchlistEntry(
                watchlist_id=watchlists[list_index].id,
                target_type=target_type,
                target_name=target_name,
                status=status,
                priority=priority,
                context=context
            )

            entries.append(entry)

        session.add_all(entries)
        session.flush()

        # --------------------------------------------------
        # 3. SKAUTAVIMO ATASKAITOS
        # --------------------------------------------------

        # Pirmas skaičius nurodo objektą iš entries
        reports_data = [
            (
                0, "Skautas A", date(2026, 9, 10),
                "Tikslūs perdavimai ir geras aikštės matymas",
                "Nestabili individuali gynyba",
                "Gerai valdo rungtynių tempą",
                "Verta tęsti stebėjimą",
                "Demonstracinė perdavimų analizė",
                8, 6
            ),
            (
                0, "Skautas B", date(2026, 9, 18),
                "Greiti sprendimai puolime",
                "Kartais skuba atakuodamas",
                "Gerai žaidžia du prieš du",
                "Perspektyvus įžaidėjas",
                "Demonstracinė puolimo situacijų analizė",
                9, 6
            ),
            (
                0, "Skautas A", date(2026, 10, 2),
                "Geras kamuolio valdymas",
                "Trūksta fizinės jėgos gynyboje",
                "Pastebimas sprendimų priėmimo progresas",
                "Rekomenduojama stebėti toliau",
                "Demonstracinė žaidimo tempo analizė",
                8, 7
            ),
            (
                1, "Skautas C", date(2026, 9, 12),
                "Geras komandinis puolimas",
                "Silpna greitų atakų gynyba",
                "Komanda dažnai išnaudoja kraštus",
                "Reikia gerinti gynybinį balansą",
                "Demonstracinis komandinių veiksmų vertinimas",
                8, 5
            ),
            (
                2, "Skautas B", date(2026, 9, 15),
                "Aktyvi gynyba ir greitos rankos",
                "Nestabilus metimas iš toli",
                "Naudingas spaudžiant varžovus",
                "Tinka gynybinio gynėjo vaidmeniui",
                "Demonstracinė gynybos analizė",
                6, 8
            ),
            (
                3, "Skautas A", date(2026, 9, 20),
                "Geras kamuolio judėjimas",
                "Sunkumai ginantis baudos aikštelėje",
                "Komanda dažnai kuria laisvus metimus",
                "Puolimas stipresnis už gynybą",
                "Demonstracinė komandos analizė",
                7, 5
            ),
            (
                4, "Skautas B", date(2026, 9, 24),
                "Geras puolimo organizavimas",
                "Pasitaiko klaidų ginantis perimetre",
                "Efektyviai naudojami užtvarų deriniai",
                "Komanda verta tolesnės analizės",
                "Demonstracinė Eurolygos komandos analizė",
                8, 7
            ),
            (
                6, "Skautas A", date(2026, 9, 27),
                "Gera kova dėl atšokusių kamuolių",
                "Ribotas metimo nuotolis",
                "Sėkmingai saugo baudos aikštelę",
                "Perspektyvus gynybinis aukštaūgis",
                "Demonstracinė aukštaūgio analizė",
                6, 9
            ),
            (
                8, "Skautas C", date(2026, 10, 1),
                "Gera pagalba komandos draugams",
                "Kartais vėluoja gynybiniai keitimai",
                "Efektyvūs dvigubinimai",
                "Reikia gerinti komunikaciją",
                "Demonstracinė komandinės gynybos analizė",
                7, 8
            ),
            (
                9, "Skautas B", date(2026, 10, 5),
                "Geras metimas ir greitas pirmas žingsnis",
                "Silpnesnė gynyba prieš fiziškus varžovus",
                "Geba susikurti metimo situacijas",
                "Perspektyvus atakuojantis gynėjas",
                "Demonstracinė individualaus puolimo analizė",
                9, 6
            )
        ]

        reports = []

        for (
            entry_index,
            scout_name,
            observation_date,
            strengths,
            weaknesses,
            insights,
            conclusion,
            statistics_note,
            offense_rating,
            defense_rating
        ) in reports_data:

            report = ScoutingReport(
                entry_id=entries[entry_index].id,
                scout_name=scout_name,
                observation_date=observation_date,
                strengths=strengths,
                weaknesses=weaknesses,
                insights=insights,
                conclusion=conclusion,
                statistics_note=statistics_note,
                offense_rating=offense_rating,
                defense_rating=defense_rating
            )

            reports.append(report)

        session.add_all(reports)

        # Visus duomenis išsaugome PostgreSQL
        session.commit()

        print("Demonstraciniai duomenys sėkmingai įkelti!")
        print("Sukurti 5 sąrašai, 10 objektų ir 10 ataskaitų.")
