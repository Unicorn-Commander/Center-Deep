"""
Center Deep Search Engine
Built-in search functionality - no external dependencies
This replaces the need for a separate SearXNG container
"""

import asyncio
import aiohttp
import json
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import re
from bs4 import BeautifulSoup

class SearchEngine:
    """Core search engine functionality for Center Deep"""
    
    def __init__(self, settings_path='searxng/settings.yml'):
        self.engines = self._load_engines()
        self.timeout = 10
        self.max_results = 20
        
    def _load_engines(self) -> Dict:
        """Load search engine configurations"""
        return {
            'general': {
                'google': {
                    'url': 'https://www.google.com/search',
                    'params': lambda q: {'q': q, 'num': 10},
                    'parser': 'google',
                    'weight': 1.0
                },
                'brave': {
                    'url': 'https://search.brave.com/search',
                    'params': lambda q: {'q': q},
                    'parser': 'brave',
                    'weight': 1.2
                },
                'duckduckgo': {
                    'url': 'https://duckduckgo.com/html/',
                    'params': lambda q: {'q': q},
                    'parser': 'ddg',
                    'weight': 1.1
                },
                'bing': {
                    'url': 'https://www.bing.com/search',
                    'params': lambda q: {'q': q},
                    'parser': 'bing',
                    'weight': 0.9
                },
                'startpage': {
                    'url': 'https://www.startpage.com/sp/search',
                    'params': lambda q: {'query': q},
                    'parser': 'startpage',
                    'weight': 1.0
                },
                'qwant': {
                    'url': 'https://api.qwant.com/v3/search/web',
                    'params': lambda q: {'q': q, 'count': 10, 'locale': 'en_US'},
                    'parser': 'qwant_api',
                    'weight': 0.9
                }
            },
            'images': {
                'google_images': {
                    'url': 'https://www.google.com/search',
                    'params': lambda q: {'q': q, 'tbm': 'isch'},
                    'parser': 'google_images',
                    'weight': 1.0
                },
                'bing_images': {
                    'url': 'https://www.bing.com/images/search',
                    'params': lambda q: {'q': q},
                    'parser': 'bing_images',
                    'weight': 0.9
                }
            },
            'videos': {
                'youtube': {
                    'url': 'https://www.youtube.com/results',
                    'params': lambda q: {'search_query': q},
                    'parser': 'youtube',
                    'weight': 1.2
                }
            },
            'news': {
                'google_news': {
                    'url': 'https://news.google.com/search',
                    'params': lambda q: {'q': q},
                    'parser': 'google_news',
                    'weight': 1.0
                }
            }
        }
    
    async def search(self, query: str, categories: List[str] = None, 
                    page: int = 1, safesearch: int = 0,
                    time_range: str = '', language: str = '') -> Dict[str, Any]:
        """
        Perform a search across multiple engines
        """
        if not categories:
            categories = ['general']
        
        all_results = []
        errors = []
        
        # Collect tasks for all engines in selected categories
        tasks = []
        for category in categories:
            if category in self.engines:
                for engine_name, engine_config in self.engines[category].items():
                    task = self._search_engine(
                        engine_name, engine_config, query, page
                    )
                    tasks.append(task)
        
        # Execute all searches in parallel
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    errors.append(str(result))
                elif result:
                    all_results.extend(result)
        
        # Deduplicate and rank results
        final_results = self._process_results(all_results)
        
        return {
            'results': final_results[:self.max_results],
            'query': query,
            'number_of_results': len(final_results),
            'errors': errors if errors else None
        }
    
    async def _search_engine(self, engine_name: str, config: Dict, 
                            query: str, page: int) -> List[Dict]:
        """Search a single engine"""
        try:
            async with aiohttp.ClientSession() as session:
                params = config['params'](query)
                if page > 1:
                    params['start'] = (page - 1) * 10
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(
                    config['url'],
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        results = self._parse_results(
                            content, config['parser'], engine_name
                        )
                        # Apply weight to results
                        for result in results:
                            result['score'] = config.get('weight', 1.0)
                            result['engine'] = engine_name
                        return results
        except Exception as e:
            print(f"Error searching {engine_name}: {e}")
        return []
    
    def _parse_results(self, content: str, parser_type: str, 
                      engine_name: str) -> List[Dict]:
        """Parse search results based on engine type"""
        results = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            if parser_type == 'google':
                # Parse Google search results
                for g in soup.find_all('div', class_='g'):
                    title_elem = g.find('h3')
                    if title_elem:
                        link_elem = g.find('a')
                        snippet_elem = g.find('span', class_='st') or g.find('div', class_='VwiC3b')
                        
                        if link_elem and link_elem.get('href'):
                            results.append({
                                'title': title_elem.get_text(),
                                'url': link_elem['href'],
                                'content': snippet_elem.get_text() if snippet_elem else '',
                                'engine': engine_name
                            })
            
            elif parser_type == 'brave':
                # Parse Brave search results
                for item in soup.find_all('div', class_='snippet'):
                    title_elem = item.find('a', class_='result-header')
                    if title_elem:
                        snippet_elem = item.find('p', class_='snippet-description')
                        results.append({
                            'title': title_elem.get_text(),
                            'url': title_elem['href'],
                            'content': snippet_elem.get_text() if snippet_elem else '',
                            'engine': engine_name
                        })
            
            elif parser_type == 'ddg':
                # Parse DuckDuckGo HTML results
                for result in soup.find_all('div', class_=['result', 'results_links']):
                    title_elem = result.find('a', class_='result__a')
                    if title_elem:
                        snippet_elem = result.find('a', class_='result__snippet')
                        results.append({
                            'title': title_elem.get_text(),
                            'url': title_elem['href'],
                            'content': snippet_elem.get_text() if snippet_elem else '',
                            'engine': engine_name
                        })
            
            elif parser_type == 'qwant_api':
                # Parse Qwant API JSON response
                try:
                    data = json.loads(content)
                    if 'data' in data and 'result' in data['data']:
                        for item in data['data']['result'].get('items', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('url', ''),
                                'content': item.get('desc', ''),
                                'engine': engine_name
                            })
                except json.JSONDecodeError:
                    pass
            
            elif parser_type == 'bing':
                # Parse Bing search results
                for li in soup.find_all('li', class_='b_algo'):
                    h2 = li.find('h2')
                    if h2:
                        a = h2.find('a')
                        if a:
                            snippet = li.find('div', class_='b_caption')
                            if snippet:
                                p = snippet.find('p')
                                results.append({
                                    'title': a.get_text(),
                                    'url': a['href'],
                                    'content': p.get_text() if p else '',
                                    'engine': engine_name
                                })
                                
        except Exception as e:
            print(f"Error parsing {parser_type} results: {e}")
        
        return results
    
    def _process_results(self, results: List[Dict]) -> List[Dict]:
        """Deduplicate and rank results"""
        seen_urls = set()
        unique_results = []
        
        # Sort by score (weight)
        sorted_results = sorted(results, key=lambda x: x.get('score', 1.0), reverse=True)
        
        for result in sorted_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results

# Singleton instance
search_engine = SearchEngine()

def perform_search(query: str, categories: str = '', page: int = 1,
                  safesearch: int = 0, time_range: str = '',
                  language: str = '') -> Dict[str, Any]:
    """
    Synchronous wrapper for async search
    """
    category_list = categories.split(',') if categories else ['general']
    
    # Run async search in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            search_engine.search(
                query=query,
                categories=category_list,
                page=page,
                safesearch=safesearch,
                time_range=time_range,
                language=language
            )
        )
        return result
    finally:
        loop.close()