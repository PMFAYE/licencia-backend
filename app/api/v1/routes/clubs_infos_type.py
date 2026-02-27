from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models

router = APIRouter(
    prefix="/clubs_infos_type",
    tags=["Clubs Infos Type"]
)

@router.get("/")
def get_all_clubs_infos_type(db: Session = Depends(get_db)):
    return db.query(models.ClubInfoType).all()
