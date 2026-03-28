from flask import Flask, render_template, redirect
import psycopg2
import os
from dotenv import load_dotenv
from agent_engine import get_anomalies, analyze_anomaly

load_dotenv()
app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.route('/')
def index():
    # Fetch all transactions to show on the page
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions ORDER BY date DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', transactions=rows)

@app.route('/audit', methods=['POST'])
def audit():
    # 1. Find the anomalies using our SQL filter
    anomalies = get_anomalies()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    for row in anomalies:
        t_id, merchant, amount = row
        # 2. Get Gemini's verdict
        verdict = analyze_anomaly(merchant, amount)
        
        # 3. Update the database with the findings
        cur.execute("""
            UPDATE transactions 
            SET ai_status = 'flagged', ai_analysis = %s 
            WHERE id = %s
        """, (verdict, t_id))
    
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, port=5000)