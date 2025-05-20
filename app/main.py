from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys

# Import des routes
from app.api.routes import router as api_router

# Création de l'application FastAPI
app = FastAPI(
    title="Agent Conversationnel CV",
    description="API pour un agent conversationnel basé sur le CV d'Antoine Goupil",
    version="1.0.0"
)

# Configuration CORS pour permettre l'intégration avec le portfolio
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://akilinoxx.github.io",  # Domaine du portfolio
        "http://localhost:8000",        # Pour le développement local
        "http://127.0.0.1:8000"         # Pour le développement local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage des routes API
app.include_router(api_router, prefix="/api")

# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Route racine
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API de l'Agent Conversationnel CV d'Antoine Goupil"}

# Point d'entrée pour uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
