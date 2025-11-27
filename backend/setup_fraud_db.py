import sqlite3
import os

DB_FILE = "fraud_cases.db"

def create_connection():
    """Create a database connection to the SQLite database specified by DB_FILE."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        print(f"Connected to {DB_FILE}")
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """Create the fraud_cases table."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS fraud_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        security_identifier TEXT NOT NULL,
        card_ending TEXT NOT NULL,
        status TEXT NOT NULL,
        merchant TEXT NOT NULL,
        amount TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        location TEXT NOT NULL,
        security_question TEXT NOT NULL,
        security_answer TEXT NOT NULL
    );
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Table 'fraud_cases' created.")
    except sqlite3.Error as e:
        print(e)

def insert_sample_data(conn):
    """Insert sample fraud cases."""
    cases = [
        (
            "John",
            "12345",
            "4242",
            "pending_review",
            "ABC Industry",
            "$125.50",
            "2023-10-27 14:30:00",
            "New York, NY",
            "What is your mother's maiden name?",
            "Smith"
        ),
        (
            "Jane",
            "67890",
            "1111",
            "pending_review",
            "Global Electronics",
            "$999.99",
            "2023-10-28 09:15:00",
            "San Francisco, CA",
            "What was the name of your first pet?",
            "Fluffy"
        )
    ]
    
    sql = ''' INSERT INTO fraud_cases(user_name, security_identifier, card_ending, status, merchant, amount, timestamp, location, security_question, security_answer)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    
    try:
        c = conn.cursor()
        # Check if data already exists to avoid duplicates on re-run
        c.execute("SELECT count(*) FROM fraud_cases")
        count = c.fetchone()[0]
        if count == 0:
            c.executemany(sql, cases)
            conn.commit()
            print(f"Inserted {len(cases)} sample cases.")
        else:
            print("Data already exists, skipping insertion.")
            
    except sqlite3.Error as e:
        print(e)

def main():
    # Remove existing db to ensure fresh start if needed, or just connect
    # if os.path.exists(DB_FILE):
    #     os.remove(DB_FILE)
    
    conn = create_connection()
    if conn is not None:
        create_table(conn)
        insert_sample_data(conn)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
