from pydantic import BaseModel, EmailStr
from typing import Optional


class ClubBase(BaseModel):
    id: int
    nom: str
    raison_sociale: Optional[str] = None
    division: Optional[str] = None

    class Config:
        from_attributes = True

class FederationBase(BaseModel):
    id: int
    nom: str

    class Config:
        from_attributes = True

class LigueBase(BaseModel):
    id: int
    nom: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    password: str
    club_id: Optional[int] = None
    federation_id: int
    role: Optional[str] = None
    token: str


class UserResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    email: EmailStr
    club_id: Optional[int] = None
    role: Optional[str] = None
    club: Optional[ClubBase] = None
    federation: Optional[FederationBase] = None
    ligue: Optional[LigueBase] = None

    class Config:
        from_attributes = True


class InvitationRequest(BaseModel):
    email: EmailStr
    role: str
    club_id: Optional[int] = None
    federation_id: int