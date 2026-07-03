# app/guards/cost.py

class CostGuard:
    def __init__(self, daily_limit=1000):
        self.daily_limit = daily_limit
        self.usage = {} # session_id -> total_tokens

    def update_and_check(self, session_id: str, text: str) -> bool:
        tokens = len(text.split()) * 1.3
        
        if session_id not in self.usage:
            self.usage[session_id] = 0
            
        self.usage[session_id] += tokens
        
        if self.usage[session_id] > self.daily_limit:
            return False # Limit exceeded
        return True

    def get_usage(self, session_id):
        return self.usage.get(session_id, 0)

cost_guard = CostGuard(daily_limit=500) # Small limit for testing