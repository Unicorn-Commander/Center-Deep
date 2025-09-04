#!/bin/bash

# Test script to verify installer will work from GitHub
# This simulates what would happen when someone runs the one-liner

set -e

echo "========================================="
echo "Testing Center Deep One-Line Installer"
echo "========================================="
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is missing!"
        return 1
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 directory exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 directory is missing!"
        return 1
    fi
}

echo -e "${YELLOW}Checking essential files...${NC}"
check_file "install.sh"
check_file "docker-compose.center-deep.yml"
check_file "docker-compose.tools.yml"
check_file "start-toolservers.sh"
check_file "app.py"
check_file "requirements.txt"

echo
echo -e "${YELLOW}Checking essential directories...${NC}"
check_dir "templates"
check_dir "static"
check_dir "toolserver"
check_dir "toolserver/search"
check_dir "toolserver/deep-search"
check_dir "toolserver/report"
check_dir "toolserver/academic"
check_dir "searxng"
check_dir "docs"

echo
echo -e "${YELLOW}Checking tool server files...${NC}"
check_file "toolserver/search/main.py"
check_file "toolserver/search/requirements.txt"
check_file "toolserver/search/Dockerfile"
check_file "toolserver/deep-search/main.py"
check_file "toolserver/report/main.py"
check_file "toolserver/academic/main.py"

echo
echo -e "${YELLOW}Checking searxng configuration...${NC}"
check_file "searxng/settings.yml"

echo
echo -e "${YELLOW}Checking if installer is executable...${NC}"
if [ -x "install.sh" ]; then
    echo -e "${GREEN}✓${NC} install.sh is executable"
else
    echo -e "${RED}✗${NC} install.sh is not executable - fixing..."
    chmod +x install.sh
    echo -e "${GREEN}✓${NC} Fixed"
fi

if [ -x "start-toolservers.sh" ]; then
    echo -e "${GREEN}✓${NC} start-toolservers.sh is executable"
else
    echo -e "${RED}✗${NC} start-toolservers.sh is not executable - fixing..."
    chmod +x start-toolservers.sh
    echo -e "${GREEN}✓${NC} Fixed"
fi

echo
echo -e "${YELLOW}Verifying Docker Compose files syntax...${NC}"
if docker compose -f docker-compose.center-deep.yml config >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} docker-compose.center-deep.yml is valid"
else
    echo -e "${RED}✗${NC} docker-compose.center-deep.yml has syntax errors!"
fi

if docker compose -f docker-compose.tools.yml config >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} docker-compose.tools.yml is valid"
else
    echo -e "${RED}✗${NC} docker-compose.tools.yml has syntax errors!"
fi

echo
echo "========================================="
echo -e "${GREEN}Test Complete!${NC}"
echo
echo "The one-liner installer command will be:"
echo -e "${YELLOW}curl -fsSL https://raw.githubusercontent.com/Unicorn-Commander/Center-Deep/main/install.sh | bash${NC}"
echo
echo "Or for cautious users:"
echo -e "${YELLOW}wget https://raw.githubusercontent.com/Unicorn-Commander/Center-Deep/main/install.sh${NC}"
echo -e "${YELLOW}chmod +x install.sh${NC}"
echo -e "${YELLOW}./install.sh${NC}"
echo "========================================="