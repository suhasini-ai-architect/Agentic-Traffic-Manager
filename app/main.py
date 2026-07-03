from fastapi import FastAPI
from app.db.session import create_db_and_tables
from app.api.router import router as api_router

app = FastAPI(
    title="Guardian-Mesh | Enterprise AI Gateway",
    version="1.0.0"
)

# Mount the router instance directly
app.include_router(api_router)

@app.on_event("startup")
def on_startup():
    print("🚀 Initializing Enterprise Guardian-Mesh Gateway Control Plane...")
    create_db_and_tables()
    print("✅ Governance Database Schema Verification Complete.")