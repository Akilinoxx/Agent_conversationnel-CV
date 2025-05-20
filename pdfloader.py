import os
import glob

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import NotFoundException
from langchain_pinecone import PineconeVectorStore

# Initialisation du loader de document pour charger un fichier PDF
documents = []

for file in glob.glob("C:/Users/a.goupil/OneDrive - BAW SAS/Bureau/Agent_conversationnel CV/PDFs_CV/*.pdf"):
    try:
        loader = PyPDFLoader(file)  # Retourne une liste de document (un pour chaque page)
        documents += loader.load()
    except Exception:
        print(f"Erreur survenue pour le fichier '{file}'.")

# Afficher le nombre de documents chargés
print(f"Nombre total de documents (pages) chargés: {len(documents)}")

# Afficher un aperçu du premier document
if documents:
    print("\nAperçu du premier document (première page):")
    print(f"Source: {documents[0].metadata['source']}")
    print(f"Page: {documents[0].metadata['page']}")
    print(f"Contenu (premiers 200 caractères): {documents[0].page_content[:200]}...")

# Initialisation du séparateur de texte avec des paramètres spécifiques pour diviser le texte
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,  # Taille maximale des morceaux de texte
    chunk_overlap=60,  # Chevauchement entre les morceaux pour garder le contexte
    length_function=len,  # Fonction pour calculer la longueur des morceaux
    separators=["\n\n", "\n"]  # Séparateurs utilisés pour diviser le texte en morceaux
)

# Division du document en morceaux (chunks)
chunks = text_splitter.split_documents(documents=documents)

# Affichage du nombre de morceaux créés à partir du document PDF
print(f"\n{len(chunks)} chunks ont été créés par le splitter à partir des documents PDF.")

# Afficher un aperçu du premier chunk
if chunks:
    print("\nAperçu du premier chunk:")
    print(f"Source: {chunks[0].metadata['source']}")
    print(f"Page: {chunks[0].metadata['page']}")
    print(f"Contenu: {chunks[0].page_content[:150]}...")

# Création des embeddings
print("\nChargement du modèle d'embeddings...")
try:
    # Charger le modèle d'encodage de texte BAAI/bge-small-en-v1.5 de HuggingFace
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5", encode_kwargs={"normalize_embeddings": True})
    print("Modèle d'embeddings chargé avec succès!")
    
    # Créer un exemple d'embedding pour vérifier que tout fonctionne
    if chunks:
        sample_embedding = embedding.embed_query(chunks[0].page_content[:100])
        print(f"\nDimension de l'embedding: {len(sample_embedding)}")
        print(f"Exemple des 5 premières valeurs de l'embedding: {sample_embedding[:5]}")
        
    # Création de l'index Pinecone
    print("\nCréation de l'index Pinecone...")
    
    #Remplacer par votre clé API Pinecone
    PINECONE_API_KEY = "pcsk_aUf9A_3P8Vxq1djT8UPSsGuWDJPZHrJ1XRdriadtcZTE2AQDPCnwwKJ2Kix2byLkzSGaw" # Vous devrez fournir votre clé API Pinecone ici
    
    if not PINECONE_API_KEY:
        print("ATTENTION: Aucune clé API Pinecone n'a été fournie. L'index ne sera pas créé.")
    else:
        try:
            # Initialisation du client Pinecone
            pinecone = Pinecone(api_key=PINECONE_API_KEY)
            
            # Vérifier si l'index existe déjà, sinon le créer
            try:
                pinecone.describe_index("rag")
                print("L'index 'rag' existe déjà.")
            except NotFoundException:
                # Créer un index nommé "rag" de dimension 384
                pinecone.create_index("rag", dimension=384, spec=ServerlessSpec(cloud="aws", region="us-east-1"))
                print("L'index 'rag' a été créé avec succès.")
            
            # Créer le vector store avec les chunks et les embeddings
            index = pinecone.Index("rag")
            
            # Convertir les chunks en vecteurs et les stocker dans Pinecone
            print("\nStockage des vecteurs dans Pinecone...")
            
            # Définir la variable d'environnement pour Pinecone
            os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
            
            # Utiliser l'instance Pinecone déjà créée
            vector_store = PineconeVectorStore.from_documents(
                documents=chunks,
                embedding=embedding,
                index_name="rag"
            )
            
            print("Les vecteurs ont été stockés avec succès dans Pinecone.")
            
        except Exception as e:
            print(f"Erreur lors de l'interaction avec Pinecone: {str(e)}")
        
except Exception as e:
    print(f"Erreur lors du chargement du modèle d'embeddings: {str(e)}")