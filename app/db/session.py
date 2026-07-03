import os
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session

# 1. Unified Enterprise Model
class ATMLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    prompt: str
    response: str
    status: str
    reason: Optional[str] = None
    tokens: float
    latency: float
    timestamp: Optional[float] = Field(default_factory=None)


# 2. Dynamic Database Factory (Multi-Cloud Flagship Pattern)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    # Enterprise Cloud Deployment Mode (AWS RDS / Azure PostgreSQL)
    print("🌐 [Data Fabric] Initializing Cloud-Scale PostgreSQL Engine Connection...")
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_size=20,          # Keeps active pool connections warm
        max_overflow=10,       # Handles sudden traffic bursts gracefully
        pool_timeout=30,       # Clean failure states under high stress
        pool_recycle=1800      # Prevents connection drops from cloud firewalls
    )
else:
    # Local Resilient Fallback Mode
    current_file_path = os.path.abspath(__file__)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
    DB_PATH = os.path.join(BASE_DIR, "atm_logs.db")
    
    print(f"💻 [Data Fabric] Local Fallback Detected. Targeting Local SQLite Cluster: {DB_PATH}")
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        echo=False,
        connect_args={"check_same_thread": False} # Required for FastAPI multi-threaded execution
    )


# 3. Gateway Architecture Helper Operations
def create_db_and_tables():
    """Ensures database schemas exist at startup without manual DB manipulation."""
    SQLModel.metadata.create_all(engine)

def reset_db():
    """Administrative command to wipe and clear local/staging topologies."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("🧹 Enterprise Governance Database wiped and reset successfully.")

def log_event(log_entry: ATMLog):
    """Executes atomic transactions via session pooling context managers."""
    with Session(engine) as session:
        session.add(log_entry)
        session.commit()
        session.refresh(log_entry)