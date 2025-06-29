import asyncpg
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Database manager using Supabase/PostgreSQL for storing scan results
    """
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.database_url = os.getenv("DATABASE_URL")
        
        self.supabase: Optional[Client] = None
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize database connections"""
        try:
            # Initialize Supabase client
            if self.supabase_url and self.supabase_key:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Initialize direct PostgreSQL connection pool
            if self.database_url:
                self.pool = await asyncpg.create_pool(self.database_url)
            
            # Create tables if they don't exist
            await self._create_tables()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        try:
            if self.pool:
                await self.pool.close()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            if self.pool:
                async with self.pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                return True
            return False
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def _create_tables(self):
        """Create necessary tables for market pulse data"""
        try:
            if not self.pool:
                return
            
            async with self.pool.acquire() as conn:
                # Market pulse scans table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS market_pulse_scans (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        scan_id VARCHAR(255) UNIQUE NOT NULL,
                        company VARCHAR(255) NOT NULL,
                        sources TEXT[] NOT NULL,
                        status VARCHAR(50) DEFAULT 'running',
                        documents_found INTEGER DEFAULT 0,
                        entities_extracted INTEGER DEFAULT 0,
                        sentiment_score DECIMAL(3,2) DEFAULT 0.0,
                        error_message TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        completed_at TIMESTAMPTZ
                    )
                """)
                
                # Market pulse events table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS market_pulse_events (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        event_id VARCHAR(255) UNIQUE NOT NULL,
                        scan_id VARCHAR(255) REFERENCES market_pulse_scans(scan_id),
                        company VARCHAR(255) NOT NULL,
                        source VARCHAR(100) NOT NULL,
                        event_type VARCHAR(100) NOT NULL,
                        content TEXT NOT NULL,
                        url TEXT,
                        entities JSONB DEFAULT '{}',
                        sentiment JSONB DEFAULT '{}',
                        confidence DECIMAL(3,2) DEFAULT 0.0,
                        timestamp TIMESTAMPTZ NOT NULL,
                        processed_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                
                # Create indexes for better performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_pulse_events_company 
                    ON market_pulse_events(company)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_pulse_events_timestamp 
                    ON market_pulse_events(timestamp)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_pulse_events_source 
                    ON market_pulse_events(source)
                """)
                
                logger.info("Database tables created/verified successfully")
                
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    async def store_scan_results(
        self, 
        scan_id: str, 
        company: str, 
        events: List[Dict[str, Any]]
    ):
        """Store scan results and events in database"""
        try:
            if not self.pool:
                return
            
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Update scan record
                    await conn.execute("""
                        UPDATE market_pulse_scans 
                        SET status = 'completed',
                            documents_found = $1,
                            entities_extracted = $2,
                            sentiment_score = $3,
                            completed_at = NOW()
                        WHERE scan_id = $4
                    """, 
                    len(events),
                    sum(len(event.get('entities', {})) for event in events),
                    sum(event.get('sentiment', {}).get('compound', 0) for event in events) / max(len(events), 1),
                    scan_id
                    )
                    
                    # Insert events
                    for event in events:
                        await conn.execute("""
                            INSERT INTO market_pulse_events (
                                event_id, scan_id, company, source, event_type,
                                content, url, entities, sentiment, confidence, timestamp
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                            ON CONFLICT (event_id) DO NOTHING
                        """,
                        event['event_id'],
                        event['scan_id'],
                        event['company'],
                        event['source'],
                        event.get('type', 'unknown'),
                        event['content'],
                        event.get('url'),
                        json.dumps(event.get('entities', {})),
                        json.dumps(event.get('sentiment', {})),
                        event.get('sentiment', {}).get('confidence', 0.0),
                        event['timestamp']
                        )
            
            logger.info(f"Stored {len(events)} events for scan {scan_id}")
            
        except Exception as e:
            logger.error(f"Failed to store scan results: {e}")
            raise
    
    async def store_scan_error(self, scan_id: str, error_message: str):
        """Store scan error in database"""
        try:
            if not self.pool:
                return
            
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE market_pulse_scans 
                    SET status = 'failed',
                        error_message = $1,
                        completed_at = NOW()
                    WHERE scan_id = $2
                """, error_message, scan_id)
            
            logger.info(f"Stored error for scan {scan_id}")
            
        except Exception as e:
            logger.error(f"Failed to store scan error: {e}")
    
    async def get_scan_results(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan results by scan ID"""
        try:
            if not self.pool:
                return None
            
            async with self.pool.acquire() as conn:
                # Get scan info
                scan_row = await conn.fetchrow("""
                    SELECT * FROM market_pulse_scans WHERE scan_id = $1
                """, scan_id)
                
                if not scan_row:
                    return None
                
                # Get events
                event_rows = await conn.fetch("""
                    SELECT * FROM market_pulse_events 
                    WHERE scan_id = $1 
                    ORDER BY timestamp DESC
                """, scan_id)
                
                return {
                    "scan_id": scan_row["scan_id"],
                    "company": scan_row["company"],
                    "sources": scan_row["sources"],
                    "status": scan_row["status"],
                    "documents_found": scan_row["documents_found"],
                    "entities_extracted": scan_row["entities_extracted"],
                    "sentiment_score": float(scan_row["sentiment_score"]) if scan_row["sentiment_score"] else 0.0,
                    "error_message": scan_row["error_message"],
                    "created_at": scan_row["created_at"],
                    "completed_at": scan_row["completed_at"],
                    "events": [dict(row) for row in event_rows]
                }
                
        except Exception as e:
            logger.error(f"Failed to get scan results: {e}")
            return None
    
    async def get_pulse_events(
        self,
        company: Optional[str] = None,
        event_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get pulse events with optional filters"""
        try:
            if not self.pool:
                return []
            
            query = "SELECT * FROM market_pulse_events WHERE 1=1"
            params = []
            param_count = 0
            
            if company:
                param_count += 1
                query += f" AND company ILIKE ${param_count}"
                params.append(f"%{company}%")
            
            if event_type:
                param_count += 1
                query += f" AND event_type = ${param_count}"
                params.append(event_type)
            
            if since:
                param_count += 1
                query += f" AND timestamp >= ${param_count}"
                params.append(since)
            
            query += f" ORDER BY timestamp DESC LIMIT ${param_count + 1}"
            params.append(limit)
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get pulse events: {e}")
            return []
    
    async def get_company_insights(self, company: str) -> Dict[str, Any]:
        """Get aggregated insights for a company"""
        try:
            if not self.pool:
                return {}
            
            async with self.pool.acquire() as conn:
                # Get recent events count by source
                source_counts = await conn.fetch("""
                    SELECT source, COUNT(*) as count
                    FROM market_pulse_events 
                    WHERE company ILIKE $1 
                    AND timestamp >= NOW() - INTERVAL '30 days'
                    GROUP BY source
                """, f"%{company}%")
                
                # Get average sentiment
                avg_sentiment = await conn.fetchrow("""
                    SELECT 
                        AVG((sentiment->>'compound')::float) as avg_compound,
                        AVG((sentiment->>'positive')::float) as avg_positive,
                        AVG((sentiment->>'negative')::float) as avg_negative
                    FROM market_pulse_events 
                    WHERE company ILIKE $1 
                    AND timestamp >= NOW() - INTERVAL '30 days'
                    AND sentiment->>'compound' IS NOT NULL
                """, f"%{company}%")
                
                # Get recent funding mentions
                funding_events = await conn.fetch("""
                    SELECT content, timestamp, url
                    FROM market_pulse_events 
                    WHERE company ILIKE $1 
                    AND (content ILIKE '%funding%' OR content ILIKE '%raised%' OR content ILIKE '%investment%')
                    AND timestamp >= NOW() - INTERVAL '90 days'
                    ORDER BY timestamp DESC
                    LIMIT 5
                """, f"%{company}%")
                
                return {
                    "company": company,
                    "source_distribution": {row["source"]: row["count"] for row in source_counts},
                    "sentiment_analysis": {
                        "average_compound": float(avg_sentiment["avg_compound"]) if avg_sentiment["avg_compound"] else 0.0,
                        "average_positive": float(avg_sentiment["avg_positive"]) if avg_sentiment["avg_positive"] else 0.0,
                        "average_negative": float(avg_sentiment["avg_negative"]) if avg_sentiment["avg_negative"] else 0.0,
                    },
                    "recent_funding_mentions": [
                        {
                            "content": row["content"][:200] + "..." if len(row["content"]) > 200 else row["content"],
                            "timestamp": row["timestamp"],
                            "url": row["url"]
                        }
                        for row in funding_events
                    ],
                    "analysis_period": "30 days",
                    "last_updated": datetime.utcnow()
                }
                
        except Exception as e:
            logger.error(f"Failed to get company insights: {e}")
            return {}