#!/bin/bash

# Wait for CrateDB to be ready
echo "Waiting for CrateDB to start..."
while ! nc -z cratedb 5432; do
  sleep 1
done
echo "CrateDB is up and running!"

# Run the database initialization script
echo "Initializing database..."
python app/init_db.py || {
  echo "Database initialization failed!"
  exit 1
}

# Start the Flask app
echo "Starting Flask application..."
exec flask run --host=0.0.0.0