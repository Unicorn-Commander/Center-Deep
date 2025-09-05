FROM python:3.11-alpine

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    libxml2-dev \
    libxslt-dev \
    git \
    nodejs \
    npm \
    redis \
    make

# Create user
RUN addgroup -S searxng && adduser -S -G searxng searxng

# Set working directory
WORKDIR /usr/local/center-deep

# Copy source code including center_deep_webapp.py
COPY --chown=searxng:searxng . /usr/local/center-deep

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    Flask-Login==0.6.3 \
    Flask-SQLAlchemy==3.1.1 \
    python-dotenv==1.0.0

# Skip theme building for now - themes are already built in the repo

# Create necessary directories
RUN mkdir -p /etc/searxng /var/log/searxng && \
    chown -R searxng:searxng /etc/searxng /var/log/searxng

# Configuration is handled by volume mount in docker-compose

# Set environment variables
ENV SEARXNG_SETTINGS_PATH=/etc/searxng/settings.yml \
    SEARXNG_BIND_ADDRESS=0.0.0.0 \
    SEARXNG_PORT=8080

# Switch to non-root user
USER searxng

# Expose port
EXPOSE 8080

# Run SearXNG webapp with Center Deep branding
CMD ["python", "-m", "searx.webapp"]