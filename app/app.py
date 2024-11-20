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

# Function to clean the response from unwanted characters
def clean_response(response: str) -> str:
    # Step 1: Remove unnecessary escape sequences (like \n, \\)
    response = re.sub(r'\\n', '\n', response)  # Replace escaped newlines with actual newlines
    response = re.sub(r'\\', '', response)    # Remove backslashes
    
    # Step 2: Remove extra spaces and line breaks (collapse multiple spaces into a single space)
    response = re.sub(r'\s+', ' ', response)  # Collapsing multiple spaces into one

    # Step 3: Properly handle line breaks for readability
    # Insert a newline after each sentence for better readability
    response = re.sub(r'([.!?])\s+(?=[A-Z])', r'\1\n\n', response)  # Split sentences into separate paragraphs

    # Step 4: Preserve markdown formatting for code blocks (wrap with triple backticks)
    response = re.sub(r'```', '\n```', response)  # Ensure triple backticks are on separate lines

    # Step 5: If there are bullet points or numbered lists, ensure they are formatted correctly
    # Format bullet points with a space after the dot
    response = re.sub(r'(\d+)\.\s+', r'\1. ', response)  # Ensure numbered lists are formatted correctly
    response = re.sub(r'(\*|[-+])\s+', r'\1 ', response)  # Fix bullet points formatting

    # Step 6: Handle bold text (markdown style)
    response = re.sub(r'(\*\*.+?\*\*)', r'\1', response)  # Preserve bold formatting

    # Step 7: Ensure proper indentation for code blocks
    # Clean up code formatting for clarity
    response = re.sub(r'```(.*?)```', lambda m: '```' + m.group(1).strip() + '```', response, flags=re.DOTALL)

    # Step 8: Strip leading/trailing spaces and ensure no unwanted leading spaces for blocks
    return response.strip()
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
        
        # Clean the assistant's reply before returning it
        cleaned_reply = clean_response(assistant_reply)
        
        return jsonify({"answer": cleaned_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
