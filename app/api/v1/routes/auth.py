from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from app.db import models
from app.db.database import get_db
from app.schemas.user_schema import InvitationRequest, UserCreate, UserResponse
from app.core import security

router = APIRouter(prefix="/auth", tags=["Authentication"])


# 🔹 LOGIN
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print('AAAAAAAAAAAAAA')
    user = (
        db.query(models.User)
        .options(
            joinedload(models.User.club),
            joinedload(models.User.federation),
            joinedload(models.User.ligue),
        )
        .filter(models.User.email == form_data.username)
        .first()
    )
    print(form_data.password)

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    
    if getattr(user, "is_active", None) is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ce compte est désactivé. Veuillez contacter l'administrateur.")

    print('BBBBBBBBBBBBB')
    access_token = security.create_access_token({
            "id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email,
            "role": user.role,
            "club_id": user.club.id if user.club else None,
            "club": {
                "id": user.club.id,
                "nom": user.club.nom,
                "email": user.club.email,
                "adresse": user.club.adresse,
                "raison_sociale": user.club.raison_sociale,
                # ajoute les champs dont tu as besoin
            } if user.club else None,
            "federation": user.federation.name if user.federation else None,
            "ligue": user.ligue.name if user.ligue else None,
        })
    print(access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# 🔹 CRÉER UNE INVITATION
@router.post("/create")
def create_invitation(invite: InvitationRequest, db: Session = Depends(get_db)):
    token = security.create_access_token(
        {
            "email": invite.email,
            "role": invite.role,
            "club_id": invite.club_id,
        },
        expires_delta=timedelta(hours=24),
    )
    invitation = models.Invitation(
        token=token,
        email=invite.email,
        role=invite.role,
        club_id=invite.club_id,
        federation_id=invite.federation_id,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    from app.services import email_service
    # URL de production du frontend
    frontend_url = "https://licencia-7a28e.firebaseapp.com"
    invitation_link = f"{frontend_url}/register?token={token}"

    try:
        email_service.send_invitation_email(
            to_email=invite.email,
            invitation_link=invitation_link,
            role=invite.role
        )
    except Exception as e:
        print(f"Failed to send email: {e}")
        # On continue quand même la création de l'invitation en DB
        # ou on pourrait lever une erreur si on veut que l'envoi soit bloquant
        pass

    return {
        "id": invitation.id,
        "email": invitation.email,
        "club_id": invitation.club_id,
        "role": invitation.role,
        "used": getattr(invitation, "used", False),
        "expiration": invitation.expires_at.isoformat(),
        "token": token,
        "invitation_link": invitation_link
    }


# 🔹 ENREGISTREMENT VIA INVITATION
@router.post("/register")
def register_with_invite(user_in: UserCreate, db: Session = Depends(get_db)):
    invitation = (
        db.query(models.Invitation)
        .filter(models.Invitation.token == user_in.token)
        .first()
    )

    if not invitation or not invitation.is_valid():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien d'invitation invalide ou expiré")

    if user_in.email != invitation.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ne correspond pas à l'invitation")

    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email déjà utilisé")

    hashed_password = security.hash_password(user_in.password)
    print(invitation)
    print(user_in)
    new_user = models.User(
        nom=user_in.nom,
        prenom=user_in.prenom,
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role,
        club_id=user_in.club_id,
        federation_id=user_in.federation_id,
    )

    db.add(new_user)
    invitation.used = True
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/invitation_by_token")
def get_invitation(token: str, db: Session = Depends(get_db)):

    invitation = (
        db.query(models.Invitation)
        .options(joinedload(models.Invitation.club))
        .filter(models.Invitation.token == token)
        .first()
    )
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation non trouvée ou invalide")
    return {
        "id": invitation.id,
        "email": invitation.email,
        "club_id": invitation.club_id,
        "club_nom": invitation.club.nom if invitation.club else None,
        "federation_id": invitation.federation_id,
        "role": invitation.role,
        "used": getattr(invitation, "used", False),
        "expiration": invitation.expires_at.isoformat()
    }