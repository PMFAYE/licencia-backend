import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.api.v1.routes.clubs import list_clubs

db = SessionLocal()
try:
    fake_user = {"role": "admin_federation", "club_id": None}
    clubs = list_clubs(db=db, current_user=fake_user)
    print("Success:", clubs)
except Exception as e:
    print(f"Error {type(e).__name__}: {e}")
finally:
    db.close()
