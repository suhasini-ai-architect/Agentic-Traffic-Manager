# app/guards/loop.py

class LoopDetector:
    def __init__(self, threshold=3):
        # session_id -> list of recent prompts
        self.history = {}
        self.threshold = threshold

    def is_looping(self, session_id: str, prompt: str) -> bool:
        if session_id not in self.history:
            self.history[session_id] = []
        
        # Check if this exact prompt has appeared recently
        matches = [p for p in self.history[session_id] if p == prompt]
        
        if len(matches) >= self.threshold:
            return True
        
        # Keep history lean (last 5 prompts)
        self.history[session_id].append(prompt)
        if len(self.history[session_id]) > 5:
            self.history[session_id].pop(0)
            
        return False

# Global instance for the MVP
detector = LoopDetector()