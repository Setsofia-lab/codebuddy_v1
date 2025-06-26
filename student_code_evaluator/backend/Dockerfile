# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container
COPY ./app.py /app/
COPY ./schema.sql /app/

# Create a startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Initializing CodeBuddy Backend..."\n\
\n\
# Initialize database\n\
python -c "from app import init_db; init_db()"\n\
\n\
echo "Starting Flask backend on port 5000..."\n\
python app.py' > /app/start.sh && chmod +x /app/start.sh

# Expose the port that the Flask app runs on
EXPOSE 5000

# Start the application
CMD ["/app/start.sh"]
