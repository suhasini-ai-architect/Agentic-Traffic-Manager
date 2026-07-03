import sqlite3

conn = sqlite3.connect('atm_logs.db')
cursor = conn.cursor()

try:
    cursor.execute("SELECT session_id, status, latency FROM atmlog ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    print("\n--- RECENT LOGS ---")
    for row in rows:
        print(f"Session: {row[0]} | Status: {row[1]} | Latency: {row[2]}s")
except Exception as e:
    print(f"Could not read DB: {e}")
finally:
    conn.close()