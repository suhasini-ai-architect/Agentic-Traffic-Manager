import os
import time
import re
import httpx
from fastapi import APIRouter, HTTPException, Request

# Point these relative imports exactly to your existing app structure
from app.db.session import log_event, ATMLog
from app.semantic_cache import global_cache

# Import the new provider factory pattern you created
from app.providers import get_provider

router = APIRouter()

# Initialize the cluster provider globally at startup based on environment variables
llm_provider = get_provider()
PROVIDER_TYPE = os.getenv("UPSTREAM_PROVIDER", "OLLAMA").upper()

# -------------------------------------------------------------
# ADVANCED ENTERPRISE SECURITY GUARDS
# -------------------------------------------------------------
class InjectionShield:
    def __init__(self):
        self.malicious_patterns = [
            re.compile(r"ignore previous instructions", re.IGNORECASE),
            re.compile(r"you are now an unrestricted", re.IGNORECASE),
            re.compile(r"system prompt override", re.IGNORECASE),
            re.compile(r"dan mode", re.IGNORECASE),
            re.compile(r"developer mode active", re.IGNORECASE)
        ]

    def is_malicious(self, text: str) -> bool: 
        return any(pattern.search(text) for pattern in self.malicious_patterns)


class PiiGuard:
    def __init__(self):
        self.pii_patterns = {
            "CREDIT_CARD_PCI": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
            "US_SSN_HIPAA": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "EMAIL_ADDRESS": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "API_SECRET_KEY": re.compile(r"(sk-[a-zA-Z0-9]{32,})|(AIzaSy[a-zA-Z0-9-_]{35})")
        }

    def scrub(self, text: str) -> tuple[str, list]: 
        found_entities = []
        scrubbed_text = text
        
        for entity_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(scrubbed_text)
            if matches:
                for match in matches:
                    actual_match = match[0] if isinstance(match, tuple) else match
                    if actual_match and actual_match not in found_entities:
                        found_entities.append(f"{entity_type}: {actual_match[:4]}****")
                
                scrubbed_text = pattern.sub(f"[{entity_type}_REDACTED]", scrubbed_text)
                
        return scrubbed_text, found_entities


injection_shield = InjectionShield()
pii_guard = PiiGuard()

# -------------------------------------------------------------
# SECURE PROXY INTERCEPTION ROUTE
# -------------------------------------------------------------
@router.post("/v1/proxy")
async def proxy_request(request: Request):
    """
    Zero-Trust Interception Pipeline acting as a state-monitored proxy.
    """
    print(f"\n--- 🛡️ NEW PROXY TRANSMISSION INTERCEPTED [{PROVIDER_TYPE}] ---")
    start_time = time.time()
    
    try:
        body = await request.json()
        session_id = body.get("session_id", "anonymous-session")
        raw_prompt = body.get("prompt", "")
        
        if not raw_prompt:
            raise HTTPException(status_code=400, detail="Payload execution requires a valid prompt string.")

        # LAYER 1: FinOps Optimization (Semantic Vector Match)
        cached_response = global_cache.get_cached_response(raw_prompt)
        if cached_response:
            latency = time.time() - start_time
            log_event(ATMLog(
                session_id=session_id, prompt=raw_prompt, response=cached_response,
                status="CACHED_HIT", tokens=0, latency=latency
            ))
            return {
                "response": cached_response, 
                "metrics": {"status": "cache_hit", "latency_seconds": latency}
            }

        # LAYER 2: Input Security (Injection Guard Plane)
        if injection_shield.is_malicious(raw_prompt):
            latency = time.time() - start_time
            log_event(ATMLog(
                session_id=session_id, prompt=raw_prompt, response="[BLOCKED]",
                status="BLOCKED_INJECTION", reason="Security Guard Violation: Malicious prompt injection detected.", 
                tokens=0, latency=latency
            ))
            return {"status": "blocked", "reason": "security_violation"}

        # LAYER 3: Governance Compliance (Data Sanitization Plane)
        scrubbed_prompt, found_pii = pii_guard.scrub(raw_prompt)
        status_flag = "PASSED_WITH_REDACTION" if found_pii else "PASSED_CLEAN"

        # LAYER 4: Upstream Orchestration (Dynamic Provider Execution)
        print(f"🔗 Routing sanitized tokens via provider engine mapping...")
        llm_response = await llm_provider.generate(scrubbed_prompt)

        # LAYER 5: Post-Execution Telemetry (Persistence & Vector Update)
        global_cache.update_cache(raw_prompt, llm_response)
        
        latency = time.time() - start_time
        log_event(ATMLog(
            session_id=session_id, prompt=scrubbed_prompt, response=llm_response,
            status=status_flag, reason=f"Entities Flagged: {', '.join(found_pii)}" if found_pii else None,
            tokens=0, latency=latency
        ))
        
        return {
            "response": llm_response,
            "metrics": {
                "status": status_flag, 
                "latency_seconds": latency, 
                "pii_detected": len(found_pii) > 0
            }
        }

    except httpx.HTTPError as exc:
        print(f"❌ Upstream Infrastructure Provider Unreachable: {exc}")
        raise HTTPException(status_code=502, detail=f"Upstream compute cluster [{PROVIDER_TYPE}] offline or degraded.")
    except Exception as e:
        print(f"❌ Internal Fabric Fault: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Architecture System Fault.")