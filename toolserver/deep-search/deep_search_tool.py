from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import aiohttp
import asyncio
from datetime import datetime
import json
from bs4 import BeautifulSoup
import trafilatura

app = FastAPI(
    title="Center Deep Deep Search Tool",
    version="1.0.0",
    description="Deep search with multi-source analysis and content extraction"
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
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')
TOOL_NAME = "deep_search"

# Tool definition
DEEP_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "deep_search",
        "description": "Perform comprehensive multi-source search with content extraction and analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for deep analysis"
                },
                "depth": {
                    "type": "integer",
                    "description": "How many levels deep to search (1-3)",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 3
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific sources to focus on (e.g., 'github', 'reddit', 'stackoverflow')"
                },
                "extract_content": {
                    "type": "boolean",
                    "description": "Whether to extract and analyze full content from pages",
                    "default": True
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
        "tools": [DEEP_SEARCH_TOOL],
        "server": "Center Deep Deep Search Tool"
    }

async def extract_page_content(url: str) -> Dict[str, Any]:
    """Extract content from a webpage"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Extract with trafilatura for clean text
                    extracted = trafilatura.extract(
                        html,
                        include_links=True,
                        include_tables=True,
                        deduplicate=True
                    )
                    
                    # Also parse with BeautifulSoup for structure
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Extract metadata
                    title = soup.find('title')
                    title_text = title.text.strip() if title else ''
                    
                    # Extract headings for structure
                    headings = []
                    for tag in ['h1', 'h2', 'h3']:
                        for heading in soup.find_all(tag):
                            headings.append({
                                'level': tag,
                                'text': heading.text.strip()
                            })
                    
                    return {
                        'url': url,
                        'title': title_text,
                        'content': extracted or '',
                        'headings': headings[:10],  # Limit headings
                        'success': True
                    }
                else:
                    return {
                        'url': url,
                        'error': f'HTTP {response.status}',
                        'success': False
                    }
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'success': False
        }

async def perform_deep_search(
    query: str, 
    depth: int = 2, 
    sources: List[str] = None,
    extract_content: bool = True
) -> Dict[str, Any]:
    """Execute deep search with content extraction"""
    
    # Build source-specific queries
    search_queries = [query]
    if sources:
        for source in sources:
            if source == 'github':
                search_queries.append(f'site:github.com {query}')
            elif source == 'reddit':
                search_queries.append(f'site:reddit.com {query}')
            elif source == 'stackoverflow':
                search_queries.append(f'site:stackoverflow.com {query}')
            elif source == 'hackernews':
                search_queries.append(f'site:news.ycombinator.com {query}')
    
    all_results = []
    extracted_content = []
    
    try:
        async with aiohttp.ClientSession() as session:
            # First level - initial searches
            for search_query in search_queries:
                params = {
                    'q': search_query,
                    'format': 'json',
                    'language': 'en',
                    'safesearch': 0
                }
                
                async with session.get(f"{SEARXNG_URL}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', [])[:5]  # Top 5 per query
                        
                        for result in results:
                            result['search_query'] = search_query
                            result['depth_level'] = 1
                            all_results.append(result)
            
            # Extract content from first level results if enabled
            if extract_content and depth >= 1:
                urls_to_extract = [r['url'] for r in all_results[:10]]  # Limit extraction
                extraction_tasks = [extract_page_content(url) for url in urls_to_extract]
                extracted = await asyncio.gather(*extraction_tasks)
                extracted_content.extend([e for e in extracted if e['success']])
            
            # Second level - search based on first results
            if depth >= 2:
                # Generate follow-up queries from first results
                follow_up_queries = set()
                for result in all_results[:5]:
                    # Extract key terms from titles and content
                    words = result.get('title', '').split() + result.get('content', '').split()
                    # Filter for significant words
                    significant_words = [w for w in words if len(w) > 4 and w.isalnum()][:3]
                    if significant_words:
                        follow_up_queries.add(f"{query} {' '.join(significant_words[:2])}")
                
                # Execute follow-up searches
                for follow_query in list(follow_up_queries)[:3]:  # Limit follow-ups
                    params = {
                        'q': follow_query,
                        'format': 'json',
                        'language': 'en'
                    }
                    
                    async with session.get(f"{SEARXNG_URL}/search", params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            results = data.get('results', [])[:3]
                            
                            for result in results:
                                result['search_query'] = follow_query
                                result['depth_level'] = 2
                                all_results.append(result)
        
        # Compile comprehensive results
        return {
            'status': 'success',
            'query': query,
            'depth': depth,
            'sources': sources,
            'timestamp': datetime.utcnow().isoformat(),
            'total_results': len(all_results),
            'extracted_pages': len(extracted_content),
            'results': all_results[:20],  # Limit final results
            'extracted_content': extracted_content[:10],  # Limit extracted content
            'search_tree': {
                'primary_query': query,
                'expanded_queries': list(search_queries),
                'follow_up_queries': list(follow_up_queries) if depth >= 2 else []
            },
            'llm_model': LLM_MODEL if LLM_API_BASE else None
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'query': query,
            'timestamp': datetime.utcnow().isoformat()
        }

# OpenAI-compatible chat endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: Dict[str, Any]):
    """OpenAI API v1 compatible endpoint"""
    
    # Check if this is a tool call
    if request.get('tools'):
        # Return tool selection
        return {
            "id": f"chatcmpl-{datetime.utcnow().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": request.get('model', 'gpt-4'),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": f"call_{datetime.utcnow().timestamp()}",
                        "type": "function",
                        "function": {
                            "name": "deep_search",
                            "arguments": json.dumps({
                                "query": "What would you like to deep search?",
                                "depth": 2
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
        "model": request.get('model', 'gpt-4'),
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Deep search tool ready. I can perform multi-level searches with content extraction."
            },
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

# Tool execution endpoint
@app.post("/v1/tools/execute")
async def execute_tool(request: Dict[str, Any]):
    """Execute the deep search tool"""
    
    if request.get('name') != "deep_search":
        raise HTTPException(status_code=400, detail=f"Unknown tool: {request.get('name')}")
    
    # Extract arguments
    args = request.get('arguments', {})
    query = args.get('query', '')
    depth = args.get('depth', 2)
    sources = args.get('sources', [])
    extract_content = args.get('extract_content', True)
    
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    # Perform deep search
    results = await perform_deep_search(query, depth, sources, extract_content)
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)