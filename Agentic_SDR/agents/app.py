from flask import Flask, render_template, request, jsonify
import asyncio
from manager_agent import run_sales_team

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    lead_info = request.form.get('lead_info', 'General Lead')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(run_sales_team(lead_info))
    loop.close()

    return jsonify({"email": result})

if __name__ == "__main__":
    app.run(debug=True)