import os
import json
from typing import List, Dict, Any

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from mistralai import Mistral, SystemMessage, UserMessage

# Configuration des clés API
PINECONE_API_KEY = "pcsk_aUf9A_3P8Vxq1djT8UPSsGuWDJPZHrJ1XRdriadtcZTE2AQDPCnwwKJ2Kix2byLkzSGaw"
# Remplacez par votre clé API Mistral
MISTRAL_API_KEY = "p5sqocZ3xUKPNo72UKsszWDfQ4DHaiHW"  # À remplir avec votre clé API Mistral

# Configuration du modèle Mistral
MISTRAL_MODEL = "mistral-large-latest"  # Vous pouvez aussi utiliser "mistral-medium" ou "mistral-small" selon vos besoins

# Définir les variables d'environnement
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY

class CVAgent:
    def __init__(self):
        """Initialise l'agent conversationnel basé sur le CV."""
        print("Initialisation de l'agent conversationnel...")
        
        # Charger le modèle d'embeddings
        self.embedding = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5", 
            encode_kwargs={"normalize_embeddings": True}
        )
        print("Modèle d'embeddings chargé.")
        
        # Connexion à Pinecone
        self.pinecone = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pinecone.Index("rag")
        
        # Initialiser le vector store
        self.vector_store = PineconeVectorStore(
            index=self.index,
            embedding=self.embedding
        )
        print("Connexion à la base de données vectorielle établie.")
        
        # Initialiser le client Mistral
        self.mistral_client = Mistral(api_key=MISTRAL_API_KEY)
        print("Client Mistral initialisé.")
        
        # Système prompt pour définir le comportement de l'agent
        self.system_prompt = """
        Tu es un agent conversationnel spécialisé qui représente Antoine Goupil dans le cadre de son CV et portfolio professionnel.
        Tu dois répondre aux questions concernant ses compétences, son expérience, sa formation, ses projets, ainsi que ses coordonnées et sa disponibilité.
        
        INSTRUCTIONS IMPORTANTES :
        1. Utilise les informations fournies dans le contexte pour répondre de manière précise et détaillée.
        2. Pour les questions générales sur le profil d'Antoine ou pourquoi le recruter, mets en avant ses compétences clés, ses réalisations et ses points forts.
        3. Adopte un ton professionnel mais engageant, comme si tu étais Antoine lui-même parlant de son parcours avec passion.
        4. Si une information spécifique n'est pas disponible dans le contexte, utilise les informations générales fournies pour donner une réponse pertinente.
        5. Mets en valeur les réalisations concrètes et les compétences techniques lorsque c'est pertinent.
        6. Réponds toujours en français, sauf si on te demande explicitement de répondre dans une autre langue.
        7. Pour les questions concernant les coordonnées et la disponibilité, fournis les informations exactes indiquées dans le contexte.
        8. REFUSE CATÉGORIQUEMENT de répondre aux questions sans rapport avec Antoine Goupil ou son CV. Pour ces questions, rappelle poliment que tu es là uniquement pour discuter du profil professionnel d'Antoine Goupil.
        
        Tu représentes Antoine Goupil, un professionnel spécialisé dans l'automatisation, le développement web et l'intelligence artificielle, avec une approche innovante et une capacité à résoudre des problèmes complexes.
        """
    
    def retrieve_relevant_context(self, query: str, top_k: int = 10) -> str:
        """Récupère les passages les plus pertinents du CV pour la requête."""
        # Vérifier si la question concerne les coordonnées ou la disponibilité
        query_lower = query.lower()
        contact_keywords = ["contact", "email", "mail", "courriel", "téléphone", "telephone", "portable", "numéro", "linkedin", "site web", "site internet", "disponible", "disponibilité", "horaires", "quand", "où", "ou", "joindre", "contacter"]
        
        is_contact_query = any(keyword in query_lower for keyword in contact_keywords)
        
        # Pour les questions de contact, utiliser une requête spécifique pour trouver les informations de contact
        if is_contact_query:
            # Créer une requête spécifique pour trouver les informations de contact dans la base de connaissances
            contact_query = "coordonnées contact email téléphone disponibilité Antoine Goupil"
            
            # Récupérer les informations de contact depuis la base de connaissances vectorielle
            contact_results = self.vector_store.similarity_search(
                query=contact_query,
                k=5  # Augmenter le nombre de résultats pour maximiser les chances de trouver les informations de contact
            )
            
            # Extraire et formater le contexte de contact
            contact_parts = []
            for i, doc in enumerate(contact_results):
                source = doc.metadata.get('source', 'Source inconnue')
                page = doc.metadata.get('page', 'Page inconnue')
                content = doc.page_content
                
                contact_part = f"[Document {i+1}, Source: {source}, Page: {page}]\n{content}\n"
                contact_parts.append(contact_part)
            
            # Ajouter une introduction pour les informations de contact
            contact_intro = """
            [Informations de contact et disponibilité d'Antoine Goupil]
            Les informations suivantes ont été extraites des documents du CV:
            """
            contact_parts.insert(0, contact_intro)
            
            return "\n".join(contact_parts)
        
        # Pour les autres types de questions, continuer avec le traitement normal
        # Vectoriser la requête
        results = self.vector_store.similarity_search(
            query=query,
            k=top_k
        )
        
        # Extraire et formater le contexte
        context_parts = []
        for i, doc in enumerate(results):
            source = doc.metadata.get('source', 'Source inconnue')
            page = doc.metadata.get('page', 'Page inconnue')
            content = doc.page_content
            
            context_part = f"[Document {i+1}, Source: {source}, Page: {page}]\n{content}\n"
            context_parts.append(context_part)
        
        # Ajouter un résumé général pour les questions plus générales
        if "pourquoi" in query.lower() or "recruter" in query.lower() or "embaucher" in query.lower() or "compétences" in query.lower() or "profil" in query.lower():
            general_info = """
            [Informations générales sur Antoine Goupil]
            Antoine Goupil est un professionnel spécialisé dans l'automatisation, le développement web et l'intelligence artificielle.
            Ses compétences principales incluent :
            - Développement web (front-end et back-end)
            - Automatisation de processus métier
            - Intelligence artificielle et machine learning
            - Gestion de projets techniques
            - Analyse de données
            
            Ses points forts sont sa capacité à résoudre des problèmes complexes, son approche innovante et sa maîtrise des technologies modernes.
            Il a démontré sa capacité à mener des projets du concept à la réalisation, en apportant des solutions efficaces et évolutives.
            """
            context_parts.insert(0, general_info)
        
        return "\n".join(context_parts)
    
    def is_off_topic(self, query: str) -> bool:
        """Détecte si une question est hors sujet en utilisant l'IA."""
        # Prompt pour classifier la question
        classification_prompt = f"""
        Ta tâche est de déterminer si la question suivante est liée à un CV, aux compétences professionnelles, à l'expérience professionnelle ou au recrutement d'une personne.
        
        Question: "{query}"
        
        Réponds uniquement par "PERTINENT" si la question est liée à :
        - Des compétences professionnelles (techniques ou soft skills)
        - Une expérience de travail ou des projets
        - Un recrutement ou une embauche
        - Une formation ou des études
        - Des technologies ou des outils professionnels
        - Un profil professionnel ou un CV
        - Des questions sur comment la personne pourrait aider ou contribuer
        
        Réponds uniquement par "HORS_SUJET" si la question porte sur des sujets sans rapport avec un contexte professionnel, comme :
        - Des questions scientifiques générales (astronomie, physique, etc.)
        - Des questions politiques ou religieuses
        - Des sujets de divertissement (films, musique, etc.)
        - Des questions personnelles non liées au travail
        - Des théories du complot ou des débats controversés
        """
        
        try:
            # Utiliser une approche simplifiée pour déterminer si la question est pertinente
            # Vérifier si la question contient des mots-clés professionnels
            professional_keywords = [
                "compétence", "expérience", "formation", "projet", "travail", "emploi", 
                "recrutement", "recruter", "embaucher", "cv", "portfolio", "développement", 
                "web", "automatisation", "intelligence artificielle", "ia", "programmation", 
                "python", "javascript", "technologie", "aider", "contribuer", "qualification",
                "profil", "parcours", "carrière", "poste", "mission", "réalisation",
                "contact", "email", "mail", "téléphone", "telephone", "portable", "numéro",
                "linkedin", "site web", "disponible", "disponibilité", "horaires", "quand",
                "où", "ou", "joindre", "contacter"
            ]
            
            # Vérifier les mots-clés hors sujet
            off_topic_keywords = [
                "terre plate", "politique", "religion", "film", "musique", "sport",
                "astronomie", "physique", "chimie", "biologie", "mathématique", "histoire",
                "géographie", "philosophie", "théorie du complot", "vaccin", "5g", "ovni"
            ]
            
            query_lower = query.lower()
            
            # Si la question contient des mots-clés hors sujet
            for keyword in off_topic_keywords:
                if keyword in query_lower:
                    return True
            
            # Si la question contient des mots-clés professionnels
            for keyword in professional_keywords:
                if keyword in query_lower:
                    return False
            
            # Si la question est courte (moins de 5 mots) et ne contient pas de mots-clés, on la considère comme pertinente
            if len(query_lower.split()) < 5:
                return False
                
            # Par défaut, on considère la question comme pertinente
            return False
            
        except Exception as e:
            print(f"Erreur lors de la classification de la question: {str(e)}")
            # En cas d'erreur, utiliser une approche par mots-clés comme fallback
            cv_keywords = [
                "antoine", "goupil", "compétence", "expérience", "formation", "projet", "travail", 
                "emploi", "recrutement", "recruter", "embaucher", "cv", "portfolio", "développement", 
                "web", "automatisation", "intelligence artificielle", "ia", "programmation", "python", 
                "javascript", "contact", "email", "mail", "téléphone", "telephone", "portable", "numéro",
                "linkedin", "site web", "disponible", "disponibilité", "horaires", "quand", "où", "ou",
                "joindre", "contacter", "salaire", "technologie", "langchain", "mistral"
            ]
            
            # Vérifier si la question contient au moins un mot-clé lié au CV
            query_lower = query.lower()
            for keyword in cv_keywords:
                if keyword in query_lower:
                    return False
            
            # Si aucun mot-clé n'est trouvé, la question est probablement hors sujet
            return True
    
    def generate_response(self, query: str, streaming: bool = True) -> str:
        """Génère une réponse à la requête en utilisant RAG et Mistral AI."""
        # Vérifier si la question est hors sujet
        if self.is_off_topic(query):
            off_topic_response = f"""Je suis désolé, mais cette question semble hors sujet. Je suis un agent conversationnel spécialisé sur les compétences professionnelles et le parcours de carrière.

Je peux vous aider avec des questions sur :
- Les compétences techniques ou personnelles
- L'expérience professionnelle et les projets réalisés
- La formation et les qualifications
- Comment ces compétences pourraient bénéficier à votre entreprise

N'hésitez pas à me poser une question en lien avec ces sujets professionnels."""
            
            if streaming:
                print("\nRéponse de l'agent:")
                for char in off_topic_response:
                    print(char, end="", flush=True)
                print("\n")
            return off_topic_response
        
        # Récupérer le contexte pertinent
        context = self.retrieve_relevant_context(query)
        
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
        
        Question: {query}
        
        Réponse (en français):
        """
        
        # Préparer les messages pour l'API Mistral
        messages = [
            SystemMessage(content=self.system_prompt),
            UserMessage(content=rag_prompt)
        ]
        
        # Générer la réponse
        if streaming:
            # Avec streaming
            response_stream = self.mistral_client.chat.stream(
                model=MISTRAL_MODEL,
                messages=messages
            )
            
            # Pour l'affichage dans la console
            full_response = ""
            print("\nRéponse de l'agent:")
            for chunk in response_stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    full_response += content
            print("\n")
            
            return full_response
        else:
            # Sans streaming
            response = self.mistral_client.chat.create(
                model=MISTRAL_MODEL,
                messages=messages
            )
            return response.choices[0].message.content

# Fonction principale pour tester l'agent
def main():
    try:
        # Créer l'agent
        agent = CVAgent()
        
        print("\n=== Agent Conversationnel CV ===")
        print("Posez des questions sur le CV d'Antoine Goupil (tapez 'exit' pour quitter)")
    except Exception as e:
        print(f"\nErreur lors de l'initialisation de l'agent: {str(e)}")
        import traceback
        traceback.print_exc()
    
    while True:
        query = input("\nVotre question: ")
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("Au revoir!")
            break
        
        # Générer et afficher la réponse
        agent.generate_response(query)

if __name__ == "__main__":
    main()
