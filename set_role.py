import sys
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import engine
from models import User, UserRole

if len(sys.argv) != 3 or sys.argv[2] not in ("reader", "analyst", "admin"):
    print("Naudojimas: python set_role.py elpastas@example.com reader|analyst|admin")
    sys.exit(1)

email = sys.argv[1].lower()
role = UserRole(sys.argv[2])

with Session(engine) as session:
    user = session.scalar(select(User).where(User.email == email))
    if user is None:
        print("Naudotojas nerastas. Pirmiausia reikia užregistruoti naudotoją per /auth/register.")
        sys.exit(1)

    user.role = role
    session.commit()
    print(f"Naudotojo {email} rolė pakeista į {role.value}.")

print("Reikia prisijungti iš naujo per /auth/login, kad JWT turėtų naują rolę.")
