#!/bin/bash

# Center Deep Open Source Installation Script
# MIT Licensed - Free for everyone

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
cat << "EOF"
   ___           _            ___               
  / __\___ _ __ | |_ ___ _ __ /   \___  ___ _ __
 / /  / _ \ '_ \| __/ _ \ '__// /\ / _ \/ _ \ '_ \
/ /__|  __/ | | | ||  __/ | / /_//  __/  __/ |_) |
\____/\___|_| |_|\__\___|_| /___,' \___|\___| .__/
                                            |_|
        🦄 Privacy-First Metasearch Engine 🦄
EOF
echo -e "${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   print_warning "Running as root - this is fine for Docker-only installation"
fi

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Docker
if command_exists docker; then
    print_status "Docker is installed"
else
    print_error "Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    print_status "Docker Compose is installed"
    DOCKER_COMPOSE="docker-compose"
    if ! command_exists docker-compose; then
        DOCKER_COMPOSE="docker compose"
    fi
else
    print_error "Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Docker daemon is running
if docker info >/dev/null 2>&1; then
    print_status "Docker daemon is running"
else
    print_error "Docker daemon is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p instance
mkdir -p searxng
mkdir -p logs
mkdir -p data
print_status "Directories created"

# Generate secure random keys
generate_key() {
    openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
}

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating environment file...${NC}"
    
    FLASK_SECRET=$(generate_key)
    SEARXNG_SECRET=$(generate_key)
    
    cat > .env << EOF
# Center Deep Environment Configuration
# Generated on $(date)

# Flask Configuration
SECRET_KEY=${FLASK_SECRET}
FLASK_ENV=production

# SearXNG Configuration  
SEARXNG_SECRET=${SEARXNG_SECRET}

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Default admin credentials (CHANGE THESE!)
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASS=changeme

# Tool Server LLM Configurations (optional)
# Uncomment and add your API keys to enable AI tool servers
# SEARCH_LLM_API_KEY=your-api-key
# DEEP_SEARCH_LLM_API_KEY=your-api-key
# REPORT_LLM_API_KEY=your-api-key
# ACADEMIC_LLM_API_KEY=your-api-key
EOF
    print_status "Environment file created with secure keys"
    print_warning "Default admin credentials: admin / changeme (PLEASE CHANGE!)"
else
    print_status "Environment file already exists"
fi

# Create SearXNG settings if not exist
if [ ! -f searxng/settings.yml ]; then
    echo -e "\n${YELLOW}Creating SearXNG configuration...${NC}"
    cat > searxng/settings.yml << 'EOF'
general:
  instance_name: "Center Deep"
  contact_url: false
  enable_metrics: true

server:
  secret_key: "${SEARXNG_SECRET}"
  base_url: "http://localhost:8888/"
  image_proxy: true

ui:
  default_theme: simple
  theme_args:
    simple_style: dark

search:
  safe_search: 0
  autocomplete: "google"
  default_lang: "en"

engines:
  - name: google
    engine: google
    shortcut: g
    disabled: false
  - name: bing
    engine: bing
    shortcut: b
    disabled: false
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
    disabled: false
  - name: qwant
    engine: qwant
    shortcut: qw
    disabled: false
  - name: wikipedia
    engine: wikipedia
    shortcut: wp
    disabled: false
  - name: github
    engine: github
    shortcut: gh
    disabled: false
  - name: reddit
    engine: reddit
    shortcut: re
    disabled: false
  - name: stackoverflow
    engine: stackoverflow
    shortcut: st
    disabled: false
  - name: arxiv
    engine: arxiv
    shortcut: arx
    disabled: false
  - name: youtube
    engine: youtube
    shortcut: yt
    disabled: false
  
redis:
  url: redis://redis:6379/0
EOF
    print_status "SearXNG configuration created"
else
    print_status "SearXNG configuration already exists"
fi

# Create complete docker-compose.yml for all services
echo -e "\n${YELLOW}Creating Docker Compose configuration...${NC}"
cat > docker-compose.complete.yml << 'EOF'
version: '3.8'

services:
  # Redis for caching and statistics
  redis:
    image: redis:7-alpine
    container_name: center-deep-redis
    restart: unless-stopped
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - center-deep-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # SearXNG metasearch engine
  searxng:
    image: searxng/searxng:latest
    container_name: center-deep-searxng
    restart: unless-stopped
    volumes:
      - ./searxng:/etc/searxng:rw
    ports:
      - "8888:8080"
    networks:
      - center-deep-network
    environment:
      - BIND_ADDRESS=0.0.0.0:8080
      - INSTANCE_NAME=Center Deep
      - SEARXNG_BASE_URL=http://localhost:8888/
    depends_on:
      redis:
        condition: service_healthy

  # Center Deep main application
  center-deep:
    build: .
    container_name: center-deep-app
    restart: unless-stopped
    ports:
      - "8890:8890"
    volumes:
      - ./instance:/app/instance
      - ./static:/app/static:ro
      - ./templates:/app/templates:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - center-deep-network
    environment:
      - FLASK_ENV=production
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    env_file:
      - .env
    depends_on:
      - redis
      - searxng

  # Tool Servers (Optional - for OpenWebUI integration)
  tool-search:
    build: ./toolserver/search
    container_name: center-deep-tool-search
    restart: unless-stopped
    ports:
      - "8001:8001"
    networks:
      - center-deep-network
    environment:
      - SEARXNG_URL=http://searxng:8080
    env_file:
      - .env
    profiles:
      - tools

  tool-deep-search:
    build: ./toolserver/deep-search
    container_name: center-deep-tool-deep-search
    restart: unless-stopped
    ports:
      - "8002:8002"
    networks:
      - center-deep-network
    environment:
      - SEARXNG_URL=http://searxng:8080
    env_file:
      - .env
    profiles:
      - tools

  tool-report:
    build: ./toolserver/report
    container_name: center-deep-tool-report
    restart: unless-stopped
    ports:
      - "8003:8003"
    networks:
      - center-deep-network
    environment:
      - SEARXNG_URL=http://searxng:8080
    env_file:
      - .env
    profiles:
      - tools

  tool-academic:
    build: ./toolserver/academic
    container_name: center-deep-tool-academic
    restart: unless-stopped
    ports:
      - "8004:8004"
    networks:
      - center-deep-network
    environment:
      - SEARXNG_URL=http://searxng:8080
    env_file:
      - .env
    profiles:
      - tools

networks:
  center-deep-network:
    driver: bridge

volumes:
  redis_data:
EOF
print_status "Docker Compose configuration created"

# Create Dockerfile if not exists
if [ ! -f Dockerfile ]; then
    echo -e "\n${YELLOW}Creating Dockerfile...${NC}"
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app_opensource.py app.py
COPY templates/ templates/
COPY static/ static/

# Create instance directory
RUN mkdir -p instance

EXPOSE 8890

CMD ["python", "app.py"]
EOF
    print_status "Dockerfile created"
fi

# Build and start services
echo -e "\n${CYAN}Starting Center Deep...${NC}"

# Build images
echo -e "${YELLOW}Building Docker images...${NC}"
$DOCKER_COMPOSE -f docker-compose.complete.yml build
print_status "Docker images built"

# Start core services
echo -e "${YELLOW}Starting core services...${NC}"
$DOCKER_COMPOSE -f docker-compose.complete.yml up -d redis searxng center-deep
print_status "Core services started"

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to initialize...${NC}"
sleep 10

# Check service health
echo -e "\n${YELLOW}Checking service health...${NC}"

# Check Redis
if docker exec center-deep-redis redis-cli ping >/dev/null 2>&1; then
    print_status "Redis is healthy"
else
    print_warning "Redis health check failed (this is OK if using in-memory mode)"
fi

# Check SearXNG
if curl -s http://localhost:8888 >/dev/null; then
    print_status "SearXNG is accessible"
else
    print_warning "SearXNG is starting up..."
fi

# Check Center Deep
if curl -s http://localhost:8890 >/dev/null; then
    print_status "Center Deep is accessible"
else
    print_warning "Center Deep is starting up..."
fi

# Success message
echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}       🦄 Center Deep Installation Complete! 🦄${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo
echo -e "${CYAN}Access Points:${NC}"
echo -e "  Main App:        ${BLUE}http://localhost:8890${NC}"
echo -e "  Admin Dashboard: ${BLUE}http://localhost:8890/admin${NC}"
echo -e "  SearXNG Direct:  ${BLUE}http://localhost:8888${NC}"
echo
echo -e "${CYAN}Default Credentials:${NC}"
echo -e "  Username: ${YELLOW}admin${NC}"
echo -e "  Password: ${YELLOW}changeme${NC}"
echo -e "  ${RED}⚠ Please change these immediately!${NC}"
echo
echo -e "${CYAN}Tool Servers (Optional):${NC}"
echo -e "  To start AI tool servers for OpenWebUI:"
echo -e "  ${BLUE}$DOCKER_COMPOSE -f docker-compose.complete.yml --profile tools up -d${NC}"
echo
echo -e "${CYAN}Management Commands:${NC}"
echo -e "  View logs:    ${BLUE}$DOCKER_COMPOSE -f docker-compose.complete.yml logs -f${NC}"
echo -e "  Stop all:     ${BLUE}$DOCKER_COMPOSE -f docker-compose.complete.yml down${NC}"
echo -e "  Restart app:  ${BLUE}$DOCKER_COMPOSE -f docker-compose.complete.yml restart center-deep${NC}"
echo
echo -e "${GREEN}Enjoy your privacy-first search experience! 🌊${NC}"