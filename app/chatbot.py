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
    
    # # Use knn_match to find the 4 most similar texts based on the query embedding
    # cursor.execute('''
    #     SELECT text
    #     FROM embeddings
    #     WHERE knn_match(embedding, ?, 4)
    #     ORDER BY _score DESC
    #     LIMIT 4
    # ''', (query_embedding,))
    
    # Retrieve the results
    similar_texts = [row[0] for row in cursor.fetchall()]

    conn.close()
    return similar_texts

# def get_most_similar_response(query):
#     conn = get_crate_connection()
#     cursor = conn.cursor()
#     query_embedding = OpenAIEmbeddings().embed_query(query)
    
#     cursor.execute('''
#         SELECT text, embedding
#         FROM embeddings
#     ''')
    
#     best_text = ""
#     max_similarity = 0
#     for text, embedding in cursor.fetchall():
#         similarity = cosine_similarity(query_embedding, embedding)
#         if similarity > max_similarity:
#             max_similarity = similarity
#             best_text = text
    
#     conn.close()
#     return best_text
