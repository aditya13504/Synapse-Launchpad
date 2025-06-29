from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import os
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

from src.scanner import MarketPulseScanner
from src.nlp_processor import NLPProcessor
from src.database import DatabaseManager
from src.kafka_publisher import KafkaPublisher
from src.scheduler import PulseScheduler

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    environment=os.getenv("ENVIRONMENT", "development"),
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Synapse LaunchPad - Market Pulse Scanner",
    description="Real-time market intelligence scanner with NLP processing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
scanner = MarketPulseScanner()
nlp_processor = NLPProcessor()
db_manager = DatabaseManager()
kafka_publisher = KafkaPublisher()
scheduler = PulseScheduler(scanner, nlp_processor, db_manager, kafka_publisher)

class ScanRequest(BaseModel):
    company: str
    sources: List[str] = ["crunchbase", "linkedin", "news", "twitter"]
    deep_scan: bool = False

class ScanResult(BaseModel):
    scan_id: str
    company: str
    sources_scanned: List[str]
    documents_found: int
    entities_extracted: int
    sentiment_score: float
    key_insights: List[str]
    timestamp: datetime

class PulseEvent(BaseModel):
    event_id: str
    company: str
    event_type: str
    source: str
    content: str
    entities: Dict[str, Any]
    sentiment: Dict[str, float]
    confidence: float
    timestamp: datetime

@app.on_event("startup")
async def startup_event():
    """Initialize services and start scheduler"""
    try:
        await db_manager.initialize()
        await kafka_publisher.initialize()
        scheduler.start()
        logger.info("Market Pulse Scanner started successfully")
    except Exception as e:
        logger.error(f"Failed to start services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services"""
    try:
        scheduler.stop()
        await kafka_publisher.close()
        await db_manager.close()
        logger.info("Market Pulse Scanner stopped successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "market-pulse-scanner",
        "timestamp": datetime.utcnow(),
        "scheduler_active": scheduler.is_running(),
        "database_connected": await db_manager.health_check(),
        "kafka_connected": await kafka_publisher.health_check()
    }

@app.post("/scan", response_model=ScanResult)
async def manual_scan(
    background_tasks: BackgroundTasks,
    company: str = Query(..., description="Company name to scan"),
    sources: str = Query("crunchbase,linkedin,news,twitter", description="Comma-separated list of sources"),
    deep_scan: bool = Query(False, description="Enable deep scanning with extended analysis")
):
    """
    Manually trigger a market pulse scan for a specific company
    """
    try:
        # Parse sources
        source_list = [s.strip() for s in sources.split(",")]
        
        # Create scan request
        scan_request = ScanRequest(
            company=company,
            sources=source_list,
            deep_scan=deep_scan
        )
        
        # Generate scan ID
        scan_id = f"scan_{company.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}"
        
        # Start background scan
        background_tasks.add_task(
            execute_scan,
            scan_id,
            scan_request
        )
        
        # Return immediate response
        return ScanResult(
            scan_id=scan_id,
            company=company,
            sources_scanned=source_list,
            documents_found=0,  # Will be updated in background
            entities_extracted=0,  # Will be updated in background
            sentiment_score=0.0,  # Will be updated in background
            key_insights=["Scan initiated - results will be available shortly"],
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Manual scan failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@app.get("/scan/{scan_id}")
async def get_scan_results(scan_id: str):
    """
    Get results of a specific scan
    """
    try:
        results = await db_manager.get_scan_results(scan_id)
        if not results:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get scan results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@app.get("/pulse/events", response_model=List[PulseEvent])
async def get_pulse_events(
    company: Optional[str] = Query(None, description="Filter by company"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    hours: int = Query(24, description="Hours to look back"),
    limit: int = Query(100, description="Maximum number of events")
):
    """
    Get recent pulse events
    """
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        events = await db_manager.get_pulse_events(
            company=company,
            event_type=event_type,
            since=since,
            limit=limit
        )
        
        return events
        
    except Exception as e:
        logger.error(f"Failed to get pulse events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@app.get("/pulse/insights/{company}")
async def get_company_insights(company: str):
    """
    Get aggregated insights for a specific company
    """
    try:
        insights = await db_manager.get_company_insights(company)
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get company insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@app.post("/pulse/schedule")
async def update_scan_schedule(
    interval_minutes: int = Query(30, description="Scan interval in minutes"),
    companies: List[str] = Query([], description="Companies to monitor")
):
    """
    Update the automated scanning schedule
    """
    try:
        scheduler.update_schedule(interval_minutes, companies)
        return {
            "status": "success",
            "interval_minutes": interval_minutes,
            "monitored_companies": companies,
            "next_scan": scheduler.get_next_scan_time()
        }
        
    except Exception as e:
        logger.error(f"Failed to update schedule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {str(e)}")

async def execute_scan(scan_id: str, scan_request: ScanRequest):
    """
    Execute a complete market pulse scan
    """
    try:
        logger.info(f"Starting scan {scan_id} for company: {scan_request.company}")
        
        # Step 1: Scan data sources
        raw_documents = await scanner.scan_all_sources(
            company=scan_request.company,
            sources=scan_request.sources,
            deep_scan=scan_request.deep_scan
        )
        
        logger.info(f"Scan {scan_id}: Found {len(raw_documents)} documents")
        
        # Step 2: Process documents with NLP
        processed_events = []
        for doc in raw_documents:
            try:
                # Extract entities and sentiment
                entities = await nlp_processor.extract_entities(doc['content'])
                sentiment = await nlp_processor.analyze_sentiment(doc['content'])
                
                # Create pulse event
                event = {
                    'event_id': f"{scan_id}_{len(processed_events)}",
                    'scan_id': scan_id,
                    'company': scan_request.company,
                    'source': doc['source'],
                    'content': doc['content'],
                    'url': doc.get('url'),
                    'entities': entities,
                    'sentiment': sentiment,
                    'timestamp': doc['timestamp'],
                    'processed_at': datetime.utcnow()
                }
                
                processed_events.append(event)
                
            except Exception as e:
                logger.error(f"Failed to process document: {e}")
                continue
        
        logger.info(f"Scan {scan_id}: Processed {len(processed_events)} events")
        
        # Step 3: Store in database
        await db_manager.store_scan_results(scan_id, scan_request.company, processed_events)
        
        # Step 4: Publish to Kafka
        for event in processed_events:
            await kafka_publisher.publish_event("pulse.events", event)
        
        logger.info(f"Scan {scan_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}")
        # Store error in database
        await db_manager.store_scan_error(scan_id, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)