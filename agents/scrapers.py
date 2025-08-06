"""
Data Scrapers Implementation
Simple but effective scrapers for various data sources
"""

import requests
import feedparser
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class BaseScraper:
    """Base class for all scrapers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Center Deep Agent/1.0 (https://github.com/MagicUnicornInc/Center-Deep)'
        })
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Override this method in subclasses"""
        raise NotImplementedError
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common unwanted patterns
        text = re.sub(r'\[.*?\]', '', text)  # Remove [brackets]
        text = re.sub(r'<.*?>', '', text)    # Remove HTML tags
        
        return text
    
    def safe_request(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """Make a safe HTTP request with error handling"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None

class RSSFeedScraper(BaseScraper):
    """Scraper for RSS feeds"""
    
    def scrape(self) -> List[Dict[str, Any]]:
        results = []
        feeds = self.config.get('feeds', [])
        max_items_per_feed = self.config.get('max_items_per_feed', 10)
        
        for feed_config in feeds:
            feed_url = feed_config['url']
            feed_name = feed_config.get('name', feed_url)
            
            try:
                logger.info(f"Scraping RSS feed: {feed_name}")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    logger.warning(f"Feed parsing warning for {feed_name}: {feed.bozo_exception}")
                
                for entry in feed.entries[:max_items_per_feed]:
                    # Extract publish date
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                    
                    # Extract content
                    content = ""
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    
                    results.append({
                        'title': self.clean_text(entry.get('title', '')),
                        'content': self.clean_text(content),
                        'url': entry.get('link', ''),
                        'metadata': {
                            'source': feed_name,
                            'author': entry.get('author', ''),
                            'published': published.isoformat() if published else None,
                            'tags': [tag.term for tag in entry.get('tags', [])],
                            'scraper_type': 'rss'
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Error scraping RSS feed {feed_name}: {e}")
                continue
        
        logger.info(f"RSS scraper collected {len(results)} items")
        return results

class GitHubScraper(BaseScraper):
    """Scraper for GitHub repository activity"""
    
    def scrape(self) -> List[Dict[str, Any]]:
        results = []
        repositories = self.config.get('repositories', [])
        github_token = self.config.get('github_token')  # Optional for higher rate limits
        
        if github_token:
            self.session.headers['Authorization'] = f'token {github_token}'
        
        for repo in repositories:
            try:
                logger.info(f"Scraping GitHub repo: {repo}")
                
                # Get recent releases
                releases_url = f"https://api.github.com/repos/{repo}/releases"
                response = self.safe_request(releases_url)
                
                if response:
                    releases = response.json()[:5]  # Last 5 releases
                    
                    for release in releases:
                        results.append({
                            'title': f"New Release: {release['name']} - {repo}",
                            'content': self.clean_text(release.get('body', '')),
                            'url': release['html_url'],
                            'metadata': {
                                'source': f'GitHub - {repo}',
                                'published': release['published_at'],
                                'author': release.get('author', {}).get('login', ''),
                                'version': release['tag_name'],
                                'scraper_type': 'github_release'
                            }
                        })
                
                # Get recent issues (optional)
                if self.config.get('include_issues', False):
                    issues_url = f"https://api.github.com/repos/{repo}/issues?state=open&sort=created&per_page=5"
                    response = self.safe_request(issues_url)
                    
                    if response:
                        issues = response.json()
                        
                        for issue in issues:
                            # Skip pull requests (they appear as issues in GitHub API)
                            if 'pull_request' in issue:
                                continue
                                
                            results.append({
                                'title': f"Issue: {issue['title']} - {repo}",
                                'content': self.clean_text(issue.get('body', '')),
                                'url': issue['html_url'],
                                'metadata': {
                                    'source': f'GitHub Issues - {repo}',
                                    'published': issue['created_at'],
                                    'author': issue.get('user', {}).get('login', ''),
                                    'labels': [label['name'] for label in issue.get('labels', [])],
                                    'scraper_type': 'github_issue'
                                }
                            })
                
                # Rate limiting - be nice to GitHub
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping GitHub repo {repo}: {e}")
                continue
        
        logger.info(f"GitHub scraper collected {len(results)} items")
        return results

class RedditScraper(BaseScraper):
    """Scraper for Reddit subreddits"""
    
    def scrape(self) -> List[Dict[str, Any]]:
        results = []
        subreddits = self.config.get('subreddits', [])
        sort_by = self.config.get('sort_by', 'hot')  # hot, new, top
        limit = self.config.get('limit', 10)
        
        for subreddit in subreddits:
            try:
                logger.info(f"Scraping Reddit: r/{subreddit}")
                
                url = f"https://www.reddit.com/r/{subreddit}/{sort_by}.json?limit={limit}"
                response = self.safe_request(url)
                
                if response:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post_data in posts:
                        post = post_data['data']
                        
                        # Skip stickied posts unless configured to include them
                        if post.get('stickied') and not self.config.get('include_stickied', False):
                            continue
                        
                        # Combine title and selftext for content
                        content = ""
                        if post.get('selftext'):
                            content = post['selftext']
                        elif post.get('url') and not post['url'].startswith('https://www.reddit.com'):
                            content = f"Link post: {post['url']}"
                        
                        results.append({
                            'title': self.clean_text(post['title']),
                            'content': self.clean_text(content),
                            'url': f"https://www.reddit.com{post['permalink']}",
                            'metadata': {
                                'source': f'Reddit - r/{subreddit}',
                                'author': post.get('author', ''),
                                'published': datetime.fromtimestamp(post['created_utc'], tz=timezone.utc).isoformat(),
                                'score': post.get('score', 0),
                                'num_comments': post.get('num_comments', 0),
                                'subreddit': post['subreddit'],
                                'flair': post.get('link_flair_text', ''),
                                'scraper_type': 'reddit'
                            }
                        })
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping Reddit r/{subreddit}: {e}")
                continue
        
        logger.info(f"Reddit scraper collected {len(results)} items")
        return results

class CustomURLScraper(BaseScraper):
    """Scraper for custom URLs with CSS selectors"""
    
    def scrape(self) -> List[Dict[str, Any]]:
        results = []
        urls = self.config.get('urls', [])
        
        for url_config in urls:
            url = url_config['url']
            name = url_config.get('name', url)
            selectors = url_config.get('selectors', {})
            
            try:
                logger.info(f"Scraping custom URL: {name}")
                response = self.safe_request(url)
                
                if response:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract items using selectors
                    item_selector = selectors.get('item', 'article')
                    items = soup.select(item_selector)
                    
                    for item in items[:self.config.get('max_items', 10)]:
                        title = ""
                        content = ""
                        item_url = url
                        
                        # Extract title
                        if 'title' in selectors:
                            title_elem = item.select_one(selectors['title'])
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                        
                        # Extract content
                        if 'content' in selectors:
                            content_elem = item.select_one(selectors['content'])
                            if content_elem:
                                content = content_elem.get_text(strip=True)
                        
                        # Extract URL if available
                        if 'url' in selectors:
                            url_elem = item.select_one(selectors['url'])
                            if url_elem:
                                href = url_elem.get('href')
                                if href:
                                    item_url = urljoin(url, href)
                        
                        if title or content:  # Only add if we got some content
                            results.append({
                                'title': self.clean_text(title),
                                'content': self.clean_text(content),
                                'url': item_url,
                                'metadata': {
                                    'source': name,
                                    'domain': urlparse(url).netloc,
                                    'scraper_type': 'custom_url'
                                }
                            })
                
            except Exception as e:
                logger.error(f"Error scraping custom URL {name}: {e}")
                continue
        
        logger.info(f"Custom URL scraper collected {len(results)} items")
        return results

# Scraper registry
SCRAPERS = {
    'rss': RSSFeedScraper,
    'github': GitHubScraper,
    'reddit': RedditScraper,
    'custom_url': CustomURLScraper
}

def get_scraper(scraper_type: str, config: Dict[str, Any]) -> Optional[BaseScraper]:
    """Get a scraper instance by type"""
    scraper_class = SCRAPERS.get(scraper_type)
    if scraper_class:
        return scraper_class(config)
    return None