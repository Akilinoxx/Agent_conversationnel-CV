from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json

# Import de l'agent conversationnel
import sys
import os

# Ajouter le répertoire parent au chemin pour pouvoir importer cv_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from cv_agent import CVAgent

# Création du router FastAPI
router = APIRouter()

# Initialisation de l'agent (singleton)
agent = None

def get_agent():
    global agent
    if agent is None:
        agent = CVAgent()
    return agent

# Modèle de données pour la requête
class ChatRequest(BaseModel):
    query: str
    streaming: bool = True

# Modèle de données pour la réponse
class ChatResponse(BaseModel):
    response: str

# Route pour le chat en mode streaming
@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, background_tasks: BackgroundTasks):
    """Endpoint pour le chat en mode streaming"""
    agent = get_agent()
    
    if not request.query:
        raise HTTPException(status_code=400, detail="La requête ne peut pas être vide")
    
    # Fonction pour générer le flux de réponse
    async def generate():
        # Vérifier si la question est hors sujet
        if agent.is_off_topic(request.query):
            off_topic_response = f"""Je suis désolé, mais cette question semble hors sujet. Je suis un agent conversationnel spécialisé sur les compétences professionnelles et le parcours de carrière.

Je peux vous aider avec des questions sur :
- Les compétences techniques ou personnelles
- L'expérience professionnelle et les projets réalisés
- La formation et les qualifications
- Comment ces compétences pourraient bénéficier à votre entreprise

N'hésitez pas à me poser une question en lien avec ces sujets professionnels."""
            
            # Envoyer la réponse caractère par caractère pour simuler le streaming
            for char in off_topic_response:
                yield f"data: {json.dumps({'content': char})}\n\n"
                await asyncio.sleep(0.01)  # Petit délai pour simuler la génération
            
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
            return
        
        # Récupérer le contexte pertinent
        context = agent.retrieve_relevant_context(request.query)
        
        # Construire le prompt avec le contexte
        rag_prompt = f"""
        Pour répondre à la question suivante sur Antoine Goupil, utilise les informations du contexte fourni.
        
        Contexte:
        {context}
        
        INSTRUCTIONS POUR LA RÉPONSE:
        - Si la question porte sur les compétences, l'expérience ou les projets d'Antoine, fournis des détails précis basés sur le contexte.
        - Si la question est du type "pourquoi recruter Antoine" ou similaire, mets en avant ses compétences clés, ses réalisations et ce qui le distingue.
        - Adopte un ton professionnel mais engageant, comme si Antoine parlait de lui-même avec passion.
        - Mets en valeur les réalisations concrètes et les compétences techniques pertinentes.
        - Si une information spécifique n'est pas disponible, utilise les informations générales pour donner une réponse pertinente.
        
        Question: {request.query}
        
        Réponse (en français):
        """
        
        # Préparer les messages pour l'API Mistral
        messages = [
            {"role": "system", "content": agent.system_prompt},
            {"role": "user", "content": rag_prompt}
        ]
        
        # Générer la réponse avec streaming
        response_stream = agent.mistral_client.chat.stream(
            model="mistral-large-latest",
            messages=messages
        )
        
        # Envoyer la réponse au fur et à mesure
        for chunk in response_stream:
            content = chunk.data.choices[0].delta.content
            if content:
                yield f"data: {json.dumps({'content': content})}\n\n"
        
        # Indiquer que la génération est terminée
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

# Route pour le chat en mode non-streaming
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint pour le chat en mode non-streaming"""
    agent = get_agent()
    
    if not request.query:
        raise HTTPException(status_code=400, detail="La requête ne peut pas être vide")
    
    # Générer la réponse
    response = agent.generate_response(request.query, streaming=False)
    
    return ChatResponse(response=response)
