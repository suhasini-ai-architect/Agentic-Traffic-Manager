import os
import time
import httpx
import pandas as pd
import streamlit as st
from sqlmodel import Session, create_engine, select
# Re-using your architectural session logic to display live ledger data
from app.db.session import engine, ATMLog

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Guardian-Mesh AI Control Plane",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise Dark-Mode Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Gateway Endpoint Configuration via Env Variables (Cloud Ready)
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000/v1/proxy")

# --- DATABASE TELEMETRY LOGIC ---
def fetch_live_metrics():
    """Queries SQLModel database directly to pull real-time architectural KPIs."""
    try:
        with Session(engine) as session:
            statement = select(ATMLog)
            logs = session.exec(statement).all()
            
            if not logs:
                return {"status": "Healthy", "blocked": 0, "cache_rate": "0%", "avg_lat": "0.00s", "raw_logs": []}
            
            total = len(logs)
            blocked = len([l for l in logs if "BLOCKED" in l.status])
            cached = len([l for l in logs if "CACHED" in l.status])
            avg_latency = sum([l.latency for l in logs]) / total
            
            cache_rate = f"{(cached / total) * 100:.1f}%" if total > 0 else "0%"
            
            # Format logs for dataframes
            raw_logs = [{
                "Session ID": l.session_id,
                "Prompt Snippet": l.prompt[:40] + "..." if len(l.prompt) > 40 else l.prompt,
                "Status": l.status,
                "Latency": f"{l.latency:.3f}s",
                "Metadata": l.reason or "N/A"
            } for l in reversed(logs)] # Show newest first
            
            return {
                "status": "Healthy",
                "blocked": blocked,
                "cache_rate": cache_rate,
                "avg_lat": f"{avg_latency:.3f}s",
                "raw_logs": raw_logs
            }
    except Exception as e:
        return {"status": "Degraded (DB Error)", "blocked": "ERR", "cache_rate": "ERR", "avg_lat": "ERR", "raw_logs": []}

metrics = fetch_live_metrics()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🛡️ Control Plane Settings")
    st.info("Operating Mode: **Hybrid-Tenant Governance**")
    
    model_choice = st.selectbox("Active LLM Cluster", ["Phi-4 Mini (Local)", "Azure OpenAI Endpoint", "AWS Bedrock Core"])
    scrub_level = st.select_slider("Scrubbing Strictness", options=["Audit Only", "Standard Mitigation", "Strict Enforcement"])
    
    st.divider()
    st.subheader("Zero-Trust Policies")
    enable_cache = st.toggle("Enable FinOps Semantic Cache", value=True)
    enforce_pci = st.toggle("Enforce PCI-DSS / HIPAA Grids", value=True)
    
    st.caption("Architecture Node: gateway-routing-mesh-01")

# --- MAIN UI DISPLAY ---
st.title("Guardian-Mesh: Enterprise AI Governance")
st.caption("Enterprise Architecture Demonstration | Principal Engineer Track")

# Live KPI Metric Strip
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("System Fabric Status", metrics["status"])
with col2:
    st.metric("Security Violations Blocked", metrics["blocked"])
with col3:
    st.metric("FinOps Cache Hit Rate", metrics["cache_rate"])
with col4:
    st.metric("Average Proxy Latency", metrics["avg_lat"])

st.divider()

# Core Interaction Split Frame
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("📡 Live Prompt Interception Simulator")
    
    user_input = st.chat_input("Input enterprise transmission payload...")
    
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        
        # Real-time network interception call to FastAPI Gateway
        with st.status("Mesh Interceptor Evaluating Payload...", expanded=True) as status:
            try:
                st.write("🔍 Evaluating input vectors via Gateway Guard Pipelines...")
                
                # Mocking a static session ID for tracking
                payload = {"session_id": "session-corp-prod-abc", "prompt": user_input}
                
                start_network_time = time.time()
                response = httpx.post(GATEWAY_URL, json=payload, timeout=30.0)
                network_latency = time.time() - start_network_time
                
                if response.status_code == 200:
                    res_data = response.json()
                    
                    # Handle Gateway Blocking
                    if res_data.get("status") == "blocked":
                        status.update(label="⚠️ Security Threat Extinguished", state="error")
                        with st.chat_message("assistant"):
                            st.error(f"**Mesh Security Alert:** Request terminated by `InjectionShield`. Reason: {res_data.get('reason')}")
                    else:
                        status.update(label=f"✅ Payload Cleared ({network_latency:.3f}s)", state="complete")
                        with st.chat_message("assistant"):
                            st.markdown(f"**Gateway Response:**\n{res_data.get('response')}")
                            if "metrics" in res_data:
                                st.caption(f"Routing Status: {res_data['metrics']['status']} | Node Latency: {res_data['metrics']['latency_seconds']:.4f}s")
                else:
                    status.update(label="❌ Gateway Outage Detected", state="error")
                    st.error(f"Gateway returned an error state: {response.status_code}")
                    
            except httpx.RequestError as err:
                status.update(label="❌ Connection Refused", state="error")
                st.error(f"Could not connect to the Guardian-Mesh Gateway daemon at {GATEWAY_URL}. Ensure your Uvicorn backend is running.")

with right_col:
    st.subheader("📋 Direct Audit Ledger (`SQLModel` Sync)")
    if metrics["raw_logs"]:
        df = pd.DataFrame(metrics["raw_logs"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No pipeline logs parsed out of SQLite cluster database storage yet.")

    st.divider()
    st.subheader("🔍 Proxy Topography Matrix")
    st.image("https://img.icons8.com/color/96/000000/network-mesh.png", width=45) 
    st.caption("Stateless architectural layout processing inbound tokens dynamically before upstream vendor models.")