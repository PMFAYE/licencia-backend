from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OffreResponse(BaseModel):
    id: int
    nom: str
    description: Optional[str] = None
    description_courte: Optional[str] = None
    prix_mensuel: Optional[int] = None
    prix_annuel: Optional[int] = None
    devise: str = "XOF"
    fonctionnalites: Optional[List[str]] = None
    badge: Optional[str] = None
    populaire: bool = False
    actif: bool = True
    ordre: int = 0

    class Config:
        from_attributes = True


class OffreList(BaseModel):
    offres: List[OffreResponse]

    class Config:
        from_attributes = True
