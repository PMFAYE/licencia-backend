from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.db import models
from app.db.database import engine
from app.api.v1.routes import auth, users, licences, clubs, clubs_infos_type, federation, demande, adherents, notifications, ws, offres, devis
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS fsbb"))
    conn.commit()

models.Base.metadata.create_all(bind=engine)

import os

# Configuration CORS
production_origins = [
    "https://licencia-7a28e.firebaseapp.com",
    "https://licencia-7a28e.web.app",
    "https://licencia-vitrine.firebaseapp.com",
    "https://licencia-vitrine.web.app",
]
localhost_origins = [
     "http://localhost:5173",
     "http://localhost:5174",
]
env_origins = os.getenv("FRONTEND_URLS", "").split(",")
origins = list(set([url.strip() for url in production_origins + localhost_origins + env_origins if url.strip()]))

app = FastAPI(title="FSBB API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
print(f"DEBUG: Allowed Origins: {origins}")

import os

# Create the uploads directory if it doesn't exist
UPLOAD_DIR = os.getenv("UPLOAD_DIR") or "/tmp/ged"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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