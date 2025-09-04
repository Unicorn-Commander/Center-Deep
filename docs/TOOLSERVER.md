# Center-Deep Tool Servers

The Center-Deep Tool Servers provide specialized AI-powered tools for search, analysis, and content generation. Each tool server is a containerized microservice that exposes OpenAI-compatible APIs.

## Available Tool Servers

### 1. Search Tool (Port 11001)
**Container:** `center-deep-tool-search`
**Purpose:** Basic web search functionality using SearXNG
**Features:**
- Multi-engine web search
- Category-based filtering (general, images, videos, news, academic)
- Configurable result count
- OpenAI-compatible API

### 2. Deep Search Tool (Port 11002)
**Container:** `center-deep-tool-deep-search`
**Purpose:** Advanced multi-source search with content extraction
**Features:**
- Multi-level search depth (1-3 levels)
- Content extraction from web pages
- Source-specific searches (GitHub, Reddit, StackOverflow, etc.)
- Rich metadata and structured results
- Follow-up query generation

### 3. Report Generator (Port 11003)
**Container:** `center-deep-tool-report`
**Purpose:** Professional report generation with citations
**Features:**
- Multiple report types (executive, technical, analytical, business)
- Automatic citation generation
- Template-based formatting
- Multiple output formats (Markdown, HTML, JSON)
- Data source integration

### 4. Academic Research Tool (Port 11004)
**Container:** `center-deep-tool-academic`
**Purpose:** Academic paper generation with proper formatting
**Features:**
- Multiple paper types (research, review, survey, position)
- Multiple citation styles (APA, MLA, Chicago, IEEE)
- Structured academic format
- Bibliography generation
- Keyword management

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Center-Deep main application running
- SearXNG service running (optional but recommended)

### Starting Tool Servers
```bash
# Make the script executable
chmod +x start-toolservers.sh

# Start all tool servers
./start-toolservers.sh
```

### Alternative Manual Start
```bash
# Build and start all services
docker-compose -f docker-compose.tools.yml up -d

# Build without cache (if needed)
docker-compose -f docker-compose.tools.yml build --no-cache

# View logs
docker-compose -f docker-compose.tools.yml logs -f
```

## API Usage

All tool servers expose OpenAI-compatible endpoints:

### Base Endpoints
- **Health Check:** `GET /health`
- **Tool Information:** `GET /v1/tools`
- **Chat Completions:** `POST /v1/chat/completions`
- **Tool Execution:** `POST /v1/tools/execute`

### Example: Basic Search
```bash
curl -X POST http://localhost:11001/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your-api-key' \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Search for latest AI news"}],
    "tools": [{"type": "function", "function": {"name": "search"}}]
  }'
```

### Example: Direct Tool Execution
```bash
curl -X POST http://localhost:11001/v1/tools/execute \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your-api-key' \
  -d '{
    "name": "search",
    "arguments": {
      "query": "artificial intelligence trends 2024",
      "category": "general",
      "num_results": 10
    }
  }'
```

### Example: Deep Search with Content Extraction
```bash
curl -X POST http://localhost:11002/v1/tools/execute \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your-api-key' \
  -d '{
    "name": "deep_search",
    "arguments": {
      "query": "machine learning optimization techniques",
      "depth": 2,
      "sources": ["github", "stackoverflow"],
      "extract_content": true
    }
  }'
```

### Example: Report Generation
```bash
curl -X POST http://localhost:11003/v1/tools/execute \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your-api-key' \
  -d '{
    "name": "generate_report",
    "arguments": {
      "topic": "Impact of AI on Modern Business",
      "report_type": "executive",
      "format": "markdown"
    }
  }'
```

### Example: Academic Paper Generation
```bash
curl -X POST http://localhost:11004/v1/tools/execute \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your-api-key' \
  -d '{
    "name": "academic_report",
    "arguments": {
      "topic": "Deep Learning Applications in Healthcare",
      "paper_type": "research",
      "citation_style": "APA",
      "keywords": ["deep learning", "healthcare", "medical imaging", "AI"]
    }
  }'
```

## Configuration

### Environment Variables

Each tool server accepts these common environment variables:

- **SEARXNG_URL**: URL of SearXNG service (default: http://unicorn-searxng:8080)
- **CENTER_DEEP_URL**: URL of Center-Deep main application (default: http://center-deep:8888)
- **LLM_API_BASE**: Base URL for LLM API (optional)
- **LLM_API_KEY**: API key for LLM service (optional)
- **LLM_MODEL**: Model to use for LLM enhancement (default varies by tool)
- **TOOL_TYPE**: Type identifier for the tool

### Customization

You can customize the configuration by:

1. Modifying `docker-compose.tools.yml`
2. Setting environment variables in your shell
3. Creating a `.env` file with your settings

Example `.env` file:
```env
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4
SEARXNG_URL=http://localhost:8888
```

## Monitoring and Management

### Service Status
```bash
# Check running containers
docker ps | grep center-deep-tool

# View specific service logs
docker logs center-deep-tool-search

# Check service health
curl http://localhost:11001/health
```

### Performance Monitoring
Each tool server exposes basic metrics at `/metrics` endpoint (Prometheus format):
```bash
curl http://localhost:11001/metrics
```

### Troubleshooting

#### Common Issues

1. **Network connectivity issues**
   - Ensure `unicorn-network` exists: `docker network create unicorn-network`
   - Check if SearXNG is running: `docker ps | grep searxng`

2. **Port conflicts**
   - Default ports: 11001-11004
   - Modify ports in `docker-compose.tools.yml` if needed

3. **Service won't start**
   - Check logs: `docker logs center-deep-tool-{service}`
   - Rebuild images: `docker-compose -f docker-compose.tools.yml build --no-cache`

4. **Search functionality not working**
   - Verify SearXNG is accessible
   - Check SEARXNG_URL environment variable

### Development

#### Local Development
```bash
# Run individual tool server locally
cd toolserver/search
python search_tool.py

# Install development dependencies
pip install fastapi uvicorn aiohttp pydantic
```

#### Adding New Tools

1. Create a new directory in `toolserver/`
2. Implement FastAPI application with required endpoints
3. Create Dockerfile
4. Add service to `docker-compose.tools.yml`
5. Update startup script

## Integration with Center-Deep

The tool servers integrate seamlessly with Center-Deep:

1. **Network Integration**: All services share the `unicorn-network`
2. **Service Discovery**: Tools can communicate with Center-Deep and SearXNG
3. **API Compatibility**: OpenAI-compatible APIs for easy integration
4. **Configuration**: Centralized configuration through environment variables

## Security Considerations

- API key validation is implemented for all endpoints
- CORS is configured for cross-origin requests
- Services run in isolated containers
- No sensitive data is logged by default

For production deployment, consider:
- Using proper API key management
- Implementing rate limiting
- Adding HTTPS termination
- Configuring proper firewall rules
- Setting up monitoring and alerting

## Support

For issues and questions:
1. Check the logs: `docker logs center-deep-tool-{service}`
2. Verify configuration: `docker-compose -f docker-compose.tools.yml config`
3. Test individual endpoints with curl
4. Review this documentation for common solutions