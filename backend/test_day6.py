import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

def test_db():
    print("Testing DB connection...")
    db_path = "fraud_cases.db"
    if not os.path.exists(db_path):
        print(f"ERROR: {db_path} not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM fraud_cases")
        count = c.fetchone()[0]
        print(f"SUCCESS: Connected to DB. Found {count} cases.")
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

def test_imports():
    print("Testing imports...")
    try:
        from src.day6_fraud_agent import FraudAgent
        print("SUCCESS: Successfully imported FraudAgent")
    except ImportError as e:
        print(f"ERROR: Import failed: {e}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_db()
    test_imports()
