# Retrieval-Augmented Generation (RAG) Architecture - Proof of Concept (POC)

This repository contains a Proof of Concept (POC) for a Retrieval-Augmented Generation (RAG) architecture. 

The project demonstrates how to process and store data from a PDF in aa vector database (CrateDB) and use it in a chatbot application to answer user queries.

## Overview

The POC consists of the following components:

1. **CrateDB**:  
   An open source distributed SQL database used as a vector store to store processed data.
   
2. **Web Service**:  
   A Flask-based chatbot application that handles user queries by retrieving relevant information from CrateDB.

### Key Features:
- **PDF Initialization**: Processes a Databricks certification PDF and populates CrateDB with the data.
- **Chatbot Interface**: A simple chatbot to answer questions based on the PDF's content.

## Architecture

- The project uses **Docker Compose** to manage and run the services.
- **CrateDB** stores vectorized data from the PDF.
- **Flask Web Service**:
  - Handles PDF processing and inserts vectorized data into CrateDB during initialization.
  - Provides a chatbot API to respond to user questions by retrieving relevant data from CrateDB.

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.

### Installation and Setup 

1. Start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Once the services are running, you can interact with them as described below.

## Accessing the Services

### Viewing Running Services

To see the list of running services, use the following command:  
```bash
docker ps
```

This will show you the active containers, their names, and the ports they expose.

### Accessing CrateDB

- **URL**: [http://127.0.0.1:4200](http://127.0.0.1:4200)  
- CrateDB is accessible on port `4200`.  
- You can log in using the default credentials (if set up).  
- **Check Initialization**:
  1. Open the CrateDB console.
  2. Navigate to the **Tables** section to verify that the tables are initialized and populated with data from the PDF.

### Accessing the Chatbot

- **Home Page**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)  
  The Flask application’s home page is accessible on port `5000`.
  
- **Ask Endpoint**:  
  Use Postman or a similar tool to test the chatbot:
  ```
  POST http://127.0.0.1:5000/ask
  ```

  **Request Body Example**:
  ```json
  {
    "question": "How do I set up an ETL pipeline in Databricks using Delta Lake?"
  }
  ```

  **Response**:
  ```json
  {
    "answer": "Relevant text blocks from the PDF"
  }
  ```

## Troubleshooting and Debugging

### Accessing CrateDB Container

To access the CrateDB container for troubleshooting:
```bash
docker exec -it <cratedb-container-name> /bin/bash
```

Once inside the container, you can use CrateDB's SQL client

### Accessing Flask Web Service Container

To access the Flask web service container:
```bash
docker exec -it <flask-container-name> /bin/bash
```

You can also run a jupyter notebook from the web service: 
```bash
docker exec -it cratebot-web-1 jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```


Inside the container, you can check logs or inspect files:
```bash
cat /path/to/logs.log
```

### Viewing Container Logs

To check the logs for a specific container:
```bash
docker logs <container-name>
```

### Common Commands

- **Restart a Container**:
  ```bash
  docker restart <container-name>
  ```
- **Stop a Service**:
  ```bash
  docker-compose down
  ```

## Project Structure

```
.
├── .dockerignore              # Docker ignore file
├── .env                       # Environment variables
├── .gitignore                 # Git ignore file
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Dockerfile to build the web service container
├── readme.md                  # Project documentation (this file)
├── requirements.txt           # Python dependencies
├── app/
│   ├── app.py                 # Main Flask application file
│   ├── chatbot.py             # Logic for the chatbot functionality
│   ├── database.py            # Database connection and queries
│   ├── embeddings.py          # Handles PDF embedding and vectors
│   ├── entrypoint.sh          # Entry point initialization script 
│   ├── init_db.py             # Initializes CrateDB with data
│   ├── __init__.py            # Marks the folder as a Python package
│   ├── static/
│   │   └── style.css          # Stylesheet for the frontend
│   ├── templates/
│   │   └── index.html         # HTML template for the chatbot interface
└── data/
    └── Databricks.pdf         # Databricks certification PDF for processing

```
