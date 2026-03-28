from flask import Flask, render_template, request, jsonify
from graph import movie_app
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get("message")
    genre = request.json.get("genre", "")

    full_query = f"Find a Movie or Series , decide movie or series (Movie or series decided by input = {user_input}, Genre decided by = {genre})  that is new and has a high IMDb rating. Mention all the tools used, Also send Push notification"
    
    inputs = {"messages": [("user", full_query)]}
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    result = movie_app.invoke(inputs, config)
    final_answer = result["messages"][-1].content

    return jsonify({"answer": final_answer})

if __name__ == '__main__':
    app.run(debug=True)