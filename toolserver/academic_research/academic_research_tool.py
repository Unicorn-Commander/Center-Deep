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
    title="Center Deep Academic Research Tool",
    version="1.0.0",
    description="Academic research using Gemma 3 4B model (25.5GB VRAM)"
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
            default="gemma-3-4b-it",
            description="Gemma 3 4B model for academic research (25.5GB VRAM)"
        )
        max_papers: int = Field(
            default=15,
            description="Maximum number of academic papers to analyze"
        )
        focus_area: str = Field(
            default="general",
            description="Academic focus area: general, computer_science, medicine, physics, etc."
        )
        include_arxiv: bool = Field(
            default=True,
            description="Include arXiv preprints in search"
        )
        include_scholar: bool = Field(
            default=True,
            description="Include Google Scholar results"
        )
        citation_style: str = Field(
            default="APA",
            description="Citation style: APA, MLA, Chicago, IEEE"
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
ACADEMIC_TOOL = {
    "type": "function",
    "function": {
        "name": "academic_research",
        "description": "Academic research using Gemma 3 4B multimodal model. Conducts scholarly research with academic focus and proper citations.",
        "parameters": {
            "type": "object",
            "properties": {
                "research_query": {
                    "type": "string",
                    "description": "Academic research question or topic"
                },
                "focus_area": {
                    "type": "string",
                    "enum": ["general", "computer_science", "medicine", "physics", "chemistry", "biology", "engineering", "mathematics"],
                    "description": "Academic discipline focus",
                    "default": "general"
                },
                "include_arxiv": {
                    "type": "boolean",
                    "description": "Include arXiv preprints",
                    "default": True
                },
                "include_scholar": {
                    "type": "boolean",
                    "description": "Include Google Scholar results",
                    "default": True
                },
                "citation_style": {
                    "type": "string",
                    "enum": ["APA", "MLA", "Chicago", "IEEE"],
                    "description": "Citation format style",
                    "default": "APA"
                }
            },
            "required": ["research_query"]
        }
    }
}

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "tool": "academic_research",
        "version": "1.0.0",
        "model": tools.valves.llm_model,
        "vram_usage": "25.5GB",
        "capabilities": ["multimodal", "scholarly-analysis", "citation-generation"],
        "description": "Academic research with Gemma 3 4B"
    }

# Tool info endpoint for Open-WebUI discovery
@app.get("/v1/tools")
async def get_tools():
    return {
        "tools": [ACADEMIC_TOOL],
        "server": "Center Deep Academic Research Tool",
        "valves": tools.valves.dict(),
        "model_info": {
            "name": tools.valves.llm_model,
            "vram": "25.5GB",
            "type": "multimodal",
            "speed": "fast",
            "quality": "very good",
            "capabilities": ["text", "images", "scholarly-focus", "citation-aware"]
        }
    }

# Academic research execution
async def perform_academic_research(
    research_query: str,
    focus_area: str = "general",
    include_arxiv: bool = True,
    include_scholar: bool = True,
    citation_style: str = "APA"
) -> Dict[str, Any]:
    """Execute academic research with scholarly focus"""
    
    try:
        # Step 1: Search for academic sources using Center Deep Pro
        academic_data = {}
        async with aiohttp.ClientSession() as session:
            # Primary academic search
            params = {
                'q': f"{research_query} {focus_area if focus_area != 'general' else ''}",
                'format': 'json',
                'categories': 'science',
                'language': 'en'
            }
            
            tasks = []
            
            # Main academic search
            tasks.append(session.get(f"{tools.valves.center_deep_url}/search", params=params))
            
            # arXiv specific search if requested
            if include_arxiv:
                arxiv_params = params.copy()
                arxiv_params['q'] = f"site:arxiv.org {research_query}"
                tasks.append(session.get(f"{tools.valves.center_deep_url}/search", params=arxiv_params))
            
            # Scholar search if requested
            if include_scholar:
                scholar_params = params.copy()
                scholar_params['q'] = f"site:scholar.google.com OR academic {research_query}"
                tasks.append(session.get(f"{tools.valves.center_deep_url}/search", params=scholar_params))
            
            responses = await asyncio.gather(*tasks)
            
            if responses[0].status == 200:
                academic_data['primary'] = await responses[0].json()
            if len(responses) > 1 and responses[1].status == 200:
                academic_data['arxiv'] = await responses[1].json()
            if len(responses) > 2 and responses[2].status == 200:
                academic_data['scholar'] = await responses[2].json()
        
        # Step 2: Academic analysis with Gemma 3 4B
        if tools.valves.vllm_api_base and academic_data:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {tools.valves.vllm_api_key}"
                    }
                    
                    # Compile all academic sources
                    all_sources = []
                    for source_type, data in academic_data.items():
                        results = data.get('results', [])[:5]
                        for r in results:
                            all_sources.append({
                                'title': r.get('title', ''),
                                'url': r.get('url', ''),
                                'content': r.get('content', '')[:400],
                                'source': source_type
                            })
                    
                    # Sort by relevance (prioritize arxiv and scholar)
                    all_sources = sorted(all_sources, key=lambda x: (
                        x['source'] == 'arxiv',
                        x['source'] == 'scholar',
                        len(x['content'])
                    ), reverse=True)[:tools.valves.max_papers]
                    
                    sources_text = "\n\n".join([
                        f"[{i+1}] {s['title']}\nSource: {s['source']}\nURL: {s['url']}\nAbstract: {s['content']}"
                        for i, s in enumerate(all_sources)
                    ])
                    
                    # Citation style templates
                    citation_templates = {
                        "APA": "Author, A. A. (Year). Title of work. Source.",
                        "MLA": "Author. \"Title of Work.\" Source, Year.",
                        "Chicago": "Author. \"Title of Work.\" Source (Year).",
                        "IEEE": "[1] A. Author, \"Title of work,\" Source, Year."
                    }
                    
                    payload = {
                        "model": tools.valves.llm_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""You are an academic research assistant specializing in {focus_area}.
                                Provide scholarly analysis with proper {citation_style} citations.
                                Focus on peer-reviewed sources, methodology, and academic rigor.
                                Use multimodal capabilities to analyze figures and diagrams when relevant."""
                            },
                            {
                                "role": "user",
                                "content": f"""Conduct academic research on: {research_query}

Academic Sources Found:
{sources_text}

Requirements:
1. Provide a comprehensive literature review
2. Identify key theories and methodologies
3. Analyze contradictions or gaps in the literature
4. Suggest future research directions
5. Use {citation_style} citation format: {citation_templates.get(citation_style, citation_templates['APA'])}
6. Include a references section at the end

Generate the academic research analysis:"""
                            }
                        ],
                        "temperature": 0.3,  # Lower for academic accuracy
                        "max_tokens": 1200
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
                            analysis = "Academic analysis unavailable"
            except Exception as e:
                analysis = f"Analysis error: {str(e)}"
        else:
            analysis = "No academic analysis performed"
        
        # Extract key findings
        key_findings = []
        if all_sources:
            for i, source in enumerate(all_sources[:5]):
                key_findings.append({
                    "citation_number": i + 1,
                    "title": source['title'],
                    "source_type": source['source'],
                    "url": source['url']
                })
        
        return {
            "status": "success",
            "research_query": research_query,
            "focus_area": focus_area,
            "academic_analysis": {
                "content": analysis,
                "citation_style": citation_style,
                "sources_analyzed": len(all_sources) if 'all_sources' in locals() else 0,
                "key_findings": key_findings,
                "included_sources": {
                    "primary": len(academic_data.get('primary', {}).get('results', [])),
                    "arxiv": len(academic_data.get('arxiv', {}).get('results', [])) if include_arxiv else 0,
                    "scholar": len(academic_data.get('scholar', {}).get('results', [])) if include_scholar else 0
                }
            },
            "model_used": tools.valves.llm_model,
            "capabilities": ["multimodal", "scholarly-focus", "citation-aware"],
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "vram_usage": "25.5GB",
                "academic_rigor": "high",
                "peer_reviewed_focus": True
            }
        }
                
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "research_query": research_query
        }

# OpenAI-compatible chat endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI API v1 compatible endpoint with Gemma 3 4B"""
    
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
                            "name": "academic_research",
                            "arguments": json.dumps({
                                "research_query": "What academic topic would you like to research?",
                                "focus_area": "general"
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
                "content": "Academic research tool ready for scholarly analysis with proper citations."
            },
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

# Tool execution endpoint
@app.post("/v1/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Execute academic research with Gemma 3 4B scholarly focus"""
    
    if request.name != "academic_research":
        raise HTTPException(status_code=400, detail=f"Unknown tool: {request.name}")
    
    # Extract arguments
    research_query = request.arguments.get('research_query', '')
    focus_area = request.arguments.get('focus_area', tools.valves.focus_area)
    include_arxiv = request.arguments.get('include_arxiv', tools.valves.include_arxiv)
    include_scholar = request.arguments.get('include_scholar', tools.valves.include_scholar)
    citation_style = request.arguments.get('citation_style', tools.valves.citation_style)
    
    if not research_query:
        raise HTTPException(status_code=400, detail="Research query parameter is required")
    
    # Perform academic research
    results = await perform_academic_research(
        research_query,
        focus_area,
        include_arxiv,
        include_scholar,
        citation_style
    )
    
    return results

# Prometheus metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    # Basic metrics in Prometheus format
    metrics = [
        f"# HELP academic_research_requests_total Total number of academic research requests",
        f"# TYPE academic_research_requests_total counter",
        f"academic_research_requests_total 0",
        f"# HELP academic_research_time_seconds Academic research time in seconds",
        f"# TYPE academic_research_time_seconds histogram",
        f"academic_research_time_seconds_bucket{{le=\"10.0\"}} 0",
        f"academic_research_time_seconds_bucket{{le=\"30.0\"}} 0",
        f"academic_research_time_seconds_bucket{{le=\"60.0\"}} 0",
        f"academic_research_time_seconds_bucket{{le=\"+Inf\"}} 0",
        f"academic_research_time_seconds_sum 0",
        f"academic_research_time_seconds_count 0",
        f"# HELP papers_analyzed_total Total academic papers analyzed",
        f"# TYPE papers_analyzed_total counter",
        f"papers_analyzed_total 0"
    ]
    return "\n".join(metrics)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)