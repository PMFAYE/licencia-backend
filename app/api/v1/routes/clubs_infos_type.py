from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas.club_schema import ClubInfoTypeBase
from typing import List

router = APIRouter(
    prefix="/clubs_infos_type",
    tags=["Clubs Infos Type"]
)

@router.get("/", response_model=List[ClubInfoTypeBase])
def get_all_clubs_infos_type(db: Session = Depends(get_db)):
    return db.query(models.ClubInfoType).all()
