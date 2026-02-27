from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, Query
from sqlalchemy.orm import Session, joinedload
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.db import models
from app.db.database import get_db
from app.core import security
from app.schemas.user_schema import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user_ws(
    websocket: WebSocket,
    token: str = Query(...)
):
    print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')
    try:
        payload = security.decode_access_token(token)
        print(payload)
        return payload
    except JWTError:
        await websocket.close(code=1008)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserResponse:
    print('AAAAAAAAAAAAAA')
    payload = security.decode_access_token(token)
    if not payload or "email" not in payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    print('AAAAAAAAAAAAAA')
    # 🔹 Chargement complet avec toutes les relations nécessaires
    user = (
        db.query(models.User)
        .options(
            joinedload(models.User.club),
            joinedload(models.User.federation),
            joinedload(models.User.ligue),
            joinedload(models.User.roles).joinedload(models.UserRole.role)
        )
        .filter(models.User.email == payload["email"])
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    role_name = user.roles[0].role.name if user.roles else user.role

    return {
            "id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email,
            "role": role_name,
            "club_id": user.club.id if user.club else None,
            "club": {
                "id": user.club.id,
                "nom": user.club.nom,
                "email": user.club.email,
                "adresse": user.club.adresse,
                "raison_sociale": user.club.raison_sociale,
                # ajoute les champs dont tu as besoin
            } if user.club else None,
            "federation": {
                "id": user.federation.id,
                "nom": user.federation.name
                } if user.federation else None,
            "ligue": {
                "id": user.ligue.id,
                "nom": user.ligue.name
                } if user.ligue else None,
        }


def admin_required(current_user=Depends(get_current_user)):
    if current_user['role'] != "admin_federation":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user=Depends(get_current_user)):
    """Renvoie les infos complètes de l'utilisateur connecté."""
    return current_user


@router.get("/invitations")
def list_invitations(db: Session = Depends(get_db), _: models.User = Depends(admin_required)):
    invitations = db.query(models.Invitation).all()
    return [
        {
            "id": inv.id,
            "email": inv.email,
            "club_id": inv.club_id,
            "role": inv.role,
            "used": inv.used,
            "expiration": inv.expires_at,
            "token": inv.token
        }
        for inv in invitations
    ]


@router.get("/all")
def list_users(db: Session = Depends(get_db), _: models.User = Depends(admin_required)):
    """Liste tous les utilisateurs (admin only)."""
    users = (
        db.query(models.User)
        .options(
            joinedload(models.User.club),
            joinedload(models.User.federation),
            joinedload(models.User.ligue),
        )
        .all()
    )

    return [
        {
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email,
            "role": user.roles[0].role.name if user.roles else user.role,
            "club": user.club.nom if user.club else None,
            "federation": user.federation.name if user.federation else None,
            "ligue": user.ligue.name if user.ligue else None,
        }
        for user in users
    ]
