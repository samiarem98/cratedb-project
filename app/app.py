from flask import Flask, request, jsonify, render_template
from .chatbot import get_most_similar_response
import os
from dotenv import load_dotenv
from openai import OpenAI
import re  # For regular expressions to clean up the response

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI client
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Render the chatbot page

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    response = get_most_similar_response(question)
    
    # Clean the response before returning it
    cleaned_response = clean_response(response)
    
    return jsonify({"answer": cleaned_response})

@app.route('/test_gpt', methods=['POST'])
def test_gpt():
    data = request.get_json()
    user_message = data.get("question", "")
    
    if not user_message:
        return jsonify({"error": "No question provided"}), 400

    try:
        # OpenAI API request to get the model's response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # You can change to "gpt-4" if you have access
            messages=[{"role": "user", "content": user_message}]
        )
        
        # Get the assistant's reply
        assistant_reply = response.choices[0].message.content
        
        return jsonify({"answer": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
