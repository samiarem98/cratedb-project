from crate import client
import psycopg2

def get_crate_connection():
    # Using the CRATE_DB_URL environment variable from Docker 
    conn = psycopg2.connect(
        dbname="langchain",  # your database name
        user="crate",        # user for CrateDB
        host="cratedb",      # CrateDB host (adjust as needed)
        port=5432,           # CrateDB port
        sslmode="disable"    # disable SSL if not required
    )
    return conn

# def get_db_connection():
#     connection = client.connect(
#         host="cratedb",    # the name of the CrateDB service from docker-compose.yml
#         port="5432",
#         user="crate",
#         password="",
#         database="doc"     # default CrateDB schema
#     )
#     return connection

def create_embeddings_table():
    conn = get_crate_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DROP TABLE embeddings
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id STRING PRIMARY KEY,
            embedding ARRAY(FLOAT),
            text STRING
        )
    ''')
    conn.close()