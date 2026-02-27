from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.db import models
from app.db.database import engine
from app.api.v1.routes import auth, users, licences, clubs, clubs_infos_type, federation, demande, adherents, notifications, ws, offres, devis

models.Base.metadata.create_all(bind=engine)

# Configuration CORS
origins = [
    "http://localhost:5173",      # ton frontend Vite/React
    "http://127.0.0.1:5173",      # au cas où tu utilises 127.0.0.1
    # Tu peux aussi ajouter "http://localhost:3000" si tu changes de port plus tard
]

app = FastAPI(title="FSBB API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],          # ou spécifie les méthodes : ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],          # ou liste les headers autorisés
)

app.mount("/home/pfaye/mvp/ged", StaticFiles(directory="/home/pfaye/mvp/ged"), name="uploads")
# Inclure les routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(licences.router)
app.include_router(clubs.router)
app.include_router(clubs_infos_type.router)
app.include_router(federation.router)
app.include_router(demande.router)
app.include_router(adherents.router)
app.include_router(notifications.router)
app.include_router(ws.router)
app.include_router(offres.router)
app.include_router(devis.router)