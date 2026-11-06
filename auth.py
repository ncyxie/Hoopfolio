import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import engine
from models import LoginSession, User, UserRole


router = APIRouter(prefix="/auth", tags=["Autentifikacija"])
password_hasher = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET nerastas .env faile")

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_DAYS = 7


# --------------------------------------------------
# UŽKLAUSŲ IR ATSAKYMŲ SCHEMOS
# --------------------------------------------------

class RegisterData(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginData(BaseModel):
    email: EmailStr
    password: str


class RefreshData(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# --------------------------------------------------
# ŽETONŲ SUKŪRIMAS IR PATIKRINIMAS
# --------------------------------------------------

def create_access_token(user: User, session_id: str) -> str:
    now = datetime.now(timezone.utc)

    data = {
        "sub": str(user.id),                  # Naudotojo ID
        "role": user.role.value,              # Naudotojo rolė
        "sid": session_id,                    # Prisijungimo ID duomenų bazėje
        "type": "access",                    # Tai access, ne refresh žetonas
        "jti": uuid4().hex,                  # Unikalus šio JWT ID
        "iat": now,                          # Išdavimo laikas
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }

    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def hash_refresh_token(token: str) -> str:
    # DB saugome refresh žetono SHA-256 maišą, ne patį žetoną.
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def read_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict:
    error = HTTPException(
        status_code=401,
        detail="Trūksta arba negalioja prisijungimo žetonas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise error

    try:
        data = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "role", "sid", "type", "exp"]},
        )

        if data["type"] != "access":
            raise error

        int(data["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise error

    return data


def get_current_user(data: dict = Depends(read_access_token)) -> User:
    with Session(engine) as session:
        login_session = session.get(LoginSession, data["sid"])
        user = session.get(User, int(data["sub"]))

        # Atsijungusio arba pasibaigusio prisijungimo žetonai nebeveikia.
        if login_session is None or login_session.revoked:
            raise HTTPException(status_code=401, detail="Prisijungimas nebegalioja")

        now = int(datetime.now(timezone.utc).timestamp())
        if login_session.expires_at <= now:
            raise HTTPException(status_code=401, detail="Prisijungimas nebegalioja")

        # Patikriname, ar JWT naudotojas ir rolė sutampa su DB.
        if user is None or login_session.user_id != user.id:
            raise HTTPException(status_code=401, detail="Naudotojo duomenys nebegalioja")

        if data["role"] != user.role.value:
            raise HTTPException(status_code=401, detail="Naudotojo rolė pasikeitė")

        return user


# --------------------------------------------------
# REGISTRACIJA IR PRISIJUNGIMAS
# --------------------------------------------------

@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterData):
    email = str(data.email).lower()

    with Session(engine) as session:
        existing_user = session.scalar(select(User).where(User.email == email))
        if existing_user is not None:
            raise HTTPException(status_code=409, detail="El. paštas jau naudojamas")

        user = User(
            email=email,
            password_hash=password_hasher.hash(data.password),
            role=UserRole.reader,  # Registruojantis negalima pasirinkti admin rolės.
        )
        session.add(user)

        try:
            session.commit()
        except IntegrityError:
            # Apsauga, jei du žmonės tuo pačiu metu registruojasi tuo pačiu el. paštu.
            session.rollback()
            raise HTTPException(status_code=409, detail="El. paštas jau naudojamas")

        session.refresh(user)
        return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginData):
    email = str(data.email).lower()

    with Session(engine) as session:
        user = session.scalar(select(User).where(User.email == email))

        if user is None or not password_hasher.verify(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Neteisingas el. paštas arba slaptažodis")

        refresh_token = secrets.token_urlsafe(48)
        expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS)

        login_session = LoginSession(
            id=uuid4().hex,
            user_id=user.id,
            refresh_hash=hash_refresh_token(refresh_token),
            expires_at=int(expires.timestamp()),
        )
        session.add(login_session)
        session.commit()

        return TokenResponse(
            access_token=create_access_token(user, login_session.id),
            refresh_token=refresh_token,
        )


# --------------------------------------------------
# ŽETONO ATNAUJINIMAS IR ATSIJUNGIMAS
# --------------------------------------------------

@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshData):
    old_hash = hash_refresh_token(data.refresh_token)

    with Session(engine) as session:
        query = select(LoginSession).where(LoginSession.refresh_hash == old_hash)
        # Užrakiname DB eilutę, kad to paties refresh žetono nepanaudotų du kartus.
        login_session = session.scalar(query.with_for_update())

        if login_session is None or login_session.revoked:
            raise HTTPException(status_code=401, detail="Refresh token nebegalioja")

        now = int(datetime.now(timezone.utc).timestamp())
        if login_session.expires_at <= now:
            raise HTTPException(status_code=401, detail="Refresh token nebegalioja")

        user = session.get(User, login_session.user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="Naudotojas nerastas")

        # Naujas refresh žetonas pakeičia senąjį toje pačioje sesijoje.
        new_refresh_token = secrets.token_urlsafe(48)
        expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS)

        login_session.refresh_hash = hash_refresh_token(new_refresh_token)
        login_session.expires_at = int(expires.timestamp())
        session.commit()

        return TokenResponse(
            access_token=create_access_token(user, login_session.id),
            refresh_token=new_refresh_token,
        )


@router.post("/logout", status_code=204)
def logout(
    user: User = Depends(get_current_user),
    data: dict = Depends(read_access_token),
):
    # get_current_user jau patikrino, kad prisijungimas galioja.
    with Session(engine) as session:
        login_session = session.get(LoginSession, data["sid"])

        if login_session is None or login_session.user_id != user.id:
            raise HTTPException(status_code=401, detail="Prisijungimas nebegalioja")

        login_session.revoked = True
        session.commit()


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
