# Use Python base image
FROM python:3.10-slim
 
# Set working directory
WORKDIR /app
 
# Copy requirements file
COPY requirements.txt .
 
# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
 
# Copy the rest of the application
COPY . .
 
# Expose FastAPI port
EXPOSE 8071
 
# Command to run the FastAPI application
# Use python -m to ensure uvicorn is found in the path
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8017"]

