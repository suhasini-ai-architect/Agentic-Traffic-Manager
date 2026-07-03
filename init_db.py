from app.db.session import create_db_and_tables
import os

if __name__ == "__main__":
    print("🛠️ Manually creating database...")
    create_db_and_tables()

    # Check if it actually worked
    db_file = os.path.join(os.getcwd(), "atm_logs.db")
    if os.path.exists(db_file):
        print(f"✅ Success! File created at: {db_file}")
    else:
        print("❌ Still missing. Check your BASE_DIR logic in session.py.")