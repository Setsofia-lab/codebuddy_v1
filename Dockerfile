# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY student_code_evaluator/backend/requirements.txt ./backend_requirements.txt
COPY student_code_evaluator/app/requirements.txt ./frontend_requirements.txt

# Install Python dependencies for both backend and frontend
RUN pip install --no-cache-dir -r backend_requirements.txt && \
    pip install --no-cache-dir -r frontend_requirements.txt

# Copy the entire application
COPY student_code_evaluator/ ./student_code_evaluator/

# Set proper permissions for the backend directory
RUN chmod 755 /app/student_code_evaluator/backend

# Set environment variable to avoid Streamlit asking for a browser
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Create a startup script that runs both services properly
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting CodeBuddy services..."\n\
\n\
# Initialize database first\n\
cd /app/student_code_evaluator/backend\n\
python -c "from app import init_db; init_db()"\n\
\n\
# Start backend in background\n\
echo "Starting Flask backend on port 5000..."\n\
cd /app/student_code_evaluator/backend\n\
python app.py &\n\
BACKEND_PID=$!\n\
\n\
# Wait for backend to start\n\
sleep 5\n\
\n\
# Start frontend\n\
echo "Starting Streamlit frontend on port 8501..."\n\
cd /app/student_code_evaluator/app\n\
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true &\n\
FRONTEND_PID=$!\n\
\n\
echo "Both services started successfully!"\n\
echo "Backend: http://localhost:5000"\n\
echo "Frontend: http://localhost:8501"\n\
\n\
# Wait for both processes\n\
wait $BACKEND_PID $FRONTEND_PID' > /app/start.sh && chmod +x /app/start.sh

# Expose ports for both backend and frontend
EXPOSE 5000 8501

# Start both services
CMD ["/app/start.sh"] 