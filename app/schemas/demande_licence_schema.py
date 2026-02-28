from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DemandeLicenceBase(BaseModel):
    type_demande: str
    nom: str
    prenom: str
    date_naissance: datetime
    categorie_id: int
    # pas besoin du club_id ici, tu l’infères du user

class DemandeLicenceCreate(DemandeLicenceBase):
    statut: Optional[str] = "brouillon"

class DemandeLicenceUpdateStatut(BaseModel):
    statut: str
    commentaire_refus: Optional[str] = None

class DemandeLicenceRead(BaseModel):
    id: int
    statut: str
    type_demande: str
    nom: str
    prenom: str
    date_naissance: datetime
    categorie_id: int
    club_id: int
    date_creation: datetime
    date_soumission: Optional[datetime]
    date_validation: Optional[datetime]
    date_refus: Optional[datetime]
    commentaire_refus: Optional[str]

    class Config:
        from_attributes = True
