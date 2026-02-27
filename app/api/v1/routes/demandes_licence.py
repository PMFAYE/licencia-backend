from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
import app.schemas.demande_licence_schema as models
import app.db.models as schemas
from app.api.deps import get_current_user

router = APIRouter(prefix="/demandes_licence", tags=["demandes_licence"])

@router.post("/", response_model=schemas.DemandeLicenceRead)
def create_demande(demande_in: schemas.DemandeLicenceCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Créer la demande en brouillon
    demande = models.DemandeLicence(
        type_demande=demande_in.type_demande,
        nom=demande_in.nom,
        prenom=demande_in.prenom,
        date_naissance=demande_in.date_naissance,
        categorie_id=demande_in.categorie_id,
        club_id=user.club_id,
        statut=demande_in.statut or "brouillon",
    )
    db.add(demande)
    db.commit()
    db.refresh(demande)
    return demande

@router.patch("/{demande_id}/statut", response_model=schemas.DemandeLicenceRead)
def update_statut(demande_id: int, stat_in: schemas.DemandeLicenceUpdateStatut, db: Session = Depends(get_db), user=Depends(get_current_user)):
    dem = db.query(models.DemandeLicence).filter(models.DemandeLicence.id == demande_id).first()
    if not dem:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    # Vérifier les transitions autorisées selon le statut actuel
    old = dem.statut
    new = stat_in.statut

    # Exemple de logique simple de transitions
    allowed = {
        "brouillon": ["soumise"],
        "soumise": ["en_verification", "refusee"],
        "en_verification": ["validee", "refusee"],
        # une fois validé ou refusé, pas de retour
    }
    if new not in allowed.get(old, []):
        raise HTTPException(status_code=400, detail=f"Transition non autorisée {old} → {new}")

    dem.statut = new
    now = datetime.utcnow()
    if new == "soumise":
        dem.date_soumission = now
    elif new == "validee":
        dem.date_validation = now
    elif new == "refusee":
        dem.date_refus = now
        dem.commentaire_refus = stat_in.commentaire_refus

    db.commit()
    db.refresh(dem)
    return dem

@router.get("/{demande_id}", response_model=schemas.DemandeLicenceRead)
def get_demande(demande_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    dem = db.query(models.DemandeLicence).filter(models.DemandeLicence.id == demande_id).first()
    if not dem:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    # Optionnel : vérifier que l’utilisateur a le droit de voir
    return dem

@router.get("/", response_model=list[schemas.DemandeLicenceRead])
def list_demandes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Par exemple : retourner toutes les demandes du club de l’utilisateur
    return db.query(models.DemandeLicence).filter(models.DemandeLicence.club_id == user.club_id).all()
