#!/bin/bash

# Center Deep Installation Script
# Magic Unicorn Unconventional Technology & Stuff Inc.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════"
echo "       Center Deep - Professional Search Platform"
echo "       Magic Unicorn Unconventional Technology & Stuff Inc."
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Please do not run this script as root!${NC}"
   exit 1
fi

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
else
    print_error "Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check Python (optional for local development)
if command_exists python3; then
    print_status "Python 3 is installed (optional)"
else
    print_info "Python 3 not found (only needed for local development)"
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
print_status "Directories created"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating environment file...${NC}"
    cat > .env << 'EOF'
# Center Deep Environment Configuration

# Flask Configuration
SECRET_KEY=change-this-to-a-random-secret-key-in-production
FLASK_ENV=production

# SearXNG Configuration
SEARXNG_SECRET=change-this-to-a-random-secret

# Redis Configuration (optional)
REDIS_HOST=redis
REDIS_PORT=6379

# Tool Server LLM Configurations (optional)
# Add your LLM API keys here if you want to use them
# SEARCH_LLM_API_BASE=https://api.openai.com/v1
# SEARCH_LLM_API_KEY=sk-...
# SEARCH_LLM_MODEL=gpt-3.5-turbo

# DEEP_SEARCH_LLM_API_BASE=https://api.openai.com/v1
# DEEP_SEARCH_LLM_API_KEY=sk-...
# DEEP_SEARCH_LLM_MODEL=gpt-4

# REPORT_LLM_API_BASE=https://api.openai.com/v1
# REPORT_LLM_API_KEY=sk-...
# REPORT_LLM_MODEL=gpt-4

# ACADEMIC_LLM_API_BASE=https://api.openai.com/v1
# ACADEMIC_LLM_API_KEY=sk-...
# ACADEMIC_LLM_MODEL=gpt-4
EOF
    print_status "Environment file created"
    print_info "Please edit .env file to add your API keys and change secret keys"
else
    print_status "Environment file already exists"
fi

# Create SearXNG settings if not exist
if [ ! -f searxng/settings.yml ]; then
    echo -e "\n${YELLOW}Creating SearXNG configuration...${NC}"
    cat > searxng/settings.yml << 'EOF'
general:
  instance_name: "Center Deep Search"
  contact_url: false
  enable_metrics: true

server:
  secret_key: "change-this-secret-key"
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
  - name: bing
    engine: bing
    shortcut: b
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
  - name: wikipedia
    engine: wikipedia
    shortcut: wp
  - name: github
    engine: github
    shortcut: gh
  - name: reddit
    engine: reddit
    shortcut: re
  - name: stackoverflow
    engine: stackoverflow
    shortcut: st
EOF
    print_status "SearXNG configuration created"
else
    print_status "SearXNG configuration already exists"
fi

# Build Docker images
echo -e "\n${YELLOW}Building Docker images...${NC}"

# Build main application
echo "Building Center Deep application..."
docker build -t center-deep:latest . || {
    print_error "Failed to build Center Deep image"
    exit 1
}
print_status "Center Deep image built"

# Build tool servers
echo -e "\n${YELLOW}Building tool server images...${NC}"

for tool in search deep-search report academic; do
    if [ -d "toolserver/$tool" ]; then
        echo "Building $tool tool server..."
        docker build -t center-deep-tool-$tool:latest ./toolserver/$tool || {
            print_error "Failed to build $tool tool server"
            continue
        }
        print_status "$tool tool server built"
    else
        print_info "Skipping $tool tool server (directory not found)"
    fi
done

# Start services
echo -e "\n${YELLOW}Starting services...${NC}"

# Start main services (Redis and SearXNG)
docker-compose up -d || {
    print_error "Failed to start main services"
    exit 1
}
print_status "Main services started"

# Optional: Start tool servers
echo -e "\n${YELLOW}Tool servers can be started from the admin dashboard${NC}"
echo "Or manually with: docker-compose -f docker-compose.tools.yml up -d"

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "\n${YELLOW}Checking service health...${NC}"

# Check Redis
if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
    print_status "Redis is healthy"
else
    print_error "Redis health check failed"
fi

# Check SearXNG
if curl -s http://localhost:8888 >/dev/null; then
    print_status "SearXNG is accessible"
else
    print_error "SearXNG is not accessible"
fi

# Run the Center Deep application
echo -e "\n${YELLOW}Starting Center Deep application...${NC}"

# For development (local Python)
if command_exists python3 && [ -f "app.py" ]; then
    echo "Starting in development mode..."
    
    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    
    # Activate and install dependencies
    source venv/bin/activate
    pip install -r requirements.txt >/dev/null 2>&1
    print_status "Python dependencies installed"
    
    echo -e "\n${GREEN}Installation complete!${NC}"
    echo -e "\n${YELLOW}Starting Center Deep...${NC}"
    echo "Access the application at: http://localhost:8890"
    echo "Default login: ucadmin / MagicUnicorn!8-)"
    echo -e "\n${BLUE}Press Ctrl+C to stop${NC}\n"
    
    python app.py
else
    # For production (Docker only)
    docker run -d \
        --name center-deep \
        --network unicorn-network \
        -p 8890:8890 \
        -v $(pwd)/instance:/app/instance \
        -v /var/run/docker.sock:/var/run/docker.sock \
        --env-file .env \
        center-deep:latest || {
        print_error "Failed to start Center Deep container"
        exit 1
    }
    
    print_status "Center Deep container started"
    
    echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Installation complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo "Access the application at: http://localhost:8890"
    echo "Default login: ucadmin / MagicUnicorn!8-)"
    echo
    echo "Admin Dashboard: http://localhost:8890/admin"
    echo "SearXNG: http://localhost:8888"
    echo
    echo "To view logs: docker logs center-deep"
    echo "To stop: docker stop center-deep"
    echo
    echo -e "${YELLOW}Tool servers can be managed from the admin dashboard${NC}"
fi