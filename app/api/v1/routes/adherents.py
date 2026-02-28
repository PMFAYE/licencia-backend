from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.db import models
from app.db.database import get_db
from app.schemas.adherent_schema import AdherentCreate, AdherentUpdate, AdherentOut, AdherentCreateOut
from app.api.v1.routes.users import get_current_user

router = APIRouter(prefix="/clubs/{club_id}", tags=["Adherents"])


# ------------------ Liste des adhérents ------------------
@router.get("/adherents", response_model=list[AdherentOut])
def list_adherents(club_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club introuvable")

    adherents = (
        db.query(models.Adherent)
        .options(
            joinedload(models.Adherent.licences),
            joinedload(models.Adherent.categorie),
        )
        .filter(models.Adherent.club_id == club_id)
        .all()
    )
    return [
        AdherentOut(
            id=ad.id,
            club_id=ad.club_id,
            nom=ad.nom,
            prenom=ad.prenom,
            date_creation=ad.date_creation,
            date_naissance=ad.date_naissance,
            genre=ad.genre,
            email=ad.email,
            telephone=ad.telephone,
            actif=ad.actif,
            categorie_id=ad.categorie.id if ad.categorie else None,
            categorie=ad.categorie.nom if ad.categorie else None,
            licence_numero=ad.licences[-1].numero if ad.licences else None,
        )
        for ad in adherents
    ]


# ------------------ Créer un adhérent ------------------
@router.post("/adherents", response_model=AdherentCreateOut, status_code=status.HTTP_201_CREATED)
def create_adherent(club_id: int, data: AdherentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club introuvable")

    # Créer l'adhérent
    adherent = models.Adherent(**data.dict(exclude={"licence_id"}), club_id=club_id)
    db.add(adherent)

    try:
        db.commit()
        db.refresh(adherent)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Un adhérent avec ce nom, prénom et cette date de naissance existe déjà dans ce club."
        )

    return AdherentCreateOut(
        id=adherent.id,
        club_id=adherent.club_id,
        date_creation=adherent.date_creation,
        nom=adherent.nom,
        prenom=adherent.prenom,
        date_naissance=adherent.date_naissance,
        genre=adherent.genre,
        email=adherent.email,
        telephone=adherent.telephone,
        actif=adherent.actif,
        categorie_id=adherent.categorie_id
    )


# ------------------ Détails d’un adhérent ------------------
@router.get("/adherents/{adherent_id}", response_model=AdherentOut)
def get_adherent(adherent_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    adherent = (
        db.query(models.Adherent)
        .options(
            joinedload(models.Adherent.licences),
            joinedload(models.Adherent.categorie),
        )
        .filter(models.Adherent.id == adherent_id)
        .first()
    )
    if not adherent:
        raise HTTPException(status_code=404, detail="Adhérent introuvable")

    return AdherentOut(
        id=adherent.id,
        club_id=adherent.club_id,
        nom=adherent.nom,
        prenom=adherent.prenom,
        date_creation=adherent.date_creation,
        date_naissance=adherent.date_naissance,
        genre=adherent.genre if adherent.genre else "",
        email=adherent.email,
        telephone=adherent.telephone,
        actif=adherent.actif,
        categorie_id=adherent.categorie.id if adherent.categorie else None,
        categorie=adherent.categorie.nom if adherent.categorie else None,
        licence_numero=adherent.licences[-1].numero if adherent.licences else None,
    )


# ------------------ Modifier un adhérent ------------------
@router.put("/adherents/{adherent_id}", response_model=AdherentCreateOut)
def update_adherent(adherent_id: int, data: AdherentUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    adherent = db.query(models.Adherent).filter(models.Adherent.id == adherent_id).first()
    if not adherent:
        raise HTTPException(status_code=404, detail="Adhérent introuvable")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(adherent, field, value)

    db.commit()
    db.refresh(adherent)

    return AdherentCreateOut(
        id=adherent.id,
        club_id=adherent.club_id,
        date_creation=adherent.date_creation,
        nom=adherent.nom,
        prenom=adherent.prenom,
        date_naissance=adherent.date_naissance,
        genre=adherent.genre,
        email=adherent.email,
        telephone=adherent.telephone,
        actif=adherent.actif,
        categorie_id=adherent.categorie_id,
    )


# ------------------ Supprimer un adhérent ------------------
@router.delete("/adherents/{adherent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adherent(adherent_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    adherent = db.query(models.Adherent).filter(models.Adherent.id == adherent_id).first()
    if not adherent:
        raise HTTPException(status_code=404, detail="Adhérent introuvable")

    db.delete(adherent)
    db.commit()