from app.services.notification_service import notify_user
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.db import models
from app.db.database import get_db
from app.schemas.licence_schema import (
    LicenceCreate, LicenceUpdate, LicenceResponse, LicenceSubmit, StatutUpdateSchema
)
from app.api.v1.routes.users import get_current_user
import random, string

router = APIRouter(prefix="/licences/demandes_licence", tags=["Licences"])


# ------------------ Utils ------------------
def admin_required(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin_federation":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs.")
    return current_user


def get_current_saison(db: Session, federation_id: int):
    return db.query(models.Saison).filter(
        models.Saison.federation_id == federation_id, models.Saison.active == True
    ).first()


def get_licence_or_404(licence_id: int, db: Session):
    licence = (
        db.query(models.Licence)
        .options(
            joinedload(models.Licence.fichiers).joinedload(models.Fichier.type),
            joinedload(models.Licence.categorie),
            joinedload(models.Licence.adherent),
            joinedload(models.Licence.club),
        )
        .filter(models.Licence.id == licence_id)
        .first()
    )
    if not licence:
        raise HTTPException(status_code=404, detail="Licence non trouvée.")
    return licence


def generer_numero_licence():
    lettres_chiffres = string.ascii_uppercase + string.digits
    return "LC" + "".join(random.choices(lettres_chiffres, k=6))


# ------------------ Création ------------------
@router.post("/", response_model=LicenceResponse, status_code=201)
def create_licence(data: LicenceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user['club_id'] != data.club_id:
        raise HTTPException(status_code=403, detail="Accès interdit à ce club.")

    if not current_user.get("federation"):
        raise HTTPException(status_code=403, detail="Aucune fédération assignée.")

    saison_active = get_current_saison(db, current_user['federation']['id'])
    if not saison_active:
        raise HTTPException(status_code=400, detail="Aucune saison active.")

    # Chercher ou créer l'adhérent
    adherent = None
    if data.adherent:
        adherent = db.query(models.Adherent).filter(models.Adherent.id == data.adherent).first()
        if not adherent:
            raise HTTPException(status_code=404, detail="Adhérent introuvable.")
    else:
        adherent = db.query(models.Adherent).filter(
            models.Adherent.nom.ilike(data.nom.strip()),
            models.Adherent.prenom.ilike(data.prenom.strip()),
            models.Adherent.date_naissance == data.date_naissance,
            models.Adherent.club_id == data.club_id
        ).first()
        if not adherent:
            adherent = models.Adherent(
                nom=data.nom.strip(),
                prenom=data.prenom.strip(),
                date_naissance=data.date_naissance,
                club_id=data.club_id,
                categorie_id=data.categorie_id,
                actif=True
            )
            db.add(adherent)
            db.commit()
            db.refresh(adherent)

    # Créer licence
    licence = models.Licence(
        nom=data.nom.strip(),
        prenom=data.prenom.strip(),
        date_naissance=data.date_naissance,
        categorie_id=data.categorie_id,
        club_id=data.club_id,
        type_demande=data.type_demande,
        statut="brouillon",
        adherent_id=adherent.id,
        saison_id=saison_active.id,
        date_creation=datetime.utcnow()
    )

    db.add(licence)
    try:
        db.commit()
        db.refresh(licence)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Licence déjà existante pour cet adhérent cette saison.")

    return LicenceResponse(
        id=licence.id,
        numero=licence.numero,
        nom=licence.nom,
        prenom=licence.prenom,
        date_naissance=licence.date_naissance,
        categorie=licence.categorie.nom if licence.categorie else None,
        statut=licence.statut,
        documents=[],
        motif_rejet=None,
        club_id=licence.club_id,
        date_creation=licence.date_creation
    )


# ------------------ Soumission ------------------
@router.post("/{licence_id}/submit", response_model=LicenceResponse)
def submit_licence(licence_id: int, _: LicenceSubmit, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    licence = get_licence_or_404(licence_id, db)
    if licence.club_id != current_user['club_id']:
        raise HTTPException(status_code=403, detail="Accès interdit.")
    if licence.statut != "brouillon":
        raise HTTPException(status_code=400, detail="Licence déjà soumise.")

    licence.statut = "soumise"
    licence.date_soumission = datetime.utcnow()
    db.commit()
    db.refresh(licence)
    return licence


# ------------------ Validation ------------------
@router.post("/{licence_id}/valider", response_model=LicenceResponse)
async def validate_licence(licence_id: int, db: Session = Depends(get_db), current_user=Depends(admin_required)):
    licence = get_licence_or_404(licence_id, db)
    licence.statut = "validée"
    licence.numero = generer_numero_licence()
    licence.date_validation = datetime.utcnow()
    db.commit()
    db.refresh(licence)
    return licence


# ------------------ Rejet ------------------
@router.post("/{licence_id}/rejeter", response_model=LicenceResponse)
def reject_licence(licence_id: int, motif: str = Form(...), db: Session = Depends(get_db), current_user=Depends(admin_required)):
    licence = get_licence_or_404(licence_id, db)
    licence.statut = "rejetée"
    licence.motif_rejet = motif
    licence.date_refus = datetime.utcnow()
    db.commit()
    db.refresh(licence)
    return licence


# ------------------ Modifier licence ------------------
@router.put("/{licence_id}", response_model=LicenceResponse)
def update_licence(licence_id: int, data: LicenceUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    licence = get_licence_or_404(licence_id, db)
    if licence.club_id != current_user['club_id']:
        raise HTTPException(status_code=403, detail="Accès interdit.")
    if licence.statut not in ["brouillon", "en attente"]:
        raise HTTPException(status_code=400, detail="Licence non modifiable à ce stade.")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(licence, key, value)

    db.commit()
    db.refresh(licence)
    return licence


# ------------------ Supprimer licence ------------------
@router.delete("/{licence_id}", status_code=204)
def delete_licence(licence_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    licence = get_licence_or_404(licence_id, db)
    if licence.club_id != current_user['club_id']:
        raise HTTPException(status_code=403, detail="Accès interdit.")
    db.delete(licence)
    db.commit()


# ------------------ Patch statut ------------------
@router.patch("/{licence_id}/statut")
async def update_statut(licence_id: int, data: StatutUpdateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    licence = get_licence_or_404(licence_id, db)
    if licence.club_id != current_user['club_id'] and current_user['role'] not in ["admin_ligue", "admin_federation"]:
        raise HTTPException(status_code=403, detail="Accès interdit.")
    licence.statut = data.statut
    db.commit()
    db.refresh(licence)
    if data.statut == "validee":
        await notify_user(
            db,
            user_id=current_user["id"],
            titre="Licence validée",
            message=f"La licence de {licence.nom} {licence.prenom} a été validée",
            type="licence",
            lien=f"/clubs/{licence.club_id}/licences?status=validee"
        )
    return {"id": licence.id, "statut": licence.statut, "message": "Statut mis à jour avec succès."}


# ------------------ Liste licences ------------------
@router.get("/", response_model=List[LicenceResponse])
def get_licences(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    club_id: Optional[int] = None,
    statut: Optional[str] = None,
    saison_id: Optional[int] = None,
    adherent_id: Optional[int] = None,
):
    query = db.query(models.Licence).options(
        joinedload(models.Licence.categorie),
        joinedload(models.Licence.club),
        joinedload(models.Licence.adherent),
        joinedload(models.Licence.fichiers).joinedload(models.Fichier.type),
    )

    if current_user["role"] == "admin_federation":
        if not current_user.get("federation"):
            return []
        federation_id = current_user["federation"]["id"]
        print(federation_id)
        query = query.join(models.Saison).filter(models.Saison.federation_id == federation_id)
    elif current_user["club_id"]:
        query = query.filter(models.Licence.club_id == current_user["club_id"])
    else:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")

    if club_id:
        query = query.filter(models.Licence.club_id == club_id)
    if statut:
        query = query.filter(models.Licence.statut == statut)
    if saison_id:
        query = query.filter(models.Licence.saison_id == saison_id)
    if adherent_id:
        query = query.filter(models.Licence.adherent_id == adherent_id)

    licences = query.order_by(models.Licence.date_creation.desc()).all()

    return [
        LicenceResponse(
            id=l.id,
            numero=l.numero,
            nom=l.nom,
            prenom=l.prenom,
            date_naissance=l.date_naissance,
            categorie=l.categorie.nom if l.categorie else None,
            statut=l.statut,
            documents=[{"id": f.id, "nom_fichier": f.nom_fichier, "type": f.type.nom, "chemin": f.chemin} for f in l.fichiers] if l.fichiers else [],
            motif_rejet=l.commentaire_refus,
            club_id=l.club_id,
            date_creation=l.date_creation,
        )
        for l in licences
    ]


# ------------------ Détail licence ------------------
@router.get("/{licence_id}", response_model=LicenceResponse)
def get_licence(licence_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    licence = get_licence_or_404(licence_id, db)

    # Vérification droits d'accès
    user_role = current_user.get("role")
    if user_role == "admin_federation":
        if not current_user.get("federation"):
            raise HTTPException(status_code=403, detail="Aucune fédération assignée.")
        federation_id = current_user["federation"]["id"]
        if licence.saison.federation_id != federation_id:
            raise HTTPException(status_code=403, detail="Accès interdit à cette fédération.")
    elif current_user.get("club_id") != licence.club_id:
        raise HTTPException(status_code=403, detail="Accès interdit à ce club.")

    return LicenceResponse(
        id=licence.id,
        numero=licence.numero,
        nom=licence.nom,
        prenom=licence.prenom,
        date_naissance=licence.date_naissance,
        categorie=licence.categorie.nom if licence.categorie else None,
        statut=licence.statut,
        documents=[{"id": f.id, "nom_fichier": f.nom_fichier, "type": f.type.nom if f.type else None, "chemin": f.chemin} for f in licence.fichiers] if licence.fichiers else [],
        motif_rejet=licence.commentaire_refus,
        club_id=licence.club_id,
        date_creation=licence.date_creation,
    )


@router.post("/{licence_id}/upload")
async def upload_fichier(
    licence_id: int,
    org_id: int = Form(...),
    club_id: int = Form(...),
    file: UploadFile = File(...),
    type: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    licence = get_licence_or_404(licence_id, db)

    # Vérification des droits
    if licence.club_id != current_user['club_id'] and current_user['role'] != "admin_federation":
        raise HTTPException(status_code=403, detail="Accès interdit.")

    # Vérifier le type de fichier
    type_obj = db.query(models.TypeFichier).filter(models.TypeFichier.nom == type).first()
    if not type_obj:
        raise HTTPException(status_code=400, detail="Type de fichier invalide.")

    # Répertoire sécurisé
    import os
    upload_dir = os.getenv("UPLOAD_DIR", "/tmp/ged")
    base_path = Path(f"{upload_dir}/{org_id}/{club_id}/{type}")
    base_path.mkdir(parents=True, exist_ok=True)


    # Création en base
    nouveau_fichier = models.Fichier(
        nom_fichier=file.filename,
        chemin=str(base_path),
        taille=0,
        id_licence=licence_id,
        id_type=type_obj.id,
        date_upload=datetime.utcnow()
    )
    db.add(nouveau_fichier)
    db.commit()
    db.refresh(nouveau_fichier)

    # Nom de fichier unique
    filename = f"{nouveau_fichier.id}"
    filepath = base_path / filename

    # Écriture du fichier
    with open(filepath, "wb") as f:
        contents = await file.read()
        f.write(contents)

    return {"message": "Fichier uploadé avec succès.", "fichier_id": nouveau_fichier.id}
