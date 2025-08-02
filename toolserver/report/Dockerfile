FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    aiohttp \
    requests \
    jinja2 \
    markdown \
    python-multipart

# Copy tool server files
COPY report_tool.py .
COPY __init__.py .
COPY templates/ ./templates/

# Expose port
EXPOSE 8003

# Run the tool server
CMD ["uvicorn", "report_tool:app", "--host", "0.0.0.0", "--port", "8003"]