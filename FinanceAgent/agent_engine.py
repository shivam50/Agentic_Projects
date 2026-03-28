import os
from google import genai
from dotenv import load_dotenv
from tools.search_tool import research_merchant
import psycopg2

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_anomalies():
    """Finds transactions 3x higher than average for that merchant."""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    query = """
    SELECT id, merchant, amount 
    FROM transactions t1
    WHERE amount > (
        SELECT AVG(amount) * 3 
        FROM transactions t2 
        WHERE t1.merchant = t2.merchant
    );
    """
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def analyze_anomaly(merchant, amount):
    web_context = research_merchant(merchant)
    prompt = f"""
    You are a Personal Finance Assistant. 
    I found a suspicious transaction: ${amount} at {merchant}.
    
    Web Research: {web_context}
    
    Is this a high risk for fraud or just a large purchase? 
    Answer in 1 very short sentence.
    """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text

if __name__ == "__main__":    
    anomalies = get_anomalies()
    for row in anomalies:
        t_id, merchant, amount = row
        print(f"\n🕵️ Analyzing Transaction {t_id}...")
        verdict = analyze_anomaly(merchant, amount)
        print(f"🤖 Gemini Verdict: {verdict}")