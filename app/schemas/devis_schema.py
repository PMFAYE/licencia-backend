from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class DevisCreate(BaseModel):
    nom_contact: str
    email_contact: str
    telephone_contact: Optional[str] = None
    nom_organisation: Optional[str] = None
    type_organisation: Optional[str] = None
    message: Optional[str] = None
    offre_ids: List[int] = []


class DevisItemResponse(BaseModel):
    id: int
    offre_id: int
    offre_nom: Optional[str] = None

    class Config:
        from_attributes = True


class DevisResponse(BaseModel):
    id: int
    reference: str
    statut: str
    nom_contact: str
    email_contact: str
    telephone_contact: Optional[str] = None
    nom_organisation: Optional[str] = None
    type_organisation: Optional[str] = None
    message: Optional[str] = None
    date_creation: Optional[datetime] = None
    date_traitement: Optional[datetime] = None
    items: List[DevisItemResponse] = []

    class Config:
        from_attributes = True


class DevisStatusUpdate(BaseModel):
    statut: str  # nouveau, en_cours, accepte, refuse
