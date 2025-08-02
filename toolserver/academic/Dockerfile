FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    aiohttp \
    requests \
    scholarly \
    bibtexparser

# Copy tool server files
COPY academic_tool.py .
COPY __init__.py .

# Expose port
EXPOSE 8004

# Run the tool server
CMD ["uvicorn", "academic_tool:app", "--host", "0.0.0.0", "--port", "8004"]