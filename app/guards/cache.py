import chromadb
from chromadb.utils import embedding_functions
import uuid
import os

class SemanticCache:
    def __init__(self):
        self.enabled = False
        try:
            # 1. Absolute Pathing to prevent Windows path confusion
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Put cache in project root, not inside guards folder
            cache_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "atm_cache")
            
            if not os.path.exists(cache_path):
                os.makedirs(cache_path)

            # 2. Initialize Client
            self.client = chromadb.PersistentClient(path=cache_path)
            
            # 3. Load Embedding Function
            self.model = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            # 4. Get Collection
            self.collection = self.client.get_or_create_collection(
                name="atm_responses", 
                embedding_function=self.model
            )
            self.enabled = True
            print("🧠 Semantic Cache: ChromaDB is online.")
        except Exception as e:
            print(f"⚠️ Semantic Cache failed to load: {e}")
            print("⚠️ ATM will continue running without caching.")

    def lookup(self, prompt: str, threshold: float = 0.2):
        if not self.enabled:
            return None
            
        try:
            results = self.collection.query(
                query_texts=[prompt], 
                n_results=1
            )
            
            if results['distances'] and len(results['distances'][0]) > 0:
                distance = results['distances'][0][0]
                if distance < threshold:
                    # Defensive check for nested metadata
                    return results['metadatas'][0][0].get('response')
        except Exception as e:
            print(f"🔍 Cache Lookup Error: {e}")
        return None

    def add(self, prompt: str, response: str):
        if not self.enabled:
            return
            
        try:
            self.collection.add(
                documents=[prompt],
                metadatas=[{"response": response}],
                ids=[str(uuid.uuid4())]
            )
            print("💾 Saved to Semantic Cache.")
        except Exception as e:
            print(f"💾 Cache Save Error: {e}")

# Create the instance
semantic_cache = SemanticCache()