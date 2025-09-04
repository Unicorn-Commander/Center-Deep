FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY search_engine.py .
COPY toolserver/ ./toolserver/
COPY templates/ ./templates/
COPY static/ ./static/
COPY searxng/ ./searxng/

# Create instance directory for database
RUN mkdir -p instance

# Expose port
EXPOSE 8888

# Environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV PORT=8888
# Center Deep is now standalone - no external dependencies
ENV CENTER_DEEP_STANDALONE=true

# Run the application
CMD ["python", "app.py"]