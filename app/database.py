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