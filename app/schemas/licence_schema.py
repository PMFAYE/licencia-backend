from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, date

# -------------------------------------------------------------------
# 🔹 Base commune (utilisée pour la création)
# -------------------------------------------------------------------
class LicenceBase(BaseModel):
    nom: str = Field(..., example="Sow")
    prenom: str = Field(..., example="Aminata")
    date_naissance: date = Field(..., example="2001-07-23")
    categorie_id: int = Field(..., example=3)
    club_id: int = Field(..., example=1)
    type_demande: str = Field(..., example="Nouvelle licence")

# -------------------------------------------------------------------
# 🟢 Création
# -------------------------------------------------------------------
class LicenceCreate(LicenceBase):
    """Données nécessaires à la création d’une licence."""
    adherent: Optional[int] = None  # ID de l'adhérent existant (optionnel)

# -------------------------------------------------------------------
# ✏️ Mise à jour
# -------------------------------------------------------------------
class LicenceUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    date_naissance: Optional[date] = None
    categorie_id: Optional[int] = None

# -------------------------------------------------------------------
# 🚀 Soumission
# -------------------------------------------------------------------
class LicenceSubmit(BaseModel):
    """Utilisé lors de la soumission d’une licence."""
    documents: Optional[List[str]] = []

# -------------------------------------------------------------------
# 📎 Fichiers attachés
# -------------------------------------------------------------------
class LicenceFichier(BaseModel):
    id: int
    nom_fichier: str
    type: Optional[str] = None
    chemin: str

    class Config:
        orm_mode = True

# -------------------------------------------------------------------
# 🔍 Réponse complète
# -------------------------------------------------------------------
class LicenceResponse(BaseModel):
    id: int
    numero: Optional[str] = None
    nom: str
    prenom: str
    date_naissance: date
    categorie: Optional[str] = None
    statut: str
    documents: List[LicenceFichier] = []
    motif_rejet: Optional[str] = None
    club_id: int

    # 🕒 Ajout de métadonnées pour l’audit
    date_creation: Optional[datetime] = None
    date_soumission: Optional[datetime] = None
    date_validation: Optional[datetime] = None
    date_refus: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

# -------------------------------------------------------------------
# 🔄 Changement de statut
# -------------------------------------------------------------------
class StatutUpdateSchema(BaseModel):
    statut: Literal["brouillon", "soumise", "en_verification", "validee", "refusee"]