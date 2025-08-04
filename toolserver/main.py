from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, app as flask_app
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, JSON, DateTime
from datetime import datetime
import uuid

# FastAPI app
tool_app = FastAPI(title="Center Deep Tool Server", version="1.0.0")

# CORS middleware
tool_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Models for LLM Configuration
class LLMProvider(db.Model):
    __tablename__ = 'llm_providers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    api_base = db.Column(db.String(500), nullable=False)
    api_key = db.Column(db.String(500))
    model_name = db.Column(db.String(200), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EmbeddingProvider(db.Model):
    __tablename__ = 'embedding_providers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    api_base = db.Column(db.String(500), nullable=False)
    api_key = db.Column(db.String(500))
    model_name = db.Column(db.String(200), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    dimension = db.Column(db.Integer, default=1536)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RerankerProvider(db.Model):
    __tablename__ = 'reranker_providers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    api_base = db.Column(db.String(500), nullable=False)
    api_key = db.Column(db.String(500))
    model_name = db.Column(db.String(200), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    top_k = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class ToolLLMConfig(db.Model):
    __tablename__ = 'tool_llm_config'
    id = db.Column(db.Integer, primary_key=True)
    tool_name = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(200), nullable=False)
    llm_provider_id = db.Column(db.Integer, db.ForeignKey('llm_providers.id'))
    embedding_provider_id = db.Column(db.Integer, db.ForeignKey('embedding_providers.id'))
    reranker_provider_id = db.Column(db.Integer, db.ForeignKey('reranker_providers.id'))
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=4000)
    system_prompt = db.Column(db.Text)
    enabled = db.Column(db.Boolean, default=True)
    settings = db.Column(db.JSON, default={})
    llm_provider = db.relationship('LLMProvider', backref='tool_configs')
    embedding_provider = db.relationship('EmbeddingProvider', backref='tool_configs')
    reranker_provider = db.relationship('RerankerProvider', backref='tool_configs')

# Create tables
with flask_app.app_context():
    db.create_all()

# Pydantic models for OpenAI API compatibility
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

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: Dict[str, Any]

# Tool definitions
AVAILABLE_TOOLS = {
    "search": {
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
                        "description": "Search category"
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
    },
    "deep_search": {
        "type": "function", 
        "function": {
            "name": "deep_search",
            "description": "Perform comprehensive multi-source search with analysis",
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
                        "default": 2
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific sources to include"
                    }
                },
                "required": ["query"]
            }
        }
    },
    "generate_report": {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "Generate a professional report with citations",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic for the report"
                    },
                    "report_type": {
                        "type": "string",
                        "enum": ["analysis", "academic", "executive", "technical"],
                        "description": "Type of report to generate"
                    },
                    "sections": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific sections to include"
                    }
                },
                "required": ["topic", "report_type"]
            }
        }
    }
}

# API key validation
async def validate_api_key(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    # In production, validate against database
    # For now, accept any non-empty token
    if not token:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

# Health check endpoint
@tool_app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Center Deep Tool Server"}

# List available tools
@tool_app.get("/v1/tools")
async def list_tools(api_key: str = Depends(validate_api_key)):
    return {
        "tools": list(AVAILABLE_TOOLS.values()),
        "server": "Center Deep Tool Server"
    }

# OpenAI-compatible chat completions endpoint
@tool_app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    api_key: str = Depends(validate_api_key)
):
    """OpenAI API v1 compatible endpoint for tool use"""
    
    # Check if tools were requested
    if request.tools:
        # Return available tools in response
        response = ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(datetime.utcnow().timestamp()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": f"call_{uuid.uuid4().hex[:8]}",
                        "type": "function",
                        "function": {
                            "name": "search",
                            "arguments": '{"query": "test search"}'
                        }
                    }]
                },
                "finish_reason": "tool_calls"
            }],
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        )
        return response.dict()
    
    # Regular completion without tools
    response = ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        created=int(datetime.utcnow().timestamp()),
        model=request.model,
        choices=[{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Tool server is operational. Use tools parameter to access search and analysis functions."
            },
            "finish_reason": "stop"
        }],
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    )
    
    return response.dict()

# Tool execution endpoint
@tool_app.post("/v1/tools/execute")
async def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    api_key: str = Depends(validate_api_key)
):
    """Execute a specific tool with given arguments"""
    
    if tool_name not in ["search", "deep_search", "generate_report"]:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
    
    # Get LLM configuration for this tool
    with flask_app.app_context():
        config = ToolLLMConfig.query.filter_by(
            tool_name=tool_name,
            enabled=True
        ).first()
        
        if config and config.llm_provider:
            llm_info = {
                "provider": config.llm_provider.name,
                "model": config.llm_provider.model_name,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            }
        else:
            llm_info = {
                "provider": "default",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 4000
            }
    
    # Execute tool based on name
    if tool_name == "search":
        from .tools.search import execute_search
        result = await execute_search(arguments, llm_info)
    elif tool_name == "deep_search":
        from .tools.deep_search import execute_deep_search
        result = await execute_deep_search(arguments, llm_info)
    elif tool_name == "generate_report":
        from .tools.analysis import generate_report
        result = await generate_report(arguments, llm_info)
    
    return {
        "tool": tool_name,
        "arguments": arguments,
        "result": result,
        "llm_config": llm_info
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(tool_app, host="0.0.0.0", port=8891)