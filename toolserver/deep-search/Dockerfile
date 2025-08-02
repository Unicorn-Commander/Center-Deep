FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    aiohttp \
    requests \
    beautifulsoup4 \
    lxml \
    trafilatura

# Copy tool server files
COPY deep_search_tool.py .
COPY __init__.py .

# Expose port
EXPOSE 8002

# Run the tool server
CMD ["uvicorn", "deep_search_tool:app", "--host", "0.0.0.0", "--port", "8002"]