from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CategorieBase(BaseModel):
    id: int
    nom: str

    class Config:
        from_attributes = True

class AdherentBase(BaseModel):
    nom: str
    prenom: str
    date_naissance: datetime
    genre: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    actif: Optional[bool] = True

class AdherentCreate(AdherentBase):
    categorie_id: Optional[int] = None

class AdherentUpdate(AdherentBase):
    categorie_id: Optional[int] = None

class AdherentCreateOut(AdherentBase):
    id: int
    club_id: int
    date_creation: datetime
    categorie_id: Optional[int] = None

class AdherentOut(AdherentBase):
    id: int
    club_id: int
    date_creation: datetime
    categorie: Optional[str] = None
    categorie_id: Optional[int] = None
    licence_numero: Optional[str] = None

    class Config:
        from_attributes = True