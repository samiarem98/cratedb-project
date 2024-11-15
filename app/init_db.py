# init_db.py
import pandas as pd
import psycopg2
import logging
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from crate import client
from psycopg2 import OperationalError
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection settings
DB_NAME = "langchain"
DB_USER = "crate"
DB_HOST = "cratedb"
DB_PORT = 5432
SSL_MODE = "disable"

# Function to get CrateDB connection
def get_crate_connection():
    """
    Establish a connection to CrateDB using psycopg2.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host=DB_HOST,
            port=DB_PORT,
            sslmode=SSL_MODE
        )
        logger.info("Successfully connected to CrateDB.")
        return conn
    except OperationalError as e:
        logger.error(f"Error connecting to CrateDB: {e}")
        raise

# Function to create the embeddings table
def create_embeddings_table(cursor):
    """
    Create the embeddings table in CrateDB.
    """
    try:
        cursor.execute("DROP TABLE IF EXISTS embeddings;")
        cursor.execute("""
            CREATE TABLE embeddings (
                text TEXT, 
                embedding FLOAT_VECTOR(1536)
            );
        """)
        logger.info("Embeddings table created successfully.")
    except Exception as e:
        logger.error(f"Error creating embeddings table: {e}")
        raise

# Function to insert data into the embeddings table
def insert_embeddings_data(cursor, df):
    """
    Insert the document text and corresponding embeddings into the CrateDB table.
    """
    try:
        for index, row in df.iterrows():
            cursor.execute(
                "INSERT INTO embeddings (text, embedding) VALUES (%s, %s)",
                (row['text'], row['embedding'])
            )
        logger.info(f"Inserted {len(df)} rows into embeddings table.")
    except Exception as e:
        logger.error(f"Error inserting data into embeddings table: {e}")
        raise

# Function to create embeddings from documents
def create_embeddings(pages):
    """
    Generate embeddings for a list of pages using OpenAI embeddings.
    """
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        pages_text = [doc.page_content for doc in pages]
        pages_embeddings = embeddings.embed_documents(pages_text)
        
        # Create a DataFrame with the text and embeddings
        df = pd.DataFrame(list(zip(pages_text, pages_embeddings)), columns=['text', 'embedding'])
        logger.info(f"Generated embeddings for {len(df)} documents.")
        return df
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise

# Function to initialize the database and insert data
def init_db(pages):
    """
    Initialize the database by creating the embeddings table and inserting data.
    """
    try:
        # Create database connection
        conn = get_crate_connection()
        
        # Use connection to run SQL queries
        with conn.cursor() as cursor:
            # Create the embeddings table
            create_embeddings_table(cursor)
            
            # Create embeddings and insert data
            df = create_embeddings(pages)
            insert_embeddings_data(cursor, df)
            
            # Refresh the table to ensure changes are committed
            cursor.execute("REFRESH TABLE embeddings;")
            conn.commit()
        
        conn.close()
        logger.info("Database initialized successfully.")
        return df.head(5)  # Return the first 5 rows of the DataFrame for confirmation
    except Exception as e:
        logger.error(f"Error initializing the database: {e}")
        raise

# Example usage:
if __name__ == "__main__":
    try:
        logger.info("------------------Initialization.---------------------")
        loader = PyPDFLoader("data/Databricks.pdf")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        pages = loader.load_and_split(text_splitter)
        result = init_db(pages)  # Initializes DB and prints the first 5 rows of the DataFrame
        logger.info("Initialization complete.")
        logger.info(f"Sample Data: {result}")
    except Exception as e:
        logger.error(f"Failed to initialize the database: {e}")
        exit(1)  # Exit with an error code if the initialization fails