FROM python:3.9

# Install dependencies
RUN apt-get update && apt-get install -y netcat-openbsd

# Set environment variables
ENV FLASK_APP=app.app
ENV FLASK_ENV=development 

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --timeout 100

# Copy application code and entrypoint script
COPY . /app
WORKDIR /app

# Set the entrypoint script as executable
# Copy the entrypoint.sh file
COPY app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/app/entrypoint.sh"]

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]

# docker build -t your-app-name .
# docker run --env-file .env -p 5000:5000 your-app-name