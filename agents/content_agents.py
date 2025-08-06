"""
Content Generation Agents
AI-powered agents that create content from scraped data
"""

import requests
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging
from jinja2 import Template
import re

logger = logging.getLogger(__name__)

class BaseContentAgent:
    """Base class for all content generation agents"""
    
    def __init__(self, config: Dict[str, Any], llm_config: Dict[str, Any]):
        self.config = config
        self.llm_config = llm_config
        self.name = config.get('name', 'Unnamed Agent')
        self.agent_type = config.get('agent_type', 'generic')
    
    def generate_content(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Override this method in subclasses"""
        raise NotImplementedError
    
    def call_llm(self, messages: List[Dict[str, str]], temperature: Optional[float] = None) -> Optional[str]:
        """Make a call to the configured LLM"""
        try:
            api_base = self.llm_config.get('api_base', '')
            api_key = self.llm_config.get('api_key', '')
            model_name = self.llm_config.get('model_name', 'gpt-3.5-turbo')
            
            if not api_base or not model_name:
                logger.error("LLM configuration incomplete")
                return None
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}' if api_key else ''
            }
            
            data = {
                'model': model_name,
                'messages': messages,
                'temperature': temperature or self.llm_config.get('temperature', 0.7),
                'max_tokens': self.llm_config.get('max_tokens', 4000)
            }
            
            response = requests.post(
                f"{api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"LLM API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return None
    
    def format_source_data(self, source_data: List[Dict[str, Any]]) -> str:
        """Format source data for LLM consumption"""
        formatted_items = []
        
        for i, item in enumerate(source_data, 1):
            metadata = item.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            published = metadata.get('published', '')
            
            formatted_item = f"""
{i}. **{item.get('title', 'No Title')}**
   Source: {source}
   Published: {published}
   URL: {item.get('url', 'N/A')}
   
   {item.get('content', 'No content available')[:500]}...
   """
            formatted_items.append(formatted_item.strip())
        
        return "\n\n".join(formatted_items)

class BlogPostAgent(BaseContentAgent):
    """Agent that generates blog posts from collected data"""
    
    def generate_content(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not source_data:
            return []
        
        logger.info(f"BlogPostAgent generating content from {len(source_data)} items")
        
        # Group data by topic/theme for better organization
        topics = self._group_by_topics(source_data)
        results = []
        
        for topic, items in topics.items():
            if len(items) < 2:  # Skip topics with too few items
                continue
                
            system_prompt = self.config.get('system_prompt', self._default_blog_system_prompt())
            formatted_data = self.format_source_data(items)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
Based on the following recent developments, write a comprehensive blog post:

{formatted_data}

Focus on:
- Creating an engaging title that captures the main theme
- Providing analysis and insights, not just summarizing
- Including relevant details and context
- Writing in a professional but accessible tone
- Adding a conclusion that ties everything together

The blog post should be informative and valuable to readers interested in technology and innovation.
"""}
            ]
            
            generated_content = self.call_llm(messages)
            
            if generated_content:
                # Extract title and content
                title, content = self._extract_title_and_content(generated_content)
                
                results.append({
                    'title': title,
                    'content': content,
                    'content_type': 'blog_post',
                    'metadata': {
                        'topic': topic,
                        'source_count': len(items),
                        'word_count': len(content.split()),
                        'generated_by': self.name,
                        'tags': self._extract_tags(items)
                    },
                    'source_data_ids': [item.get('id') for item in items if item.get('id')]
                })
        
        logger.info(f"BlogPostAgent generated {len(results)} blog posts")
        return results
    
    def _default_blog_system_prompt(self) -> str:
        return """You are a professional tech blogger for Center Deep, a search platform company. Your role is to create engaging, insightful blog posts based on recent developments in technology, search, AI, and related fields.

Guidelines:
- Write in a professional but approachable tone
- Focus on analysis and insights, not just news reporting
- Include context and explain why developments matter
- Keep posts between 800-1500 words
- Use clear structure with headings and subheadings
- Include actionable insights when possible
- Always fact-check and attribute sources appropriately

Format your response as:
# [Blog Post Title]

[Blog post content with appropriate markdown formatting]
"""
    
    def _group_by_topics(self, source_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group source data by detected topics"""
        # Simple topic detection based on keywords
        topics = {}
        
        for item in source_data:
            title = item.get('title', '').lower()
            content = item.get('content', '').lower()
            full_text = f"{title} {content}"
            
            # Define topic keywords
            topic_keywords = {
                'AI & Machine Learning': ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt', 'claude', 'neural', 'model'],
                'Search Technology': ['search', 'index', 'crawler', 'seo', 'query', 'ranking', 'elasticsearch', 'solr'],
                'Web Development': ['javascript', 'react', 'vue', 'angular', 'node', 'python', 'api', 'framework'],
                'Open Source': ['open source', 'github', 'release', 'repository', 'commit', 'pull request'],
                'Security': ['security', 'vulnerability', 'encryption', 'privacy', 'breach', 'authentication'],
                'General Tech': []  # Catch-all category
            }
            
            # Find best matching topic
            best_topic = 'General Tech'
            max_matches = 0
            
            for topic, keywords in topic_keywords.items():
                if topic == 'General Tech':
                    continue
                    
                matches = sum(1 for keyword in keywords if keyword in full_text)
                if matches > max_matches:
                    max_matches = matches
                    best_topic = topic
            
            if best_topic not in topics:
                topics[best_topic] = []
            topics[best_topic].append(item)
        
        return topics
    
    def _extract_title_and_content(self, generated_content: str) -> tuple:
        """Extract title and content from generated blog post"""
        lines = generated_content.strip().split('\n')
        
        title = "Generated Blog Post"  # Default title
        content_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#') and not content_lines:  # First heading is the title
                title = line.lstrip('# ').strip()
            else:
                content_lines.append(line)
        
        content = '\n'.join(content_lines).strip()
        return title, content
    
    def _extract_tags(self, source_items: List[Dict[str, Any]]) -> List[str]:
        """Extract relevant tags from source items"""
        tags = set()
        
        for item in source_items:
            metadata = item.get('metadata', {})
            
            # Add existing tags
            if 'tags' in metadata:
                tags.update(metadata['tags'])
            
            # Add source-based tags
            source = metadata.get('source', '')
            if 'github' in source.lower():
                tags.add('open-source')
            if 'reddit' in source.lower():
                tags.add('community')
            
            # Add scraper type tags
            scraper_type = metadata.get('scraper_type', '')
            if scraper_type:
                tags.add(scraper_type.replace('_', '-'))
        
        return list(tags)[:10]  # Limit to 10 tags

class SocialMediaAgent(BaseContentAgent):
    """Agent that generates social media posts"""
    
    def generate_content(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not source_data:
            return []
        
        logger.info(f"SocialMediaAgent generating content from {len(source_data)} items")
        
        # Select most interesting items for social posts
        interesting_items = self._select_interesting_items(source_data, max_items=5)
        results = []
        
        platforms = self.config.get('platforms', ['twitter', 'linkedin'])
        
        for item in interesting_items:
            for platform in platforms:
                system_prompt = self._get_platform_prompt(platform)
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""
Create a {platform} post about this development:

Title: {item.get('title', '')}
Content: {item.get('content', '')[:300]}...
Source: {item.get('metadata', {}).get('source', 'Unknown')}
URL: {item.get('url', '')}

Make it engaging and include relevant hashtags.
"""}
                ]
                
                generated_content = self.call_llm(messages, temperature=0.8)
                
                if generated_content:
                    results.append({
                        'title': f"{platform.title()} Post - {item.get('title', 'Update')[:50]}...",
                        'content': generated_content.strip(),
                        'content_type': 'social_post',
                        'metadata': {
                            'platform': platform,
                            'source_title': item.get('title', ''),
                            'source_url': item.get('url', ''),
                            'generated_by': self.name
                        },
                        'source_data_ids': [item.get('id')] if item.get('id') else []
                    })
        
        logger.info(f"SocialMediaAgent generated {len(results)} social posts")
        return results
    
    def _select_interesting_items(self, source_data: List[Dict[str, Any]], max_items: int = 5) -> List[Dict[str, Any]]:
        """Select the most interesting items for social media"""
        # Simple scoring based on various factors
        scored_items = []
        
        for item in source_data:
            score = 0
            title = item.get('title', '').lower()
            content = item.get('content', '').lower()
            metadata = item.get('metadata', {})
            
            # Score based on engagement indicators
            if 'score' in metadata:
                score += min(metadata['score'] / 100, 5)  # Reddit score
            
            if 'num_comments' in metadata:
                score += min(metadata['num_comments'] / 10, 3)
            
            # Score based on keywords
            interesting_keywords = ['breakthrough', 'launch', 'release', 'new', 'first', 'major', 'significant']
            score += sum(2 for keyword in interesting_keywords if keyword in title or keyword in content)
            
            # Prefer recent content
            if 'published' in metadata:
                try:
                    pub_date = datetime.fromisoformat(metadata['published'].replace('Z', '+00:00'))
                    days_old = (datetime.now(timezone.utc) - pub_date).days
                    if days_old < 1:
                        score += 3
                    elif days_old < 7:
                        score += 1
                except:
                    pass
            
            scored_items.append((score, item))
        
        # Sort by score and return top items
        scored_items.sort(reverse=True)
        return [item for score, item in scored_items[:max_items]]
    
    def _get_platform_prompt(self, platform: str) -> str:
        """Get platform-specific system prompt"""
        prompts = {
            'twitter': """You are a social media manager creating Twitter/X posts for Center Deep, a search platform company. 
            
            Guidelines:
            - Keep posts under 280 characters
            - Use engaging, conversational tone
            - Include 2-3 relevant hashtags
            - Make it shareable and discussion-worthy
            - Focus on the key insight or development
            """,
            
            'linkedin': """You are a professional social media manager creating LinkedIn posts for Center Deep, a search platform company.
            
            Guidelines:
            - Professional but engaging tone
            - Can be longer (up to 1300 characters)
            - Include insights and professional perspective
            - Use relevant professional hashtags
            - Encourage professional discussion
            - Focus on business implications
            """
        }
        
        return prompts.get(platform, prompts['twitter'])

class NewsletterAgent(BaseContentAgent):
    """Agent that generates newsletter content"""
    
    def generate_content(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not source_data:
            return []
        
        logger.info(f"NewsletterAgent generating content from {len(source_data)} items")
        
        # Organize data by categories for newsletter sections
        categorized_data = self._categorize_newsletter_data(source_data)
        
        system_prompt = self.config.get('system_prompt', self._default_newsletter_prompt())
        formatted_data = self._format_newsletter_data(categorized_data)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
Create a newsletter based on this week's developments:

{formatted_data}

Structure the newsletter with:
- Engaging subject line
- Brief intro
- Main sections covering different topics
- Key highlights and insights
- Conclusion with call-to-action

Make it informative and valuable for subscribers interested in technology and search.
"""}
        ]
        
        generated_content = self.call_llm(messages)
        
        if generated_content:
            # Extract subject line and content
            subject_line, content = self._extract_newsletter_parts(generated_content)
            
            return [{
                'title': subject_line,
                'content': content,
                'content_type': 'newsletter',
                'metadata': {
                    'sections': list(categorized_data.keys()),
                    'total_items': len(source_data),
                    'word_count': len(content.split()),
                    'generated_by': self.name
                },
                'source_data_ids': [item.get('id') for item in source_data if item.get('id')]
            }]
        
        return []
    
    def _default_newsletter_prompt(self) -> str:
        return """You are the newsletter editor for Center Deep, a search platform company. Create engaging weekly newsletters that keep subscribers informed about developments in search technology, AI, web development, and related fields.

Guidelines:
- Professional but friendly tone
- Well-structured with clear sections
- Include analysis and insights, not just news
- Keep sections concise but informative
- End with actionable insights or call-to-action
- Format with proper markdown

Format:
Subject: [Compelling subject line]

[Newsletter content with markdown formatting]
"""
    
    def _categorize_newsletter_data(self, source_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize data for newsletter sections"""
        categories = {
            'AI & Machine Learning': [],
            'Search & Discovery': [],
            'Open Source Highlights': [],
            'Developer Tools': [],
            'Industry News': []
        }
        
        for item in source_data:
            title = item.get('title', '').lower()
            content = item.get('content', '').lower()
            metadata = item.get('metadata', {})
            
            # Categorize based on content and source
            if any(keyword in title + content for keyword in ['ai', 'artificial intelligence', 'machine learning', 'llm']):
                categories['AI & Machine Learning'].append(item)
            elif any(keyword in title + content for keyword in ['search', 'index', 'query', 'ranking']):
                categories['Search & Discovery'].append(item)
            elif metadata.get('scraper_type') == 'github_release' or 'github' in metadata.get('source', '').lower():
                categories['Open Source Highlights'].append(item)
            elif any(keyword in title + content for keyword in ['api', 'framework', 'library', 'development']):
                categories['Developer Tools'].append(item)
            else:
                categories['Industry News'].append(item)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _format_newsletter_data(self, categorized_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Format categorized data for newsletter generation"""
        sections = []
        
        for category, items in categorized_data.items():
            section = f"\n**{category}:**\n"
            
            for item in items[:5]:  # Limit items per section
                metadata = item.get('metadata', {})
                source = metadata.get('source', 'Unknown')
                
                section += f"- {item.get('title', 'No title')} ({source})\n"
                section += f"  {item.get('content', 'No content')[:200]}...\n"
                section += f"  {item.get('url', '')}\n\n"
            
            sections.append(section)
        
        return "\n".join(sections)
    
    def _extract_newsletter_parts(self, generated_content: str) -> tuple:
        """Extract subject line and content from generated newsletter"""
        lines = generated_content.strip().split('\n')
        
        subject_line = "Center Deep Newsletter"  # Default
        content_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('Subject:'):
                subject_line = line.replace('Subject:', '').strip()
            elif not line.startswith('Subject:'):
                content_lines.append(line)
        
        content = '\n'.join(content_lines).strip()
        return subject_line, content

# Agent registry
AGENTS = {
    'blog_writer': BlogPostAgent,
    'social_media': SocialMediaAgent,
    'newsletter': NewsletterAgent
}

def get_content_agent(agent_type: str, config: Dict[str, Any], llm_config: Dict[str, Any]) -> Optional[BaseContentAgent]:
    """Get a content agent instance by type"""
    agent_class = AGENTS.get(agent_type)
    if agent_class:
        return agent_class(config, llm_config)
    return None