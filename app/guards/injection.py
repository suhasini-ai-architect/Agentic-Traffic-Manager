import re

class InjectionShield:
    def __init__(self):
        # Patterns commonly used in jailbreak attempts
        self.malicious_patterns = [
            r"ignore (all )?previous instructions",
            r"system override",
            r"you are now an admin",
            r"disregard (any )?guidelines",
            r"new role:",
            r"forget everything you know"
        ]

    def is_malicious(self, text: str) -> bool:
        text_lower = text.lower()
        for pattern in self.malicious_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

injection_shield = InjectionShield()