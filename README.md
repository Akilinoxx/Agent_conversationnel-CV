# Agent Conversationnel CV

Un agent conversationnel basé sur le CV d'Antoine Goupil, utilisant une approche RAG (Retrieval Augmented Generation) avec l'API Mistral AI.

## Fonctionnalités

- Répond aux questions sur les compétences, l'expérience, la formation et les projets d'Antoine Goupil
- Détecte et gère les questions hors sujet
- Fournit des réponses contextuelles basées sur le contenu du CV
- API REST pour l'intégration dans un portfolio ou un site web
- Interface de démonstration incluse

## Prérequis

- Python 3.9+
- Clé API Mistral AI
- Clé API Pinecone

## Installation

1. Clonez ce dépôt :
```bash
git clone <url-du-repo>
cd agent-conversationnel-cv
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez les variables d'environnement :
```bash
# Windows
set MISTRAL_API_KEY=votre_cle_api_mistral
set PINECONE_API_KEY=votre_cle_api_pinecone

# Linux/Mac
export MISTRAL_API_KEY=votre_cle_api_mistral
export PINECONE_API_KEY=votre_cle_api_pinecone
```

## Démarrage du serveur

Pour démarrer le serveur API :

```bash
cd app
uvicorn main:app --reload
```

Le serveur sera accessible à l'adresse http://localhost:8000.

## Utilisation de l'API

### Endpoints disponibles

- `GET /` : Page d'accueil de l'API
- `POST /api/chat` : Endpoint pour les requêtes de chat (non-streaming)
- `POST /api/chat/stream` : Endpoint pour les requêtes de chat en mode streaming (recommandé)

### Exemple de requête

```javascript
// Exemple avec fetch
fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        query: 'Quelles sont les compétences techniques d\'Antoine ?',
        streaming: false
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Intégration dans un portfolio

### Méthode 1 : Utilisation du script d'intégration

1. Ajoutez le script dans votre page HTML :
```html
<script src="http://localhost:8000/static/cv-chatbot.js"></script>
```

2. Ajoutez un conteneur pour le chatbot :
```html
<div id="cv-chatbot-container"></div>
```

3. Initialisez le chatbot :
```html
<script>
    document.addEventListener('DOMContentLoaded', function() {
        CVChatbot.init({
            apiUrl: 'http://localhost:8000/api',
            theme: 'light'  // ou 'dark'
        });
    });
</script>
```

### Méthode 2 : Intégration personnalisée

Vous pouvez également créer votre propre interface en utilisant directement les endpoints de l'API. Consultez le fichier `app/static/demo.html` pour un exemple d'implémentation.

## Page de démonstration

Une page de démonstration est disponible à l'adresse http://localhost:8000/static/demo.html après le démarrage du serveur.

## Structure du projet

```
agent-conversationnel-cv/
├── app/                      # Application principale
│   ├── api/                  # API REST
│   │   ├── __init__.py
│   │   └── routes.py         # Routes de l'API
│   ├── data/                 # Données du CV
│   ├── models/               # Modèles pour la base de données vectorielle
│   ├── static/               # Fichiers statiques
│   │   ├── cv-chatbot.js     # Script d'intégration
│   │   └── demo.html         # Page de démonstration
│   ├── utils/                # Utilitaires
│   └── main.py               # Point d'entrée de l'application
├── cv_agent.py               # Agent conversationnel
├── pdfloader.py              # Chargeur de PDF pour extraire le contenu du CV
└── README.md                 # Documentation
```

## Déploiement en production

Pour un déploiement en production, il est recommandé de :

1. Utiliser un serveur WSGI comme Gunicorn
2. Configurer un proxy inverse comme Nginx
3. Sécuriser les endpoints avec HTTPS
4. Limiter les requêtes par IP pour éviter les abus
5. Mettre à jour les paramètres CORS pour n'autoriser que votre domaine

Exemple de démarrage avec Gunicorn :
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## Personnalisation

Vous pouvez personnaliser l'agent en modifiant :

- Le contenu du CV dans le fichier de données
- Le prompt système dans `cv_agent.py`
- Les mots-clés pour la détection des questions hors sujet
- L'apparence du chatbot via les options du script d'intégration

## Licence

[Insérer votre licence ici]
