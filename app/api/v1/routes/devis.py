from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from app.db import models
from app.db.database import get_db
from app.schemas.devis_schema import DevisCreate, DevisResponse, DevisItemResponse, DevisStatusUpdate
from app.services.email_service import send_devis_confirmation

router = APIRouter(prefix="/devis", tags=["Devis"])


def generate_reference(db: Session) -> str:
    """Génère une référence unique pour le devis : DEV-2026-0001."""
    year = datetime.utcnow().year
    last_devis = (
        db.query(models.Devis)
        .filter(models.Devis.reference.like(f"DEV-{year}-%"))
        .order_by(models.Devis.id.desc())
        .first()
    )
    if last_devis:
        last_num = int(last_devis.reference.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"DEV-{year}-{new_num:04d}"


@router.post("", response_model=DevisResponse)
def create_devis(devis_in: DevisCreate, db: Session = Depends(get_db)):
    """Créer un devis (endpoint public) — envoie un email de confirmation."""
    # Créer le devis
    reference = generate_reference(db)
    devis = models.Devis(
        reference=reference,
        statut="nouveau",
        nom_contact=devis_in.nom_contact,
        email_contact=devis_in.email_contact,
        telephone_contact=devis_in.telephone_contact,
        nom_organisation=devis_in.nom_organisation,
        type_organisation=devis_in.type_organisation,
        message=devis_in.message,
    )
    db.add(devis)
    db.flush()  # pour obtenir l'id

    # Ajouter les items (offres choisies)
    offres_noms = []
    for offre_id in devis_in.offre_ids:
        offre = db.query(models.Offre).filter(models.Offre.id == offre_id).first()
        if offre:
            item = models.DevisItem(devis_id=devis.id, offre_id=offre.id)
            db.add(item)
            offres_noms.append(offre.nom)

    db.commit()
    db.refresh(devis)

    # Envoi email de confirmation (non bloquant)
    try:
        send_devis_confirmation(
            to_email=devis.email_contact,
            nom_contact=devis.nom_contact,
            reference=devis.reference,
            offres=offres_noms,
        )
    except Exception as e:
        print(f"[EMAIL] Erreur envoi email: {e}")

    # Construire la réponse
    return _devis_to_response(devis, db)


@router.get("", response_model=List[DevisResponse])
def list_devis(db: Session = Depends(get_db)):
    """Lister tous les devis (endpoint admin)."""
    devis_list = (
        db.query(models.Devis)
        .options(joinedload(models.Devis.items).joinedload(models.DevisItem.offre))
        .order_by(models.Devis.date_creation.desc())
        .all()
    )
    return [_devis_to_response(d, db) for d in devis_list]


@router.patch("/{devis_id}/statut", response_model=DevisResponse)
def update_devis_statut(devis_id: int, status_in: DevisStatusUpdate, db: Session = Depends(get_db)):
    """Changer le statut d'un devis (endpoint admin)."""
    devis = db.query(models.Devis).filter(models.Devis.id == devis_id).first()
    if not devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")

    valid_statuts = ["nouveau", "en_cours", "accepte", "refuse"]
    if status_in.statut not in valid_statuts:
        raise HTTPException(status_code=400, detail=f"Statut invalide. Valeurs possibles: {valid_statuts}")

    devis.statut = status_in.statut
    if status_in.statut in ["accepte", "refuse"]:
        devis.date_traitement = datetime.utcnow()

    db.commit()
    db.refresh(devis)
    return _devis_to_response(devis, db)


def _devis_to_response(devis: models.Devis, db: Session) -> DevisResponse:
    """Convertit un modèle Devis en DevisResponse."""
    items = []
    for item in devis.items:
        offre = db.query(models.Offre).filter(models.Offre.id == item.offre_id).first()
        items.append(DevisItemResponse(
            id=item.id,
            offre_id=item.offre_id,
            offre_nom=offre.nom if offre else None,
        ))

    return DevisResponse(
        id=devis.id,
        reference=devis.reference,
        statut=devis.statut,
        nom_contact=devis.nom_contact,
        email_contact=devis.email_contact,
        telephone_contact=devis.telephone_contact,
        nom_organisation=devis.nom_organisation,
        type_organisation=devis.type_organisation,
        message=devis.message,
        date_creation=devis.date_creation,
        date_traitement=devis.date_traitement,
        items=items,
    )
