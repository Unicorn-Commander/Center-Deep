"""
Agent Scheduler
Manages execution of scrapers and content agents
"""

import schedule
import threading
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import uuid
from contextlib import contextmanager

from app import app, db
from .models import DataScraper, ScrapedData, ContentAgent, GeneratedContent, AgentSchedule
from .scrapers import get_scraper
from .content_agents import get_content_agent

logger = logging.getLogger(__name__)

class AgentScheduler:
    """Manages scheduling and execution of scrapers and content agents"""
    
    def __init__(self):
        self.scheduler = schedule.Scheduler()
        self.running = False
        self.scheduler_thread = None
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Agent scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Agent scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        logger.info("Scheduler thread started")
        
        while self.running:
            try:
                self.scheduler.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
        
        logger.info("Scheduler thread stopped")
    
    def setup_schedules(self):
        """Setup all schedules from database"""
        with app.app_context():
            # Clear existing schedules
            self.scheduler.clear()
            
            # Setup scraper schedules
            scrapers = DataScraper.query.filter_by(enabled=True).all()
            for scraper in scrapers:
                self._schedule_scraper(scraper)
            
            # Setup agent schedules
            agents = ContentAgent.query.filter_by(enabled=True).all()
            for agent in agents:
                self._schedule_agent(agent)
            
            logger.info(f"Setup {len(scrapers)} scraper schedules and {len(agents)} agent schedules")
    
    def _schedule_scraper(self, scraper: DataScraper):
        """Schedule a scraper based on its configuration"""
        schedule_type = scraper.schedule
        scraper_id = scraper.id
        
        try:
            if schedule_type == 'hourly':
                self.scheduler.every().hour.do(self._run_scraper, scraper_id)
            elif schedule_type == 'daily':
                self.scheduler.every().day.at("06:00").do(self._run_scraper, scraper_id)
            elif schedule_type == 'weekly':
                self.scheduler.every().week.do(self._run_scraper, scraper_id)
            elif schedule_type.startswith('custom:'):
                # Custom cron-like expressions (simplified)
                # Format: custom:HH:MM for daily at specific time
                try:
                    _, time_part = schedule_type.split(':', 1)
                    self.scheduler.every().day.at(time_part).do(self._run_scraper, scraper_id)
                except ValueError:
                    logger.error(f"Invalid custom schedule format for scraper {scraper_id}: {schedule_type}")
            
            logger.info(f"Scheduled scraper {scraper.name} ({scraper_id}) to run {schedule_type}")
            
        except Exception as e:
            logger.error(f"Error scheduling scraper {scraper_id}: {e}")
    
    def _schedule_agent(self, agent: ContentAgent):
        """Schedule a content agent based on its configuration"""
        schedule_type = agent.schedule
        agent_id = agent.id
        
        try:
            if schedule_type == 'hourly':
                self.scheduler.every().hour.do(self._run_agent, agent_id)
            elif schedule_type == 'daily':
                self.scheduler.every().day.at("08:00").do(self._run_agent, agent_id)
            elif schedule_type == 'weekly':
                self.scheduler.every().monday.at("09:00").do(self._run_agent, agent_id)
            elif schedule_type.startswith('custom:'):
                # Custom cron-like expressions (simplified)
                try:
                    _, time_part = schedule_type.split(':', 1)
                    self.scheduler.every().day.at(time_part).do(self._run_agent, agent_id)
                except ValueError:
                    logger.error(f"Invalid custom schedule format for agent {agent_id}: {schedule_type}")
            
            logger.info(f"Scheduled agent {agent.name} ({agent_id}) to run {schedule_type}")
            
        except Exception as e:
            logger.error(f"Error scheduling agent {agent_id}: {e}")
    
    def _run_scraper(self, scraper_id: int):
        """Execute a scraper"""
        with app.app_context():
            try:
                scraper_config = DataScraper.query.get(scraper_id)
                if not scraper_config or not scraper_config.enabled:
                    logger.warning(f"Scraper {scraper_id} not found or disabled")
                    return
                
                logger.info(f"Running scraper: {scraper_config.name}")
                
                # Get scraper instance
                scraper = get_scraper(scraper_config.scraper_type, scraper_config.config)
                if not scraper:
                    logger.error(f"Could not create scraper of type {scraper_config.scraper_type}")
                    return
                
                # Run scraper
                start_time = datetime.now(timezone.utc)
                scraped_items = scraper.scrape()
                
                # Save scraped data
                saved_count = 0
                for item in scraped_items:
                    # Check for duplicates based on URL
                    existing = ScrapedData.query.filter_by(
                        scraper_id=scraper_id,
                        url=item.get('url')
                    ).first()
                    
                    if not existing:
                        scraped_data = ScrapedData(
                            scraper_id=scraper_id,
                            title=item.get('title', ''),
                            content=item.get('content', ''),
                            url=item.get('url', ''),
                            metadata=item.get('metadata', {}),
                            scraped_at=start_time
                        )
                        db.session.add(scraped_data)
                        saved_count += 1
                
                # Update scraper run info
                scraper_config.last_run = start_time
                scraper_config.next_run = self._calculate_next_run(scraper_config.schedule, start_time)
                
                db.session.commit()
                
                logger.info(f"Scraper {scraper_config.name} completed: {saved_count} new items saved")
                
            except Exception as e:
                logger.error(f"Error running scraper {scraper_id}: {e}")
                db.session.rollback()
    
    def _run_agent(self, agent_id: int):
        """Execute a content agent"""
        with app.app_context():
            try:
                agent_config = ContentAgent.query.get(agent_id)
                if not agent_config or not agent_config.enabled:
                    logger.warning(f"Agent {agent_id} not found or disabled")
                    return
                
                logger.info(f"Running agent: {agent_config.name}")
                
                # Get LLM configuration
                llm_config = {}
                if agent_config.llm_provider:
                    llm_config = {
                        'api_base': agent_config.llm_provider.api_base,
                        'api_key': agent_config.llm_provider.api_key,
                        'model_name': agent_config.llm_provider.model_name,
                        'temperature': agent_config.temperature,
                        'max_tokens': agent_config.max_tokens
                    }
                
                # Get content agent instance
                agent = get_content_agent(
                    agent_config.agent_type,
                    {
                        'name': agent_config.name,
                        'agent_type': agent_config.agent_type,
                        'system_prompt': agent_config.system_prompt,
                        **agent_config.__dict__  # Include other config
                    },
                    llm_config
                )
                
                if not agent:
                    logger.error(f"Could not create agent of type {agent_config.agent_type}")
                    return
                
                # Get source data
                source_data = self._get_source_data_for_agent(agent_config)
                if not source_data:
                    logger.warning(f"No source data available for agent {agent_config.name}")
                    return
                
                # Generate content
                start_time = datetime.now(timezone.utc)
                generated_items = agent.generate_content(source_data)
                
                # Save generated content
                saved_count = 0
                for item in generated_items:
                    content = GeneratedContent(
                        agent_id=agent_id,
                        title=item.get('title', ''),
                        content=item.get('content', ''),
                        content_type=item.get('content_type', 'generic'),
                        metadata=item.get('metadata', {}),
                        source_data_ids=item.get('source_data_ids', []),
                        status='approved' if agent_config.auto_approve else 'pending',
                        generated_at=start_time
                    )
                    
                    if agent_config.auto_approve:
                        content.approved_at = start_time
                    
                    db.session.add(content)
                    saved_count += 1
                
                # Update agent run info
                agent_config.last_run = start_time
                agent_config.next_run = self._calculate_next_run(agent_config.schedule, start_time)
                
                db.session.commit()
                
                logger.info(f"Agent {agent_config.name} completed: {saved_count} items generated")
                
            except Exception as e:
                logger.error(f"Error running agent {agent_id}: {e}")
                db.session.rollback()
    
    def _get_source_data_for_agent(self, agent_config: ContentAgent) -> List[Dict[str, Any]]:
        """Get source data for a content agent"""
        data_sources = agent_config.data_sources or []
        if not data_sources:
            return []
        
        # Get recent unprocessed data from specified scrapers
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)  # Last week's data
        
        query = ScrapedData.query.filter(
            ScrapedData.scraper_id.in_(data_sources),
            ScrapedData.scraped_at >= cutoff_date,
            ScrapedData.processed == False
        ).order_by(ScrapedData.scraped_at.desc())
        
        scraped_items = query.limit(50).all()  # Limit to prevent overwhelming the LLM
        
        # Convert to dict format
        source_data = []
        for item in scraped_items:
            source_data.append({
                'id': item.id,
                'title': item.title,
                'content': item.content,
                'url': item.url,
                'metadata': item.metadata or {}
            })
        
        # Mark as processed
        for item in scraped_items:
            item.processed = True
        
        return source_data
    
    def _calculate_next_run(self, schedule_type: str, last_run: datetime) -> datetime:
        """Calculate next run time based on schedule"""
        if schedule_type == 'hourly':
            return last_run + timedelta(hours=1)
        elif schedule_type == 'daily':
            return last_run + timedelta(days=1)
        elif schedule_type == 'weekly':
            return last_run + timedelta(weeks=1)
        elif schedule_type.startswith('custom:'):
            # For custom schedules, default to daily
            return last_run + timedelta(days=1)
        else:
            return last_run + timedelta(days=1)
    
    def run_scraper_now(self, scraper_id: int) -> bool:
        """Manually run a scraper immediately"""
        try:
            self._run_scraper(scraper_id)
            return True
        except Exception as e:
            logger.error(f"Error manually running scraper {scraper_id}: {e}")
            return False
    
    def run_agent_now(self, agent_id: int) -> bool:
        """Manually run an agent immediately"""
        try:
            self._run_agent(agent_id)
            return True
        except Exception as e:
            logger.error(f"Error manually running agent {agent_id}: {e}")
            return False

# Global scheduler instance
scheduler = AgentScheduler()

def start_scheduler():
    """Start the global scheduler"""
    scheduler.setup_schedules()
    scheduler.start()

def stop_scheduler():
    """Stop the global scheduler"""
    scheduler.stop()

def restart_scheduler():
    """Restart the scheduler with updated configuration"""
    scheduler.stop()
    time.sleep(1)
    scheduler.setup_schedules()
    scheduler.start()