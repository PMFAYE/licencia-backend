from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.schemas.demande_schema import DemandeCreate, DemandeOut, DemandeUpdate
from app.db import models
from app.api.v1.routes.users import get_current_user  # dépendance pour utilisateur connecté

router = APIRouter(prefix="/demandes", tags=["demandes"])

@router.post("/", response_model=DemandeOut)
def create_demande(demande_in: DemandeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Créer une demande
    db_demande = models.Demande(
        type=demande_in.type,
        statut="soumise",
        commentaires=demande_in.commentaires,
        utilisateur_id=current_user['id'],
        club_id=current_user['club_id'],
    )
    db.add(db_demande)
    db.commit()
    db.refresh(db_demande)
    return db_demande

@router.patch("/{demande_id}/statut", response_model=DemandeOut)
def update_statut(
    demande_id: int,
    stat_in: DemandeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_demande = db.query(models.Demande).filter(models.Demande.id == demande_id).first()
    if not db_demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    # 🔒 Vérification du rôle
    if current_user["role"] not in ["admin_federation", "admin_ligue"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits pour modifier le statut de cette demande"
        )

    ancien_statut = db_demande.statut
    nouveau_statut = stat_in.statut

    # ✅ Validation du statut
    statuts_valides = ["brouillon", "soumise", "en_verification", "validee", "refusee"]
    if nouveau_statut not in statuts_valides:
        raise HTTPException(status_code=400, detail=f"Statut '{nouveau_statut}' invalide")

    db_demande.statut = nouveau_statut
    db_demande.commentaires = stat_in.commentaires or db_demande.commentaires

    # 🔄 Dates automatiques selon le statut
    now = datetime.utcnow()
    if nouveau_statut == "validee":
        db_demande.date_validation = now
    elif nouveau_statut == "refusee":
        db_demande.date_refus = now
    elif nouveau_statut == "soumise":
        db_demande.date_soumission = now
    elif nouveau_statut == "en_verification":
        db_demande.date_modification = now

    # 🕓 Historique
    # historique = models.HistoriqueDemande(
    #     demande_id=demande_id,
    #     ancien_statut=ancien_statut,
    #     nouveau_statut=nouveau_statut,
    #     date_changement=now,
    #     modifie_par_id=current_user["id"]
    # )

    # db.add(historique)

    try:
        db.commit()
        db.refresh(db_demande)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return db_demande

@router.get("/{demande_id}")
def read_demande(demande_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_demande = (
        db.query(models.Demande)
        .options(
            joinedload(models.Demande.user),
            joinedload(models.Demande.club),
            joinedload(models.Demande.licence),
        )
        .filter(models.Demande.id == demande_id)
        .first()
    )
    if not db_demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    # tu peux vérifier que l'utilisateur appartient au même club ou a les droits
    return db_demande

@router.get("/")
def list_demandes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # selon rôle, tu filtres les demandes visibles
    if current_user['role'] == "admin_federation":
        data = (
            db.query(models.Demande)
            .options(
                joinedload(models.Demande.user),
                joinedload(models.Demande.club),
                joinedload(models.Demande.licence),
            )
            .all()
        )
    else:
        data = (
            db.query(models.Demande)
            .options(
                joinedload(models.Demande.user),
                joinedload(models.Demande.club),
                joinedload(models.Demande.licence),
            )
            .filter(models.Demande.club_id == current_user['club_id'])
            .all()
        )

    return data
