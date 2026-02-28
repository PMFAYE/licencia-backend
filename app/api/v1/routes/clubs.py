# app/api/v1/routes/clubs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from sqlalchemy import func, distinct
from datetime import date

from app.db import models
from app.db.database import get_db
from app.schemas.club_schema import ClubOut, ClubDetail, ClubCreate
from app.api.v1.routes.users import get_current_user

router = APIRouter(prefix="/clubs", tags=["Clubs"])


# 🟢 Lister tous les clubs (admin ou user)
@router.get("/", response_model=List[ClubOut])
def list_clubs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clubs = db.query(models.Club).all()
    return clubs


# 🔎 Obtenir les détails d’un club
@router.get("/{club_id}", response_model=ClubDetail)
def get_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Si user est admin → accès à tout
    # print(current_user)
    if current_user['role'] != "admin_federation" and current_user['club_id'] != club_id:
        raise HTTPException(status_code=403, detail="Accès interdit à ce club")

    club = (
        db.query(models.Club)
        .filter(models.Club.id == club_id)
        .first()
    )
    if not club:
        raise HTTPException(status_code=404, detail="Club non trouvé")

    return club


# 🟠 Créer un club (admin uniquement)
@router.post("/", response_model=ClubOut)
def create_club(
    club_data: ClubCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin_federation":
        raise HTTPException(status_code=403, detail="Seul un administrateur peut créer un club")

    # ✅ Vérifie que la fédération existe

    federation = db.query(models.Federation).filter_by(id=club_data.federation_id).first()

    if not federation:
        raise HTTPException(status_code=404, detail="Fédération non trouvée")

    # ✅ Vérifie si le club existe déjà (optionnel)
    existing_club = db.query(models.Club).filter(models.Club.email == club_data.email).first()
    if existing_club:
        raise HTTPException(status_code=400, detail="Un club avec cet email existe déjà")

    # ✅ Création du club

    club = models.Club(**club_data.dict())
    db.add(club)
    db.commit()
    db.refresh(club)

    return club


# 🟣 Modifier un club
@router.put("/{club_id}", response_model=ClubOut)
def update_club(
    club_data: ClubOut,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    club_id = club_data.id
    club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club non trouvé")

    if current_user['role'] != "admin_federation" and current_user.get('club_id') != club_id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    for key, value in club_data.dict(exclude_unset=True).items():
        setattr(club, key, value)

    db.commit()
    db.refresh(club)
    return club


# 🔴 Supprimer un club (admin uniquement)
@router.delete("/{club_id}")
def delete_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user['role'] != "admin_federation":
        raise HTTPException(status_code=403, detail="Seul un administrateur peut supprimer un club")

    club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club non trouvé")

    db.delete(club)
    db.commit()
    return {"message": "Club supprimé"}


@router.get("/{club_id}/infos")
def get_club_infos(club_id: int, db: Session = Depends(get_db)):
    infos = (
        db.query(models.ClubInfo, models.ClubInfoType)
        .join(models.ClubInfoType, models.ClubInfo.id_type == models.ClubInfoType.id)
        .filter(models.ClubInfo.club_id == club_id)
        .all()
    )
    return [
        {
            "id": i.ClubInfoType.id, 
            "libelle": i.ClubInfoType.valeur, 
            "valeur": i.ClubInfo.valeur
        } for i in infos]


@router.put("/{club_id}/infos")
def update_club_infos(
    club_id: int,
    data: list[dict],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user['role'] != "admin_federation" and current_user.get('club_id') != club_id:
        raise HTTPException(status_code=403, detail="Non autorisé")

    for item in data:
        info = (
            db.query(models.ClubInfo)
            .filter(models.ClubInfo.club_id == club_id, models.ClubInfo.id_type == item["id_info_type"])
            .first()
        )
        if info:
            info.valeur = item["valeur"]
        else:
            db.add(models.ClubInfo(club_id=club_id, id_type=item["id_info_type"], valeur=item["valeur"]))

    db.commit()
    return {"message": "Infos mises à jour"}


@router.get("/clubs_infos_type")
def get_all_infos_types(db: Session = Depends(get_db)):
    types = db.query(models.ClubInfoType).all()
    return types


@router.get("/{club_id}/stats")
def get_club_stats(
    club_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Sécurité : admin fédération ou club lui-même
    if current_user["role"] != "admin_federation" and current_user["club_id"] != club_id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    # Vérifier club
    club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club non trouvé")

    # Saison courante
    saison_courante = (
        db.query(models.Saison)
        .filter(models.Saison.active == True)
        .first()
    )

    if not saison_courante:
        raise HTTPException(status_code=400, detail="Aucune saison active")

    # Licences saison courante
    licences_saison = (
        db.query(models.Licence)
        .filter(models.Licence.club_id == club_id)
        .filter(models.Licence.saison_id == saison_courante.id)
    )

    licences_valides = licences_saison.filter(
        models.Licence.statut == "validee"
    ).count()

    licences_attente = licences_saison.filter(
        models.Licence.statut == "soumise"
    ).count()

    licences_refusees = licences_saison.filter(
        models.Licence.statut == "refusee"
    ).count()

    # Adhérents distincts
    adherents = (
        db.query(distinct(models.Licence.adherent_id))
        .filter(models.Licence.club_id == club_id)
        .filter(models.Licence.saison_id == saison_courante.id)
        .count()
    )

    # Licences par catégorie
    par_categorie = (
        db.query(
            models.Categorie.nom.label("categorie"),
            func.count(models.Licence.id).label("total")
        )
        .join(models.Licence, models.Licence.categorie_id == models.Categorie.id)
        .filter(models.Licence.club_id == club_id)
        .filter(models.Licence.saison_id == saison_courante.id)
        .filter(models.Licence.statut == "validee")
        .group_by(models.Categorie.nom)
        .all()
    )

    licences_par_categorie = [
        {"categorie": c.categorie, "total": c.total}
        for c in par_categorie
    ]

    # Taux de renouvellement
    saison_precedente = (
        db.query(models.Saison)
        .filter(models.Saison.id != saison_courante.id)
        .order_by(models.Saison.date_debut.desc())
        .first()
    )

    taux_renouvellement = "0%"

    if saison_precedente:
        anciens = (
            db.query(distinct(models.Licence.adherent_id))
            .filter(models.Licence.club_id == club_id)
            .filter(models.Licence.saison_id == saison_precedente.id)
            .filter(models.Licence.statut == "validee")
        )

        nouveaux = (
            db.query(distinct(models.Licence.adherent_id))
            .filter(models.Licence.club_id == club_id)
            .filter(models.Licence.saison_id == saison_courante.id)
            .filter(models.Licence.statut == "validee")
        )

        total_anciens = anciens.count()
        renouveles = anciens.intersect(nouveaux).count()

        if total_anciens > 0:
            taux = round((renouveles / total_anciens) * 100)
            taux_renouvellement = f"{taux}%"

    # Réponse API
    return {
        "adherents": adherents,
        "licencesValides": licences_valides,
        "licencesEnAttente": licences_attente,
        "licencesExpirees": licences_refusees,
        "tauxRenouvellement": taux_renouvellement,
        "parCategorie": licences_par_categorie
    }