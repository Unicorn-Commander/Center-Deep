from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import aiohttp
import asyncio
from datetime import datetime
import json

app = FastAPI(
    title="Center Deep Search Tool",
    version="1.0.0",
    description="Basic search tool for Center Deep"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
SEARXNG_URL = os.getenv('SEARXNG_URL', 'http://searxng:8080')
CENTER_DEEP_URL = os.getenv('CENTER_DEEP_URL', 'http://center-deep:8890')
LLM_API_BASE = os.getenv('LLM_API_BASE', '')
LLM_API_KEY = os.getenv('LLM_API_KEY', '')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
TOOL_NAME = "search"

# Pydantic models
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4000
    stream: Optional[bool] = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Any] = None

class ToolExecutionRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

# Tool definition
SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search",
        "description": "Search the web using Center Deep's multi-engine search",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "category": {
                    "type": "string",
                    "enum": ["general", "images", "videos", "news", "academic"],
                    "description": "Search category",
                    "default": "general"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }
}

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "tool": TOOL_NAME,
        "version": "1.0.0",
        "llm_configured": bool(LLM_API_BASE)
    }

# Tool info endpoint
@app.get("/v1/tools")
async def get_tools():
    return {
        "tools": [SEARCH_TOOL],
        "server": "Center Deep Search Tool"
    }

# Search execution
async def perform_search(query: str, category: str = "general", num_results: int = 10) -> Dict[str, Any]:
    """Execute search against SearXNG"""
    
    # Map categories
    category_map = {
        'general': '',
        'images': 'images',
        'videos': 'videos',
        'news': 'news',
        'academic': 'science'
    }
    
    searxng_category = category_map.get(category, '')
    
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'q': query,
                'format': 'json',
                'categories': searxng_category,
                'language': 'en',
                'safesearch': 0
            }
            
            async with session.get(f"{SEARXNG_URL}/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Format results
                    results = []
                    for idx, result in enumerate(data.get('results', [])[:num_results]):
                        results.append({
                            'title': result.get('title', 'No title'),
                            'url': result.get('url', ''),
                            'content': result.get('content', ''),
                            'engine': result.get('engine', 'unknown'),
                            'score': result.get('score', 0),
                            'publishedDate': result.get('publishedDate', ''),
                            'rank': idx + 1
                        })
                    
                    return {
                        'status': 'success',
                        'query': query,
                        'category': category,
                        'results': results,
                        'metadata': {
                            'total_results': len(data.get('results', [])),
                            'num_returned': len(results),
                            'response_time': data.get('response_time', 0),
                            'engines_used': list(set(r.get('engine', 'unknown') for r in results))
                        }
                    }
                else:
                    return {
                        'status': 'error',
                        'error': f'Search failed with status {response.status}',
                        'query': query
                    }
                    
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'query': query
        }

# OpenAI-compatible chat endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI API v1 compatible endpoint"""
    
    # Check if this is a tool call
    if request.tools:
        # Return tool selection
        return {
            "id": f"chatcmpl-{datetime.utcnow().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": f"call_{datetime.utcnow().timestamp()}",
                        "type": "function",
                        "function": {
                            "name": "search",
                            "arguments": json.dumps({
                                "query": "What would you like to search for?"
                            })
                        }
                    }]
                },
                "finish_reason": "tool_calls"
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
    
    # Regular response
    return {
        "id": f"chatcmpl-{datetime.utcnow().timestamp()}",
        "object": "chat.completion",
        "created": int(datetime.utcnow().timestamp()),
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Search tool is ready. Use the tools parameter to perform searches."
            },
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

# Tool execution endpoint
@app.post("/v1/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Execute the search tool"""
    
    if request.name != "search":
        raise HTTPException(status_code=400, detail=f"Unknown tool: {request.name}")
    
    # Extract arguments
    query = request.arguments.get('query', '')
    category = request.arguments.get('category', 'general')
    num_results = request.arguments.get('num_results', 10)
    
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    # Perform search
    results = await perform_search(query, category, num_results)
    
    # If LLM is configured, enhance results
    if LLM_API_BASE and results['status'] == 'success':
        # Could add LLM processing here to summarize or enhance results
        results['llm_enhanced'] = False
        results['llm_model'] = LLM_MODEL
    
    return results

# Prometheus metrics endpoint (stub for now)
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    # Basic metrics in Prometheus format
    metrics = [
        f"# HELP search_requests_total Total number of search requests",
        f"# TYPE search_requests_total counter",
        f"search_requests_total 0",
        f"# HELP search_response_time_seconds Search response time in seconds",
        f"# TYPE search_response_time_seconds histogram",
        f"search_response_time_seconds_bucket{{le=\"1.0\"}} 0",
        f"search_response_time_seconds_bucket{{le=\"2.0\"}} 0",
        f"search_response_time_seconds_bucket{{le=\"5.0\"}} 0",
        f"search_response_time_seconds_bucket{{le=\"+Inf\"}} 0",
        f"search_response_time_seconds_sum 0",
        f"search_response_time_seconds_count 0"
    ]
    return "\n".join(metrics)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)