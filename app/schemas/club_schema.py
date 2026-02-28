from pydantic import BaseModel, EmailStr
from typing import Optional, List


# ----------------------------
# CATEGORIES
# ----------------------------
class CategorieBase(BaseModel):
    id: int
    nom: str

    class Config:
        from_attributes = True


# ----------------------------
# INFOS TYPES
# ----------------------------
class ClubInfoTypeBase(BaseModel):
    id: int
    valeur: str
    description: Optional[str]

    class Config:
        from_attributes = True


# ----------------------------
# INFOS CLUB
# ----------------------------
class ClubInfoBase(BaseModel):
    id: int
    club_id: int
    id_type: int
    valeur: Optional[str]
    type_info: Optional[ClubInfoTypeBase]

    class Config:
        from_attributes = True


# ----------------------------
# CLUBS
# ----------------------------
class ClubOut(BaseModel):
    id: int
    nom: Optional[str] = None
    raison_sociale: Optional[str] = None
    division: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class ClubDetail(ClubOut):
    infos: List[ClubInfoBase] = []

    class Config:
        from_attributes = True


class ClubCreate(BaseModel):
    nom: str
    raison_sociale: Optional[str]
    adresse: Optional[str]
    email: EmailStr
    telephone: Optional[str]
    federation_id: int
    ligue_id: Optional[int]


    class Config:
        from_attributes = True