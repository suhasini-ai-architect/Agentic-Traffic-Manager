import streamlit as st
import time
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Guardian-Mesh AI Architect",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional "Dark Mode" Enterprise feel
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_view_safe_headers=True)

# --- MOCK LOGIC (Replace with your actual imports) ---
def guardian_scrub_logic(text):
    """
    Integration point for your PII scrubbing scripts.
    Returns (is_sensitive, scrubbed_text, found_entities)
    """
    sensitive_keywords = ["credit card", "ssn", "password", "email"]
    found = [word for word in sensitive_keywords if word in text.lower()]
    if found:
        return True, text.lower().replace(found[0], "[REDACTED]"), found
    return False, text, []

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.header("🛡️ Control Plane Settings")
    st.info("Currently running in **Azure-Hybrid Mode**")
    
    model_choice = st.selectbox("LLM Backend", ["Phi-4 Mini (Local)", "Azure OpenAI", "Llama 3 (Ollama)"])
    scrub_level = st.select_slider("Scrubbing Intensity", options=["Audit Only", "Standard", "Strict"])
    
    st.divider()
    st.subheader("Trust Zones")
    enable_cache = st.toggle("Enable Semantic Cache", value=True)
    enforce_pci = st.toggle("PCI-DSS Compliance", value=True)
    
    if st.button("Clear Audit Logs", use_container_width=True):
        st.session_state.logs = []

# --- MAIN UI ---
st.title("Guardian-Mesh: Enterprise AI Governance")
st.caption("Azure Solution Architect | AI Governance MVP | Stealth Mode")

# Metric Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("System Status", "Healthy", delta="0.025s Latency")
with col2:
    st.metric("PII Blocked", "1,248", delta="+42 today")
with col3:
    st.metric("Cache Hit Rate", "68%", delta="12% vs last week")
with col4:
    st.metric("Total Tokens Saved", "450k", delta="SaaS Ready")

st.divider()

# Core Interaction Area
left_col, right_col = st.columns([3, 2])

if 'logs' not in st.session_state:
    st.session_state.logs = []

with left_col:
    st.subheader("📡 Live Request Interception")
    
    prompt = st.chat_input("Enter a prompt (e.g., 'My credit card number is 1234...')")
    
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        
        # 1. Interception Phase
        is_sensitive, scrubbed, entities = guardian_scrub_logic(prompt)
        
        with st.status("Guardian-Mesh Processing...", expanded=True) as status:
            st.write("🔍 Scanning for PII/Sensitive Data...")
            time.sleep(0.6)
            
            if is_sensitive:
                st.error(f"Sensitive Data Detected: {entities}")
                st.write(f"🛡️ Applying Redaction: {scrubbed}")
            else:
                st.success("No PII detected. Proceeding.")
                
            st.write("🚀 Routing to LLM Backend...")
            time.sleep(0.4)
            status.update(label="Request Authorized", state="complete")

        with st.chat_message("assistant"):
            if is_sensitive:
                st.write(f"**Mesh Notice:** Your request was sanitized before reaching the model.")
                st.write(f"**LLM Response:** I see you've provided a [REDACTED]. How can I help with that safely?")
            else:
                st.write("This is a simulated response from your Phi-4 Mini backend.")

        # Add to Audit Logs
        st.session_state.logs.insert(0, {
            "Timestamp": time.strftime("%H:%M:%S"),
            "Status": "BLOCKED" if is_sensitive else "PASSED",
            "Latency": "0.025s",
            "Entities": ", ".join(entities) if entities else "None"
        })

with right_col:
    st.subheader("📋 Audit Ledger")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("No traffic detected yet.")

    st.divider()
    st.subheader("🔍 Architectural View")
    st.image("https://img.icons8.com/color/96/000000/network-mesh.png", width=50) 
    st.caption("The Guardian-Mesh sits between your application and the LLM, acting as a stateless proxy for governance.")