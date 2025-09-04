#!/bin/bash

# Center-Deep Tool Servers Startup Script
# Starts all tool servers on high ports (11001-11004) with LLM models

echo "🚀 Starting Center-Deep Tool Servers with LLM Models"
echo "=============================================================="
echo ""
echo "📊 Tool Server Configuration:"
echo "- Search Tool (Port 11001): Basic web search functionality"
echo "- Deep Search (Port 11002): Advanced multi-source search with content extraction"  
echo "- Report Generator (Port 11003): Professional report generation with citations"
echo "- Academic Research (Port 11004): Academic paper generation with proper formatting"
echo ""
echo "🔧 Supporting Services:"
echo "- SearXNG: Multi-engine search aggregation"
echo "- Center-Deep: Main application backend"
echo "- Optional: LLM services for enhanced functionality"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! docker ps | grep -q center-deep; then
    echo "⚠️  Warning: Center-Deep service is not running!"
    echo "Please start Center-Deep first with: docker-compose up -d"
fi

if ! docker ps | grep -q searxng; then
    echo "⚠️  Warning: SearXNG service is not running!"
    echo "Tool servers will still work but search functionality may be limited"
fi

echo "✅ Prerequisites checked"
echo ""

# Start the tool servers
echo "🏗️  Building and starting tool servers..."
cd "$(dirname "$0")"

# Build if needed
docker-compose -f docker-compose.tools.yml build --no-cache

# Start services
docker-compose -f docker-compose.tools.yml up -d

# Wait for services to start
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 15

# Check status
echo ""
echo "📋 Tool Server Status:"
echo "======================"

services=("center-deep-tool-search:11001:Search" "center-deep-tool-deep-search:11002:Deep_Search" "center-deep-tool-report:11003:Report_Generator" "center-deep-tool-academic:11004:Academic_Research")

for service_info in "${services[@]}"; do
    IFS=':' read -r container port model <<< "$service_info"
    
    if docker ps | grep -q "$container"; then
        status="🟢 Running"
    else
        status="🔴 Stopped"
    fi
    
    echo "$status - $container (Port $port) - $model"
done

echo ""
echo "🧪 Testing Tool Server Endpoints:"
echo "=================================="

for service_info in "${services[@]}"; do
    IFS=':' read -r container port model <<< "$service_info"
    
    echo -n "Testing port $port... "
    if timeout 10 curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "⚠️  Not responding (may still be initializing)"
    fi
done

echo ""
echo "🎯 Ready to Use!"
echo "================"
echo ""
echo "📡 OpenAI-Compatible Endpoints:"
echo "- Search Tool: http://localhost:11001/v1/chat/completions"
echo "- Deep Search: http://localhost:11002/v1/chat/completions" 
echo "- Report Generator: http://localhost:11003/v1/chat/completions"
echo "- Academic Research: http://localhost:11004/v1/chat/completions"
echo ""
echo "🔧 Management:"
echo "- Center-Deep Admin: http://localhost:8888"
echo "- SearXNG Search: http://localhost:8888"
echo ""
echo "📖 Usage Examples:"
echo "curl -X POST http://localhost:11001/v1/chat/completions \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer \${API_KEY}' \\"
echo "  -d '{\"model\":\"gpt-3.5-turbo\",\"messages\":[{\"role\":\"user\",\"content\":\"Search for latest AI news\"}]}'"
echo ""
echo "📊 Monitor with:"
echo "- docker logs center-deep-tool-search"
echo "- docker logs center-deep-tool-deep-search" 
echo "- docker logs center-deep-tool-report"
echo "- docker logs center-deep-tool-academic"
echo ""
echo "🎉 Center-Deep Pro Tool Servers are ready!"