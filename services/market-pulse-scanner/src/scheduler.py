import asyncio
import schedule
import time
from typing import List
from datetime import datetime, timedelta
import logging
import threading

logger = logging.getLogger(__name__)

class PulseScheduler:
    """
    Scheduler for automated market pulse scanning
    """
    
    def __init__(self, scanner, nlp_processor, db_manager, kafka_publisher):
        self.scanner = scanner
        self.nlp_processor = nlp_processor
        self.db_manager = db_manager
        self.kafka_publisher = kafka_publisher
        
        self.is_running_flag = False
        self.scheduler_thread = None
        self.monitored_companies = []
        self.scan_interval_minutes = 30
        
        # Setup default schedule
        self.setup_schedule()
    
    def setup_schedule(self):
        """Setup the scanning schedule"""
        schedule.clear()
        schedule.every(self.scan_interval_minutes).minutes.do(self._run_scheduled_scan)
        logger.info(f"Scheduled scans every {self.scan_interval_minutes} minutes")
    
    def start(self):
        """Start the scheduler"""
        if self.is_running_flag:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running_flag = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Pulse scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running_flag = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Pulse scheduler stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.is_running_flag
    
    def update_schedule(self, interval_minutes: int, companies: List[str]):
        """Update the scanning schedule"""
        self.scan_interval_minutes = interval_minutes
        self.monitored_companies = companies
        self.setup_schedule()
        logger.info(f"Updated schedule: {interval_minutes} minutes, monitoring {len(companies)} companies")
    
    def get_next_scan_time(self) -> datetime:
        """Get the next scheduled scan time"""
        next_run = schedule.next_run()
        return next_run if next_run else datetime.utcnow() + timedelta(minutes=self.scan_interval_minutes)
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running_flag:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(5)
    
    def _run_scheduled_scan(self):
        """Execute scheduled scan"""
        try:
            if not self.monitored_companies:
                logger.info("No companies configured for monitoring")
                return
            
            logger.info(f"Starting scheduled scan for {len(self.monitored_companies)} companies")
            
            # Run async scan in new event loop
            asyncio.run(self._execute_scheduled_scan())
            
        except Exception as e:
            logger.error(f"Scheduled scan failed: {e}")
    
    async def _execute_scheduled_scan(self):
        """Execute the actual scanning process"""
        try:
            for company in self.monitored_companies:
                try:
                    scan_id = f"scheduled_{company.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}"
                    
                    logger.info(f"Scanning {company} (scan_id: {scan_id})")
                    
                    # Create scan record
                    await self._create_scan_record(scan_id, company)
                    
                    # Scan all sources
                    raw_documents = await self.scanner.scan_all_sources(
                        company=company,
                        sources=["crunchbase", "linkedin", "news", "twitter"],
                        deep_scan=False
                    )
                    
                    # Process documents
                    processed_events = []
                    for doc in raw_documents:
                        try:
                            entities = await self.nlp_processor.extract_entities(doc['content'])
                            sentiment = await self.nlp_processor.analyze_sentiment(doc['content'])
                            
                            event = {
                                'event_id': f"{scan_id}_{len(processed_events)}",
                                'scan_id': scan_id,
                                'company': company,
                                'source': doc['source'],
                                'type': doc.get('type', 'unknown'),
                                'content': doc['content'],
                                'url': doc.get('url'),
                                'entities': entities,
                                'sentiment': sentiment,
                                'timestamp': doc['timestamp'],
                                'processed_at': datetime.utcnow()
                            }
                            
                            processed_events.append(event)
                            
                        except Exception as e:
                            logger.error(f"Failed to process document for {company}: {e}")
                            continue
                    
                    # Store results
                    await self.db_manager.store_scan_results(scan_id, company, processed_events)
                    
                    # Publish to Kafka
                    for event in processed_events:
                        await self.kafka_publisher.publish_event("pulse.events", event)
                    
                    logger.info(f"Completed scan for {company}: {len(processed_events)} events")
                    
                    # Small delay between companies to avoid rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Failed to scan {company}: {e}")
                    continue
            
            logger.info("Scheduled scan completed")
            
        except Exception as e:
            logger.error(f"Scheduled scan execution failed: {e}")
    
    async def _create_scan_record(self, scan_id: str, company: str):
        """Create initial scan record in database"""
        try:
            if not self.db_manager.pool:
                return
            
            async with self.db_manager.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO market_pulse_scans (
                        scan_id, company, sources, status
                    ) VALUES ($1, $2, $3, $4)
                    ON CONFLICT (scan_id) DO NOTHING
                """, 
                scan_id, 
                company, 
                ["crunchbase", "linkedin", "news", "twitter"],
                "running"
                )
                
        except Exception as e:
            logger.error(f"Failed to create scan record: {e}")