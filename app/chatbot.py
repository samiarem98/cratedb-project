from app.database import get_crate_connection
from langchain.embeddings import OpenAIEmbeddings

def get_most_similar_response(query):
    conn = get_crate_connection()
    cursor = conn.cursor()
    
    # Generate embedding for the query
    query_embedding = OpenAIEmbeddings().embed_query(query)

    cursor.execute('''
        SELECT text 
        FROM embeddings 
        WHERE knn_match(embedding, {0}, 4) 
        ORDER BY _score DESC 
        LIMIT 4
    '''.format(query_embedding))

    # Retrieve the results
    similar_texts = [row[0] for row in cursor.fetchall()]

    conn.close()
    return similar_texts