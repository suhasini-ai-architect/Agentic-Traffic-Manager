import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize a lightweight model (perfect for laptops)
model = SentenceTransformer('all-MiniLM-L6-v2')

class SemanticCache:
    def __init__(self, threshold=0.92):
        self.cache = []  # List of dicts: {"embedding": np.array, "response": str, "prompt": str}
        self.threshold = threshold

    def get_cached_response(self, prompt):
        if not self.cache:
            return None
        
        # Generate embedding for the incoming prompt
        query_embedding = model.encode([prompt])
        
        # Compare with all cached embeddings
        cached_embeddings = np.array([item["embedding"] for item in self.cache])
        similarities = cosine_similarity(query_embedding, cached_embeddings)[0]
        
        max_idx = np.argmax(similarities)
        if similarities[max_idx] >= self.threshold:
            print(f"--- Semantic Cache Hit (Score: {similarities[max_idx]:.2f}) ---")
            return self.cache[max_idx]["response"]
        
        return None

    def update_cache(self, prompt, response):
        embedding = model.encode([prompt])[0]
        self.cache.append({
            "prompt": prompt,
            "embedding": embedding,
            "response": response
        })

# Singleton instance
global_cache = SemanticCache()