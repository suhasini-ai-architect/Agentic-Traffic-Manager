import requests
import time

ATM_URL = "http://localhost:8000/v1/proxy"

def run_broken_simulation():
    session_id = f"demo-session-{int(time.time())}"
    
    # SCENARIO: An agent that keeps asking the same thing because it's 'confused'
    confused_prompt = "I need to check the weather in Pune. Can you check the weather in Pune?"
    
    print(f"🚀 Starting Simulation for Session: {session_id}")
    
    for i in range(1, 7):
        print(f"\n[Iteration {i}] Sending prompt to ATM...")
        
        payload = {
            "session_id": session_id,
            "prompt": confused_prompt
        }
        
        try:
            response = requests.post(ATM_URL, json=payload)
            data = response.json()
            
            status = data.get("atm_metadata", {}).get("guard_status")
            
            if status == "KILLED":
                print(f"🛑 ATM INTERVENED: {data['atm_metadata']['reason']}")
                print(f"Final Message: {data.get('response')}")
                break
            else:
                print(f"✅ ATM PASSED: Response received (Tokens used: {data['atm_metadata'].get('usage')})")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    run_broken_simulation()