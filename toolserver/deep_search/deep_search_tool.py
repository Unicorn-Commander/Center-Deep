from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import aiohttp
import asyncio
from datetime import datetime
import json

app = FastAPI(
    title="Center Deep Advanced Search Tool",
    version="1.0.0",
    description="Advanced multi-source analysis using Gemma 3 12B model (8.5GB VRAM)"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tool class with valves (Open-WebUI format)
class Tools:
    def __init__(self):
        self.valves = self.Valves()

    class Valves(BaseModel):
        center_deep_url: str = Field(
            default="http://unicorn-centerdeep-pro:8888",
            description="Center Deep Pro URL (Evolution of SearXNG)"
        )
        vllm_api_base: str = Field(
            default="http://unicorn-vllm:8000/v1",
            description="vLLM API base URL for Gemma 3 models"
        )
        vllm_api_key: str = Field(
            default="dummy-key",
            description="API key for vLLM service"
        )
        llm_model: str = Field(
            default="gemma-3-12b-it",
            description="Gemma 3 12B model for advanced multimodal analysis (8.5GB VRAM)"
        )
        max_results: int = Field(
            default=20,
            description="Maximum number of search results to analyze"
        )
        search_depth: str = Field(
            default="comprehensive",
            description="Search depth: quick, standard, comprehensive"
        )
        include_images: bool = Field(
            default=True,
            description="Include image analysis in multimodal search"
        )
        timeout: int = Field(
            default=60,
            description="Request timeout in seconds"
        )

# Initialize tools
tools = Tools()

# Pydantic models for API
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

# Tool definition for Open-WebUI
DEEP_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "deep_search",
        "description": "Advanced multi-source analysis using Gemma 3 12B multimodal model. Performs comprehensive research with image understanding capabilities.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The research query or topic to analyze deeply"
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["quick", "standard", "comprehensive"],
                    "description": "Depth of analysis",
                    "default": "comprehensive"
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Include visual content analysis",
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
        "tool": "deep_search",
        "version": "1.0.0",
        "model": tools.valves.llm_model,
        "vram_usage": "8.5GB",
        "capabilities": ["multimodal", "comprehensive-analysis", "image-understanding"],
        "description": "Advanced research with Gemma 3 12B"
    }

# Tool info endpoint for Open-WebUI discovery
@app.get("/v1/tools")
async def get_tools():
    return {
        "tools": [DEEP_SEARCH_TOOL],
        "server": "Center Deep Advanced Search Tool",
        "valves": tools.valves.dict(),
        "model_info": {
            "name": tools.valves.llm_model,
            "vram": "8.5GB",
            "type": "multimodal",
            "speed": "medium",
            "capabilities": ["text", "images", "comprehensive-analysis"]
        }
    }

# Deep search execution
async def perform_deep_search(query: str, search_depth: str = "comprehensive", include_images: bool = True) -> Dict[str, Any]:
    """Execute deep multi-source analysis"""
    
    try:
        # Step 1: Get search results from Center Deep Pro
        async with aiohttp.ClientSession() as session:
            # Search for general content
            params = {
                'q': query,
                'format': 'json',
                'categories': '',
                'language': 'en'
            }
            
            if include_images:
                # Also search for images
                image_params = params.copy()
                image_params['categories'] = 'images'
            
            # Parallel searches
            tasks = [
                session.get(f"{tools.valves.center_deep_url}/search", params=params)
            ]
            if include_images:
                tasks.append(session.get(f"{tools.valves.center_deep_url}/search", params=image_params))
            
            responses = await asyncio.gather(*tasks)
            
            results_data = {}
            if responses[0].status == 200:
                results_data['text'] = await responses[0].json()
            if len(responses) > 1 and responses[1].status == 200:
                results_data['images'] = await responses[1].json()
        
        # Step 2: Deep analysis with Gemma 3 12B
        if tools.valves.vllm_api_base and results_data:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {tools.valves.vllm_api_key}"
                    }
                    
                    # Prepare comprehensive analysis prompt
                    text_results = results_data.get('text', {}).get('results', [])[:10]
                    image_results = results_data.get('images', {}).get('results', [])[:5] if include_images else []
                    
                    results_text = "\n".join([
                        f"Title: {r.get('title', '')}\nURL: {r.get('url', '')}\nContent: {r.get('content', '')[:200]}"
                        for r in text_results
                    ])
                    
                    depth_prompts = {
                        "quick": "Provide a quick summary of key findings.",
                        "standard": "Analyze the main themes and provide insights.",
                        "comprehensive": "Conduct thorough analysis including trends, patterns, contradictions, and comprehensive insights."
                    }
                    
                    payload = {
                        "model": tools.valves.llm_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"You are an advanced research assistant with multimodal capabilities. {depth_prompts[search_depth]}"
                            },
                            {
                                "role": "user",
                                "content": f"Analyze these search results for '{query}':\n\n{results_text}\n\nProvide comprehensive analysis with key insights."
                            }
                        ],
                        "temperature": 0.4,
                        "max_tokens": 1000
                    }
                    
                    async with session.post(
                        f"{tools.valves.vllm_api_base}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=tools.valves.timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            analysis = data['choices'][0]['message']['content']
                        else:
                            analysis = "Deep analysis unavailable"
            except Exception as e:
                analysis = f"Analysis error: {str(e)}"
        else:
            analysis = "No analysis performed"
        
        return {
            "status": "success",
            "query": query,
            "search_depth": search_depth,
            "multimodal": include_images,
            "results": {
                "text_sources": len(results_data.get('text', {}).get('results', [])),
                "image_sources": len(results_data.get('images', {}).get('results', [])) if include_images else 0,
                "top_results": text_results[:5] if 'text_results' in locals() else [],
                "analysis": analysis
            },
            "model_used": tools.valves.llm_model,
            "capabilities": ["multimodal", "comprehensive-analysis", "image-understanding"],
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "vram_usage": "8.5GB"
            }
        }
                
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": query
        }

# OpenAI-compatible chat endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI API v1 compatible endpoint with Gemma 3 12B"""
    
    # Check if this is a tool call
    if request.tools:
        # Return tool selection
        return {
            "id": f"chatcmpl-{datetime.utcnow().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": tools.valves.llm_model,
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
                                "query": "What would you like to research?",
                                "search_depth": "comprehensive"
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
                "content": "Deep search tool ready for comprehensive multimodal analysis."
            },
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

# Tool execution endpoint
@app.post("/v1/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Execute deep search with Gemma 3 12B multimodal analysis"""
    
    if request.name != "deep_search":
        raise HTTPException(status_code=400, detail=f"Unknown tool: {request.name}")
    
    # Extract arguments
    query = request.arguments.get('query', '')
    search_depth = request.arguments.get('search_depth', tools.valves.search_depth)
    include_images = request.arguments.get('include_images', tools.valves.include_images)
    
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    # Perform deep search
    results = await perform_deep_search(query, search_depth, include_images)
    
    return results

# Prometheus metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    # Basic metrics in Prometheus format
    metrics = [
        f"# HELP deep_search_requests_total Total number of deep search requests",
        f"# TYPE deep_search_requests_total counter",
        f"deep_search_requests_total 0",
        f"# HELP deep_search_response_time_seconds Deep search response time in seconds",
        f"# TYPE deep_search_response_time_seconds histogram",
        f"deep_search_response_time_seconds_bucket{{le=\"5.0\"}} 0",
        f"deep_search_response_time_seconds_bucket{{le=\"10.0\"}} 0",
        f"deep_search_response_time_seconds_bucket{{le=\"30.0\"}} 0",
        f"deep_search_response_time_seconds_bucket{{le=\"+Inf\"}} 0",
        f"deep_search_response_time_seconds_sum 0",
        f"deep_search_response_time_seconds_count 0"
    ]
    return "\n".join(metrics)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)