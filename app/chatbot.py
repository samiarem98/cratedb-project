from langchain.embeddings import OpenAIEmbeddings
from app.database import get_crate_connection
from openai import OpenAI  # Add this import to use the OpenAI client
import os
import re

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])  # Make sure your OpenAI API key is set in the environment variables

def clean_response(raw_response):
    """
    Cleans and formats the response for better readability.
    """
    # Trim excessive whitespace
    clean_text = raw_response.strip()

    # Format code blocks
    clean_text = re.sub(r"```(.*?)```", r"```\1```", clean_text, flags=re.DOTALL)

    # Add spacing for lists (bullet or numbered)
    clean_text = re.sub(r"(?<=\n)(\d+\.\s)", r"\n\1", clean_text)  # Numbered lists
    clean_text = re.sub(r"(?<=\n)([-*]\s)", r"\n\1", clean_text)   # Bullet lists

    # Add line breaks around headings or emphasized sections
    clean_text = re.sub(r"(?<=\n)(\*\*.*?\*\*)", r"\n\1\n", clean_text)

    # Remove excessive newlines
    clean_text = re.sub(r"\n\s*\n", "\n\n", clean_text)

    # Optionally, handle table formatting or blockquotes
    clean_text = clean_text.replace("|", " | ")  # For table formatting
    clean_text = re.sub(r"(^>\s)", r"\n\1", clean_text, flags=re.MULTILINE)  # Blockquotes

    return clean_text




def get_most_similar_response(query):
    conn = get_crate_connection()
    cursor = conn.cursor()
    
    # Generate embedding for the query
    query_embedding = OpenAIEmbeddings().embed_query(query)

    cursor.execute(''' 
        SELECT text 
        FROM embeddings 
        WHERE knn_match(embedding, %s, 4)  -- Use the embedding for search
        ORDER BY _score DESC 
        LIMIT 4
    ''', (query_embedding,))
    
    # Retrieve the most similar texts
    similar_texts = [row[0] for row in cursor.fetchall()]
    
    conn.close()

    # Concatenate the found documents to use as context for the model
    context = '---\n'.join(similar_texts)

    # Construct system prompt for OpenAI's model
    system_prompt = f"""
      You are a Databricks expert tasked with answering user questions exclusively related to Databricks.

      ### Guidelines for answering:
      1. Use only the provided context to generate an answer. Do not use any external information or assumptions.
      2. Ensure your answer is concise, detailed, accurate, and directly addresses the user's query.
      3. Do not speculate or include additional details not explicitly supported by the provided context.
      4. Format answers in plain text with clear and structured responses. Avoid unnecessary characters like excessive escape sequences.
      5. If the user's query is vague, ambiguous, or too broad, respond by asking a clarifying question to narrow down their intent before providing an answer. Avoid attempting to answer until clarification is provided. For example:  
         - Query: "How do I manage tables?"  
         - Follow-up: "Would you like to know about creating, modifying, or dropping tables?"
      6. At the end of your response, always include the page number(s) and section number(s) from which the information was extracted. Use the format:  
         "Source: Page [Page Number], Section [Section Number]"  
      7. If the provided context does not contain relevant information, respond only with: "I don't know."
      8. If the query is not about Databricks, respond with: "I don't know."

      ### Context:
      {context}
"""

    # Use OpenAI to get a response with the provided context
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Adjust to "gpt-4" if needed
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        
        # Clean and return the assistant's response
        raw_response = response.choices[0].message.content
        return clean_response(raw_response)
    except Exception as e:
        return f"Error generating response: {e}"
