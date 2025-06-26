# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app code into the container
COPY streamlit_app.py .

# Expose the port that Streamlit runs on
EXPOSE 8501

# Set environment variable to avoid Streamlit asking for a browser
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Command to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"] 