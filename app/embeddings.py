#from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from PyPDF2 import PdfReader
import uuid
from app.database import get_crate_connection
import re

def clean_text(text):
    # Regular expression to match more than three occurrences of ". . . ." and remove them
    cleaned_text = re.sub(r'(\s*\.\s*\.\s*\.\s*\.\s*)', ' ', text)  # Replace three or more occurrences of ". . . ."
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space
    cleaned_text = cleaned_text.strip()  # Remove leading/trailing spaces
    return cleaned_text

def split_text_by_sections(text):
    # Regular expression to match sections with at least two numeric components (e.g., 1.1, 1.1.1, 2.3)
    pattern = r'(\d+\.\d+(\.\d+)*)(.*?)(?=\n\d+\.\d+(\.\d+)*|\Z)'  # Matches sections starting with n.n or n.n.n, etc.
    sections = re.findall(pattern, text, re.DOTALL)  # Find all matches, including newlines

    # Collect all the text with section headers and content, keeping the original order
    result = []
    for section in sections:
        section_header = section[0]
        section_content = clean_text(section[2].strip())
        result.append(f"{section_header} {section_content}")
    
    return result

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_embeddings(text):
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    return embeddings.embed_query(text)

def store_embeddings_in_cratedb(text, embeddings):
    conn = get_crate_connection()
    cursor = conn.cursor()
    embedding_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO embeddings (id, embedding, text) VALUES (?, ?, ?)
    ''', (embedding_id, embeddings, text))
    conn.close()

def process_pdf_and_store(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    sections = split_text_by_sections(text)
    for section in sections:
        embedding = generate_embeddings(section)
        store_embeddings_in_cratedb(section, embedding)