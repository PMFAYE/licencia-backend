from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.database import get_db
from app.schemas.offre_schema import OffreResponse

router = APIRouter(prefix="/offres", tags=["Offres"])


@router.get("", response_model=List[OffreResponse])
def list_offres(db: Session = Depends(get_db)):
    """Liste toutes les offres actives (endpoint public)."""
    offres = (
        db.query(models.Offre)
        .filter(models.Offre.actif == True)
        .order_by(models.Offre.ordre)
        .all()
    )
    return offres


@router.get("/{offre_id}", response_model=OffreResponse)
def get_offre(offre_id: int, db: Session = Depends(get_db)):
    """Détail d'une offre (endpoint public)."""
    offre = db.query(models.Offre).filter(models.Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return offre
