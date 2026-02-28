from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.database import get_db
from app.api.v1.routes.users import get_current_user
from app.db import models
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/federation", tags=["Fédérations"])

class CategorieResponse(BaseModel):
    id: int
    nom: str

    class Config:
        from_attributes = True



@router.get("/{federation_id}/categories", response_model=List[CategorieResponse])
def get_categories_federation(
    federation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not federation_id:
        raise HTTPException(status_code=400, detail="Utilisateur sans fédération assignée")
    
    federation = db.query(models.Federation).filter(
        models.Federation.id == federation_id
    ).first()
    
    if not federation:
        raise HTTPException(status_code=404, detail="Fédération non trouvée")
    
    categories = [fc.categorie for fc in federation.federation_categories]
    return categories


@router.get("/{federation_id}")
def get_federation(federation_id: int, db: Session = Depends(get_db)):
    federation = (
        db.query(models.Federation)
        .options(
            joinedload(models.Federation.ligues),
            joinedload(models.Federation.clubs),
            joinedload(models.Federation.federation_categories)
                .joinedload(models.FederationCategorie.categorie),
            joinedload(models.Federation.competitions),
        )
        .filter(models.Federation.id == federation_id)
        .first()
    )

    if not federation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fédération {federation_id} introuvable"
        )

    # Construction d'une réponse propre
    return {
        "id": federation.id,
        "name": federation.name,
        "code": federation.code,
        "ligues": [{"id": l.id, "name": l.name, "code": l.code} for l in federation.ligues],
        "clubs": [{"id": c.id, "nom": c.nom, "email": c.email} for c in federation.clubs],
        "categories": [{"id": fc.categorie.id, "nom": fc.categorie.nom} for fc in federation.federation_categories],
        "competitions": [{"id": fcomp.id, "nom": fcomp.name} for fcomp in federation.competitions],
    }