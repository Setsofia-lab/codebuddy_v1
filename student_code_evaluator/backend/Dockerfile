# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app/backend

# Copy the requirements file into the container
# The backend uses the same requirements as the app for now
COPY ../app/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container
COPY ./app.py /app/backend/

# Copy the schema file for database initialization
COPY ./schema.sql /app/backend/

# Expose the port that the Flask app runs on
EXPOSE 5000

# Command to run the Flask application using Gunicorn
# The Flask app instance is named 'app' in app.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
