from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DemandeBase(BaseModel):
    type: str
    commentaires: Optional[str] = None
    club_id: Optional[str] = None
    anneeAffiliation: Optional[str] = None
    categorie: Optional[str] = None
    nbParticipants: Optional[str] = None

class DemandeCreate(DemandeBase):
    # les champs obligatoires pour créer une demande
    nom: str
    prenom: str
    date_naissance: datetime  # ou str selon comment tu veux le gérer
    # éventuellement : statut explicite, mais tu peux le fixer côté backend
    # statut: Optional[str] = "brouillon"

class DemandeUpdate(BaseModel):
    statut: Optional[str] = None
    commentaires: Optional[str] = None

class DemandeOut(BaseModel):
    id: int
    type: str
    statut: str
    date_creation: datetime
    date_soumission: Optional[datetime]
    date_validation: Optional[datetime]
    date_refus: Optional[datetime]
    commentaires: Optional[str]

    # Relations optionnelles si tu veux retourner aussi :
    utilisateur_id: int
    club_id: int
    licence_id: Optional[int]

    class Config:
        from_attributes = True
