import re

class PIIScrubber:
    def __init__(self):
        # Basic patterns for MVP (Email and Phone)
        self.patterns = {
            "EMAIL": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
            "PHONE": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        }

    def scrub(self, text: str) -> tuple[str, list]:
        found_pii = []
        scrubbed_text = text
        
        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, scrubbed_text)
            if matches:
                found_pii.extend([pii_type] * len(matches))
                scrubbed_text = re.sub(pattern, f"[{pii_type}_REDACTED]", scrubbed_text)
        
        return scrubbed_text, found_pii

pii_guard = PIIScrubber()