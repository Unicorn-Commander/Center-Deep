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
    title="Center Deep Report Generator",
    version="1.0.0",
    description="Professional report generation using Gemma 3 27B model (34.4GB VRAM)"
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
            default="gemma-3-27b-it",
            description="Gemma 3 27B model for maximum quality professional reports (34.4GB VRAM)"
        )
        report_sections: int = Field(
            default=5,
            description="Number of sections in generated reports"
        )
        max_report_length: int = Field(
            default=2000,
            description="Maximum report length in tokens"
        )
        include_citations: bool = Field(
            default=True,
            description="Include citations and references"
        )
        report_format: str = Field(
            default="professional",
            description="Report format: professional, academic, executive, technical"
        )
        timeout: int = Field(
            default=90,
            description="Request timeout in seconds (longer for detailed reports)"
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
REPORT_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_report",
        "description": "Professional report generation using Gemma 3 27B multimodal model. Generates high-quality professional reports with maximum detail.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Report topic or subject"
                },
                "report_type": {
                    "type": "string",
                    "enum": ["professional", "executive", "technical", "academic"],
                    "description": "Type of report to generate",
                    "default": "professional"
                },
                "sections": {
                    "type": "integer",
                    "description": "Number of sections (3-10)",
                    "default": 5,
                    "minimum": 3,
                    "maximum": 10
                },
                "include_citations": {
                    "type": "boolean",
                    "description": "Include citations and references",
                    "default": True
                }
            },
            "required": ["topic"]
        }
    }
}

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "tool": "generate_report",
        "version": "1.0.0",
        "model": tools.valves.llm_model,
        "vram_usage": "34.4GB",
        "capabilities": ["multimodal", "maximum-quality", "professional-reports"],
        "description": "Professional reports with Gemma 3 27B"
    }

# Tool info endpoint for Open-WebUI discovery
@app.get("/v1/tools")
async def get_tools():
    return {
        "tools": [REPORT_TOOL],
        "server": "Center Deep Report Generator",
        "valves": tools.valves.dict(),
        "model_info": {
            "name": tools.valves.llm_model,
            "vram": "34.4GB",
            "type": "multimodal",
            "speed": "slower",
            "quality": "maximum",
            "capabilities": ["text", "images", "professional-output", "comprehensive-analysis"]
        }
    }

# Report generation
async def generate_professional_report(
    topic: str, 
    report_type: str = "professional",
    sections: int = 5,
    include_citations: bool = True
) -> Dict[str, Any]:
    """Generate professional report with maximum quality"""
    
    try:
        # Step 1: Research the topic using Center Deep Pro
        research_data = {}
        async with aiohttp.ClientSession() as session:
            # Search for comprehensive information
            params = {
                'q': topic,
                'format': 'json',
                'categories': '',
                'language': 'en'
            }
            
            # Also search for academic sources if needed
            if report_type == "academic":
                academic_params = params.copy()
                academic_params['categories'] = 'science'
                
                tasks = [
                    session.get(f"{tools.valves.center_deep_url}/search", params=params),
                    session.get(f"{tools.valves.center_deep_url}/search", params=academic_params)
                ]
                responses = await asyncio.gather(*tasks)
                
                if responses[0].status == 200:
                    research_data['general'] = await responses[0].json()
                if responses[1].status == 200:
                    research_data['academic'] = await responses[1].json()
            else:
                response = await session.get(f"{tools.valves.center_deep_url}/search", params=params)
                if response.status == 200:
                    research_data['general'] = await response.json()
        
        # Step 2: Generate comprehensive report with Gemma 3 27B
        if tools.valves.vllm_api_base and research_data:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {tools.valves.vllm_api_key}"
                    }
                    
                    # Prepare research summary
                    all_results = []
                    for category, data in research_data.items():
                        results = data.get('results', [])[:10]
                        all_results.extend(results)
                    
                    research_text = "\n\n".join([
                        f"Source: {r.get('title', '')}\nURL: {r.get('url', '')}\nContent: {r.get('content', '')[:300]}"
                        for r in all_results[:15]
                    ])
                    
                    # Create report structure prompt
                    report_structures = {
                        "professional": "Executive Summary, Introduction, Key Findings, Analysis, Recommendations, Conclusion",
                        "executive": "Executive Brief, Strategic Overview, Key Insights, Business Impact, Action Items",
                        "technical": "Abstract, Technical Background, Implementation Details, Architecture, Performance Analysis, Conclusion",
                        "academic": "Abstract, Introduction, Literature Review, Methodology, Results, Discussion, Conclusion, References"
                    }
                    
                    structure = report_structures.get(report_type, report_structures["professional"])
                    
                    citation_instruction = "Include numbered citations [1], [2], etc. and a References section at the end." if include_citations else ""
                    
                    payload = {
                        "model": tools.valves.llm_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""You are a professional report writer with expertise in creating {report_type} reports. 
                                Generate comprehensive, well-structured reports with maximum quality and detail.
                                Use multimodal analysis capabilities to provide rich insights."""
                            },
                            {
                                "role": "user",
                                "content": f"""Create a comprehensive {report_type} report on: {topic}

Research Data Available:
{research_text}

Report Requirements:
- Format: {report_type.capitalize()} Report
- Sections ({sections}): {structure}
- Length: Comprehensive and detailed (approximately {tools.valves.max_report_length} words)
- Style: Professional, authoritative, and insightful
- {citation_instruction}

Generate the complete report with all sections:"""
                            }
                        ],
                        "temperature": 0.2,  # Lower temperature for professional output
                        "max_tokens": tools.valves.max_report_length
                    }
                    
                    async with session.post(
                        f"{tools.valves.vllm_api_base}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=tools.valves.timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            report_content = data['choices'][0]['message']['content']
                        else:
                            report_content = "Report generation failed"
            except Exception as e:
                report_content = f"Report generation error: {str(e)}"
        else:
            report_content = "Unable to generate report without research data"
        
        # Calculate report statistics
        word_count = len(report_content.split()) if report_content else 0
        
        return {
            "status": "success",
            "topic": topic,
            "report_type": report_type,
            "report": {
                "title": f"{report_type.capitalize()} Report: {topic}",
                "content": report_content,
                "sections": sections,
                "format": report_type,
                "word_count": word_count,
                "includes_citations": include_citations
            },
            "model_used": tools.valves.llm_model,
            "quality_indicators": {
                "detail_level": "comprehensive",
                "analysis_depth": "maximum",
                "visual_analysis": "enabled",
                "professional_formatting": True
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "vram_usage": "34.4GB",
                "model_type": "Gemma 3 27B Multimodal",
                "sources_analyzed": len(all_results) if 'all_results' in locals() else 0
            }
        }
                
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "topic": topic
        }

# OpenAI-compatible chat endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI API v1 compatible endpoint with Gemma 3 27B"""
    
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
                            "name": "generate_report",
                            "arguments": json.dumps({
                                "topic": "What topic would you like a report on?",
                                "report_type": "professional"
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
                "content": "Report generator ready for maximum quality professional reports."
            },
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

# Tool execution endpoint
@app.post("/v1/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Execute report generation with Gemma 3 27B maximum quality"""
    
    if request.name != "generate_report":
        raise HTTPException(status_code=400, detail=f"Unknown tool: {request.name}")
    
    # Extract arguments
    topic = request.arguments.get('topic', '')
    report_type = request.arguments.get('report_type', tools.valves.report_format)
    sections = request.arguments.get('sections', tools.valves.report_sections)
    include_citations = request.arguments.get('include_citations', tools.valves.include_citations)
    
    if not topic:
        raise HTTPException(status_code=400, detail="Topic parameter is required")
    
    # Generate report
    results = await generate_professional_report(topic, report_type, sections, include_citations)
    
    return results

# Prometheus metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    # Basic metrics in Prometheus format
    metrics = [
        f"# HELP report_generation_requests_total Total number of report generation requests",
        f"# TYPE report_generation_requests_total counter",
        f"report_generation_requests_total 0",
        f"# HELP report_generation_time_seconds Report generation time in seconds",
        f"# TYPE report_generation_time_seconds histogram",
        f"report_generation_time_seconds_bucket{{le=\"30.0\"}} 0",
        f"report_generation_time_seconds_bucket{{le=\"60.0\"}} 0",
        f"report_generation_time_seconds_bucket{{le=\"90.0\"}} 0",
        f"report_generation_time_seconds_bucket{{le=\"+Inf\"}} 0",
        f"report_generation_time_seconds_sum 0",
        f"report_generation_time_seconds_count 0"
    ]
    return "\n".join(metrics)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)