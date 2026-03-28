import os
import csv
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    # Connects to your Docker container using the .env URL
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Create the table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            date DATE,
            merchant TEXT,
            amount DECIMAL(10,2),
            category TEXT,
            is_recurring BOOLEAN,
            ai_status TEXT DEFAULT 'pending',
            ai_analysis TEXT
        );
    """)

    # 2. Open the CSV and insert data
    with open('data/dummy_transactions.csv', mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT INTO transactions (date, merchant, amount, category, is_recurring)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['date'], row['merchant'], row['amount'], row['category'], row['is_recurring']))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database is ready and data is loaded!")

if __name__ == "__main__":
    setup_database()