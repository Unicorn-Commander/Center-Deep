FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    aiohttp \
    requests

# Copy tool server files
COPY search_tool.py .
COPY __init__.py .

# Expose port
EXPOSE 8001

# Run the tool server
CMD ["uvicorn", "search_tool:app", "--host", "0.0.0.0", "--port", "8001"]