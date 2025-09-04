#!/bin/bash

# Center Deep - Universal Installation Script
# Detects OS and installs Docker if needed
# Built by Magic Unicorn Unconventional Technology & Stuff Inc

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
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
        🦄 The One-Click Privacy Search Engine 🦄
        
    Built by Magic Unicorn Unconventional Technology
EOF
echo -e "${NC}"

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
            VER=$VERSION_ID
        else
            OS=$(uname -s)
            VER=$(uname -r)
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        OS="macos"
        VER=$(sw_vers -productVersion)
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        OS="windows"
        VER=$(ver)
    else
        OS="unknown"
        VER="unknown"
    fi
}

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

# Function to install Docker on Ubuntu/Debian
install_docker_debian() {
    echo -e "${YELLOW}Installing Docker on Debian/Ubuntu...${NC}"
    
    # Update package index
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    sudo mkdir -m 0755 -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_status "Docker installed successfully on Debian/Ubuntu"
    print_warning "You may need to log out and back in for group changes to take effect"
}

# Function to install Docker on RHEL/CentOS/Fedora
install_docker_rhel() {
    echo -e "${YELLOW}Installing Docker on RHEL/CentOS/Fedora...${NC}"
    
    # Remove old versions
    sudo dnf remove -y docker \
                      docker-client \
                      docker-client-latest \
                      docker-common \
                      docker-latest \
                      docker-latest-logrotate \
                      docker-logrotate \
                      docker-engine
    
    # Set up repository
    sudo dnf -y install dnf-plugins-core
    sudo dnf config-manager --add-repo https://download.docker.com/linux/$OS/docker-ce.repo
    
    # Install Docker Engine
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_status "Docker installed successfully on RHEL/CentOS/Fedora"
    print_warning "You may need to log out and back in for group changes to take effect"
}

# Function to install Docker on macOS
install_docker_macos() {
    echo -e "${YELLOW}Installing Docker on macOS...${NC}"
    
    # Check if Homebrew is installed
    if ! command_exists brew; then
        print_info "Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install Docker Desktop using Homebrew
    brew install --cask docker
    
    print_status "Docker Desktop installed successfully on macOS"
    print_warning "Please start Docker Desktop from Applications folder"
    print_info "Waiting for Docker Desktop to start..."
    
    # Wait for Docker to start
    while ! docker system info > /dev/null 2>&1; do
        sleep 2
        echo -n "."
    done
    echo
}

# Function to install Docker on Windows (WSL2)
install_docker_windows() {
    echo -e "${YELLOW}Docker installation on Windows${NC}"
    echo
    print_info "For Windows, please install Docker Desktop manually:"
    echo "1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/"
    echo "2. Run the installer"
    echo "3. Enable WSL2 integration"
    echo "4. Start Docker Desktop"
    echo "5. Re-run this script in WSL2 or Git Bash"
    echo
    read -p "Press Enter once Docker Desktop is installed and running..."
}

# Main installation logic
echo -e "${MAGENTA}Detecting operating system...${NC}"
detect_os
print_info "Detected OS: $OS (Version: $VER)"

# Check if Docker is already installed
if command_exists docker; then
    print_status "Docker is already installed"
    docker_version=$(docker --version)
    print_info "Docker version: $docker_version"
else
    print_warning "Docker is not installed"
    
    # Ask user if they want to install Docker
    echo -e "${YELLOW}Would you like to install Docker automatically? (y/n)${NC}"
    read -p "> " install_docker
    
    if [[ "$install_docker" == "y" ]] || [[ "$install_docker" == "Y" ]]; then
        case "$OS" in
            ubuntu|debian)
                install_docker_debian
                ;;
            centos|rhel|fedora)
                install_docker_rhel
                ;;
            macos)
                install_docker_macos
                ;;
            windows)
                install_docker_windows
                ;;
            *)
                print_error "Unsupported OS: $OS"
                echo "Please install Docker manually from: https://docs.docker.com/get-docker/"
                exit 1
                ;;
        esac
    else
        print_error "Docker is required to run Center Deep"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
fi

# Check Docker Compose
echo -e "\n${MAGENTA}Checking Docker Compose...${NC}"
if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    print_status "Docker Compose is installed"
    if command_exists docker-compose; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi
else
    print_error "Docker Compose is not installed"
    
    # Docker Compose should come with Docker Desktop on Mac/Windows
    # On Linux, it might need separate installation
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]] || [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "fedora" ]]; then
        print_info "Installing Docker Compose plugin..."
        sudo apt-get update && sudo apt-get install -y docker-compose-plugin || \
        sudo dnf install -y docker-compose-plugin
    fi
fi

# Check if Docker daemon is running
echo -e "\n${MAGENTA}Checking Docker daemon...${NC}"
if docker info >/dev/null 2>&1; then
    print_status "Docker daemon is running"
else
    print_warning "Docker daemon is not running"
    
    if [[ "$OS" == "macos" ]] || [[ "$OS" == "windows" ]]; then
        print_info "Please start Docker Desktop"
        print_info "Waiting for Docker to start..."
        while ! docker info >/dev/null 2>&1; do
            sleep 2
            echo -n "."
        done
        echo
        print_status "Docker daemon is now running"
    else
        print_info "Starting Docker daemon..."
        sudo systemctl start docker
        print_status "Docker daemon started"
    fi
fi

# Create necessary directories
echo -e "\n${MAGENTA}Setting up Center Deep...${NC}"
mkdir -p instance searxng logs data
print_status "Directories created"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating minimal environment configuration...${NC}"
    cat > .env << 'EOF'
# Center Deep Initial Configuration
# Full configuration will be done via web interface

# Redis Configuration (port 6385 to avoid conflicts)
USE_EXTERNAL_REDIS=false
REDIS_PORT=6385

# Temporary secret key (will be replaced during setup)
EOF
    
    # Generate secure key
    if command_exists openssl; then
        echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
        echo "SEARXNG_SECRET_KEY=$(openssl rand -hex 32)" >> .env
    else
        echo "SECRET_KEY=$(head -c 32 /dev/urandom | base64)" >> .env
        echo "SEARXNG_SECRET_KEY=$(head -c 32 /dev/urandom | base64)" >> .env
    fi
    
    # Mark setup as incomplete
    echo "SETUP_COMPLETE=false" >> .env
    
    print_status "Initial configuration created"
    print_info "You'll complete setup via the web interface"
else
    print_status "Environment configuration already exists"
fi

# Start Center Deep
echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}           🚀 Starting Center Deep 🚀${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

# Pull and start services
echo -e "\n${YELLOW}Starting Center Deep (standalone - no external dependencies)...${NC}"
$DOCKER_COMPOSE up -d

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to initialize...${NC}"
sleep 10

# Check service health
echo -e "\n${MAGENTA}Checking service health...${NC}"

# Check main app
if curl -s http://localhost:8888 >/dev/null 2>&1; then
    print_status "Center Deep is running"
else
    print_warning "Center Deep is starting up..."
fi

# Check Redis
if docker exec center-deep-redis redis-cli ping >/dev/null 2>&1; then
    print_status "Redis cache is healthy"
else
    print_warning "Redis is initializing..."
fi

# Check if setup is needed
if grep -q "SETUP_COMPLETE=false" .env 2>/dev/null; then
    # First time setup
    echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}       🦄 Center Deep Ready for Setup! 🦄${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo -e "${CYAN}🎉 Installation Complete!${NC}"
    echo
    echo -e "${YELLOW}➡️  Next Step: Complete Setup${NC}"
    echo -e "   Visit: ${BLUE}http://localhost:8888${NC}"
    echo
    echo -e "   The setup wizard will guide you through:"
    echo -e "   • Creating your admin account"
    echo -e "   • Selecting search engines"
    echo -e "   • Configuring privacy settings"
    echo -e "   • Choosing your theme"
    echo
    echo -e "   ${GREEN}No command line configuration needed!${NC}"
else
    # Already configured
    echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}       🦄 Center Deep Successfully Started! 🦄${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo -e "${CYAN}Access Points:${NC}"
    echo -e "  🔍 Search Engine:  ${BLUE}http://localhost:8888${NC}"
    echo -e "  ⚙️  Admin Panel:    ${BLUE}http://localhost:8888/admin${NC}"
fi
echo
echo -e "${CYAN}Tool Servers (Optional):${NC}"
echo -e "  To enable AI tool servers for OpenWebUI:"
echo -e "  ${BLUE}./start-toolservers.sh${NC}"
echo -e "  Or manually: ${BLUE}$DOCKER_COMPOSE -f docker-compose.tools.yml up -d${NC}"
echo
echo -e "${CYAN}Useful Commands:${NC}"
echo -e "  View logs:    ${BLUE}$DOCKER_COMPOSE logs -f${NC}"
echo -e "  Stop all:     ${BLUE}$DOCKER_COMPOSE down${NC}"
echo -e "  Restart:      ${BLUE}$DOCKER_COMPOSE restart${NC}"
echo -e "  Update:       ${BLUE}git pull && $DOCKER_COMPOSE up -d --build${NC}"
echo
echo -e "${GREEN}Enjoy your privacy-first search experience! 🌊${NC}"
echo -e "${MAGENTA}Built with ❤️ by Magic Unicorn Unconventional Technology & Stuff Inc${NC}"
echo -e "${MAGENTA}https://magicunicorn.tech | https://unicorncommander.com${NC}"