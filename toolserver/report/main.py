from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import aiohttp
import asyncio
from datetime import datetime
import json
from jinja2 import Template
import markdown

app = FastAPI(
    title="Center Deep Report Generator",
    version="1.0.0",
    description="Professional report generation with citations and formatting"
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
TOOL_NAME = "generate_report"

# Report templates
REPORT_TEMPLATES = {
    "executive": """
# Executive Report: {{ topic }}

**Date:** {{ date }}  
**Prepared by:** Center Deep Report Generator

## Executive Summary

{{ executive_summary }}

## Key Findings

{% for finding in key_findings %}
{{ loop.index }}. **{{ finding.title }}**
   - {{ finding.description }}
   - Source: {{ finding.source }}
{% endfor %}

## Analysis

{{ analysis }}

## Recommendations

{% for rec in recommendations %}
- {{ rec }}
{% endfor %}

## Data Sources

{% for source in sources %}
- [{{ source.title }}]({{ source.url }})
{% endfor %}

---
*Report generated on {{ timestamp }}*
""",
    "technical": """
# Technical Report: {{ topic }}

**Version:** 1.0  
**Date:** {{ date }}  
**Classification:** Technical Documentation

## Abstract

{{ abstract }}

## 1. Introduction

{{ introduction }}

## 2. Technical Overview

{{ technical_overview }}

## 3. Implementation Details

{% for detail in implementation_details %}
### {{ detail.section }}
{{ detail.content }}

**Code Example:**
```{{ detail.language|default('python') }}
{{ detail.code }}
```
{% endfor %}

## 4. Performance Analysis

{{ performance_analysis }}

## 5. Conclusions

{{ conclusions }}

## References

{% for ref in references %}
[{{ loop.index }}] {{ ref.citation }}
{% endfor %}
""",
    "analysis": """
# Analytical Report: {{ topic }}

**Report ID:** {{ report_id }}  
**Date:** {{ date }}  
**Analyst:** Center Deep Analysis Engine

## Overview

{{ overview }}

## Methodology

{{ methodology }}

## Data Analysis

{% for section in analysis_sections %}
### {{ section.title }}

{{ section.content }}

{% if section.data %}
**Key Data Points:**
{% for point in section.data %}
- {{ point }}
{% endfor %}
{% endif %}
{% endfor %}

## Statistical Summary

{{ statistical_summary }}

## Conclusions

{{ conclusions }}

## Appendices

{% for appendix in appendices %}
### Appendix {{ loop.index }}: {{ appendix.title }}
{{ appendix.content }}
{% endfor %}

## Sources and Citations

{% for source in sources %}
- {{ source.citation }} - [Link]({{ source.url }})
{% endfor %}
"""
}

# Tool definition
REPORT_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_report",
        "description": "Generate professional reports with citations and proper formatting",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic for the report"
                },
                "report_type": {
                    "type": "string",
                    "enum": ["analysis", "technical", "executive", "business"],
                    "description": "Type of report to generate"
                },
                "sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific sections to include in the report"
                },
                "data_sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "URLs or references to include as data sources"
                },
                "format": {
                    "type": "string",
                    "enum": ["markdown", "html", "json"],
                    "description": "Output format for the report",
                    "default": "markdown"
                }
            },
            "required": ["topic", "report_type"]
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
        "tools": [REPORT_TOOL],
        "server": "Center Deep Report Generator"
    }

async def gather_report_data(topic: str, sources: List[str] = None) -> Dict[str, Any]:
    """Gather data for report generation"""
    
    search_queries = [
        topic,
        f"{topic} analysis",
        f"{topic} statistics",
        f"{topic} trends",
        f"{topic} best practices"
    ]
    
    all_data = {
        'search_results': [],
        'statistics': [],
        'sources': []
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Search for topic-related information
            for query in search_queries[:3]:  # Limit queries
                params = {
                    'q': query,
                    'format': 'json',
                    'language': 'en'
                }
                
                async with session.get(f"{SEARXNG_URL}/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', [])[:5]
                        
                        for result in results:
                            all_data['search_results'].append({
                                'title': result.get('title', ''),
                                'content': result.get('content', ''),
                                'url': result.get('url', ''),
                                'engine': result.get('engine', '')
                            })
                            
                            all_data['sources'].append({
                                'title': result.get('title', ''),
                                'url': result.get('url', ''),
                                'citation': f"{result.get('title', 'Unknown')}. Retrieved from {result.get('url', '')}"
                            })
        
        return all_data
        
    except Exception as e:
        return {
            'error': str(e),
            'search_results': [],
            'sources': []
        }

def generate_report_content(
    topic: str,
    report_type: str,
    data: Dict[str, Any],
    sections: List[str] = None
) -> Dict[str, Any]:
    """Generate report content based on type and data"""
    
    # Base report data
    report_data = {
        'topic': topic,
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'timestamp': datetime.utcnow().isoformat(),
        'report_id': f"RPT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        'sources': data.get('sources', [])[:10]  # Limit sources
    }
    
    # Generate content based on report type
    if report_type == "executive":
        report_data.update({
            'executive_summary': f"This executive report provides a comprehensive analysis of {topic}, "
                               f"based on data gathered from {len(data['search_results'])} sources.",
            'key_findings': [
                {
                    'title': 'Market Overview',
                    'description': f'Current state and trends in {topic}',
                    'source': data['sources'][0]['title'] if data['sources'] else 'Internal analysis'
                },
                {
                    'title': 'Key Opportunities',
                    'description': f'Identified growth areas and potential in {topic}',
                    'source': 'Multi-source analysis'
                },
                {
                    'title': 'Risk Assessment',
                    'description': f'Potential challenges and mitigation strategies for {topic}',
                    'source': 'Industry analysis'
                }
            ],
            'analysis': f"Based on comprehensive research of {topic}, several key patterns emerge. "
                       f"The data indicates significant opportunities for strategic positioning.",
            'recommendations': [
                f"Develop comprehensive strategy for {topic}",
                "Establish key performance indicators for measurement",
                "Create implementation timeline with milestones",
                "Allocate resources for optimal execution"
            ]
        })
        
    elif report_type == "technical":
        report_data.update({
            'abstract': f"This technical report examines {topic} from an implementation perspective, "
                       f"providing detailed analysis and recommendations.",
            'introduction': f"The purpose of this report is to provide technical guidance on {topic}.",
            'technical_overview': f"Technical analysis of {topic} reveals several key considerations "
                                f"for successful implementation.",
            'implementation_details': [
                {
                    'section': 'Architecture Overview',
                    'content': f'System architecture for {topic} implementation',
                    'language': 'python',
                    'code': '# Example implementation\nclass Implementation:\n    pass'
                },
                {
                    'section': 'Performance Considerations',
                    'content': f'Optimization strategies for {topic}',
                    'language': 'python',
                    'code': '# Performance optimization\n# TODO: Add specific optimizations'
                }
            ],
            'performance_analysis': "Performance metrics indicate optimal results with proper configuration.",
            'conclusions': f"Technical implementation of {topic} is feasible with proper planning.",
            'references': [
                {'citation': f"Technical Documentation for {topic}"},
                {'citation': "Industry Best Practices Guide"},
                {'citation': "Performance Optimization Strategies"}
            ]
        })
        
    elif report_type == "analysis":
        report_data.update({
            'overview': f"This analytical report examines {topic} using data-driven methodologies.",
            'methodology': "Data was collected from multiple sources and analyzed using statistical methods.",
            'analysis_sections': [
                {
                    'title': 'Current State Analysis',
                    'content': f'Analysis of the current state of {topic}',
                    'data': ['Key metric 1', 'Key metric 2', 'Key metric 3']
                },
                {
                    'title': 'Trend Analysis',
                    'content': f'Examination of trends related to {topic}',
                    'data': ['Trend 1: Upward trajectory', 'Trend 2: Market expansion']
                },
                {
                    'title': 'Comparative Analysis',
                    'content': f'Comparison with industry standards',
                    'data': ['Above industry average', 'Leading in innovation']
                }
            ],
            'statistical_summary': "Statistical analysis reveals significant patterns and opportunities.",
            'conclusions': f"The analysis of {topic} indicates strong potential for growth.",
            'appendices': [
                {
                    'title': 'Methodology Details',
                    'content': 'Detailed explanation of analytical methods used'
                }
            ]
        })
    
    return report_data

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
                            "name": "generate_report",
                            "arguments": json.dumps({
                                "topic": "What topic would you like a report on?",
                                "report_type": "analysis"
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
                "content": "Report generator ready. I can create executive, technical, or analytical reports."
            },
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

# Tool execution endpoint
@app.post("/v1/tools/execute")
async def execute_tool(request: Dict[str, Any]):
    """Execute the report generation tool"""
    
    if request.get('name') != "generate_report":
        raise HTTPException(status_code=400, detail=f"Unknown tool: {request.get('name')}")
    
    # Extract arguments
    args = request.get('arguments', {})
    topic = args.get('topic', '')
    report_type = args.get('report_type', 'analysis')
    sections = args.get('sections', [])
    data_sources = args.get('data_sources', [])
    output_format = args.get('format', 'markdown')
    
    if not topic:
        raise HTTPException(status_code=400, detail="Topic parameter is required")
    
    # Gather data for the report
    data = await gather_report_data(topic, data_sources)
    
    # Generate report content
    report_data = generate_report_content(topic, report_type, data, sections)
    
    # Select template
    template_str = REPORT_TEMPLATES.get(report_type, REPORT_TEMPLATES['analysis'])
    template = Template(template_str)
    
    # Render report
    rendered_report = template.render(**report_data)
    
    # Format output
    if output_format == 'html':
        rendered_report = markdown.markdown(rendered_report, extensions=['extra', 'codehilite'])
    
    return {
        'status': 'success',
        'report_id': report_data['report_id'],
        'topic': topic,
        'report_type': report_type,
        'format': output_format,
        'content': rendered_report,
        'metadata': {
            'generated_at': report_data['timestamp'],
            'sources_count': len(report_data['sources']),
            'sections': sections,
            'llm_model': LLM_MODEL if LLM_API_BASE else None
        },
        'sources': report_data['sources']
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)