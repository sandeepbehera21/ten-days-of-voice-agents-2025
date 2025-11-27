import sqlite3
import os

DB_FILE = "fraud_cases.db"

def view_db():
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM fraud_cases")
        rows = c.fetchall()
        
        if not rows:
            print("No records found in fraud_cases table.")
        else:
            print(f"{'ID':<5} {'Name':<10} {'Status':<20} {'Merchant':<20} {'Amount':<10} {'Notes'}")
            print("-" * 80)
            for row in rows:
                # Handle cases where columns might be missing if schema changed, though unlikely here
                r = dict(row)
                print(f"{r['id']:<5} {r['user_name']:<10} {r['status']:<20} {r['merchant']:<20} {r['amount']:<10}")
    except sqlite3.Error as e:
        print(f"Error reading database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    view_db()
