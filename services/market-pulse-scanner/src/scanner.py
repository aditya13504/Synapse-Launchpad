import asyncio
import httpx
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
import tweepy
from linkedin_api import Linkedin

logger = logging.getLogger(__name__)

class MarketPulseScanner:
    """
    Multi-source market data scanner
    """
    
    def __init__(self):
        self.crunchbase_key = os.getenv("CRUNCHBASE_KEY")
        self.linkedin_token = os.getenv("LINKEDIN_TOKEN")
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        # Initialize API clients
        self.setup_clients()
    
    def setup_clients(self):
        """Initialize API clients"""
        try:
            # Twitter client
            if self.twitter_bearer_token:
                self.twitter_client = tweepy.Client(bearer_token=self.twitter_bearer_token)
            
            # LinkedIn client (requires username/password - use with caution)
            # self.linkedin_client = Linkedin(username, password)
            
        except Exception as e:
            logger.error(f"Failed to setup API clients: {e}")
    
    async def scan_all_sources(
        self, 
        company: str, 
        sources: List[str], 
        deep_scan: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Scan all specified sources for company data
        """
        all_documents = []
        
        tasks = []
        if "crunchbase" in sources:
            tasks.append(self.scan_crunchbase(company, deep_scan))
        if "linkedin" in sources:
            tasks.append(self.scan_linkedin(company, deep_scan))
        if "news" in sources:
            tasks.append(self.scan_news(company, deep_scan))
        if "twitter" in sources:
            tasks.append(self.scan_twitter(company, deep_scan))
        
        # Execute all scans concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scan failed: {result}")
                continue
            all_documents.extend(result)
        
        return all_documents
    
    async def scan_crunchbase(self, company: str, deep_scan: bool = False) -> List[Dict[str, Any]]:
        """
        Scan Crunchbase for company funding and news data
        """
        documents = []
        
        try:
            async with httpx.AsyncClient() as client:
                # Search for organization
                search_url = "https://api.crunchbase.com/api/v4/searches/organizations"
                headers = {"X-cb-user-key": self.crunchbase_key}
                
                search_payload = {
                    "field_ids": [
                        "identifier",
                        "name",
                        "short_description",
                        "categories",
                        "location_identifiers",
                        "funding_total"
                    ],
                    "query": [
                        {
                            "type": "predicate",
                            "field_id": "name",
                            "operator_id": "contains",
                            "values": [company]
                        }
                    ],
                    "limit": 10 if deep_scan else 5
                }
                
                response = await client.post(search_url, json=search_payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for entity in data.get("entities", []):
                        # Get detailed organization data
                        org_id = entity["identifier"]["value"]
                        org_url = f"https://api.crunchbase.com/api/v4/entities/organizations/{org_id}"
                        
                        org_response = await client.get(org_url, headers=headers)
                        if org_response.status_code == 200:
                            org_data = org_response.json()
                            
                            documents.append({
                                "source": "crunchbase",
                                "type": "organization_profile",
                                "company": company,
                                "content": self._format_crunchbase_content(org_data),
                                "url": f"https://www.crunchbase.com/organization/{org_id}",
                                "timestamp": datetime.utcnow(),
                                "raw_data": org_data
                            })
                
                # Get funding rounds if deep scan
                if deep_scan:
                    funding_docs = await self._scan_crunchbase_funding(company, client, headers)
                    documents.extend(funding_docs)
                
        except Exception as e:
            logger.error(f"Crunchbase scan failed: {e}")
        
        return documents
    
    async def scan_linkedin(self, company: str, deep_scan: bool = False) -> List[Dict[str, Any]]:
        """
        Scan LinkedIn for company posts and updates
        """
        documents = []
        
        try:
            # Note: LinkedIn API access is restricted
            # This is a placeholder for when proper API access is available
            
            # Alternative: Use web scraping (be mindful of ToS)
            async with httpx.AsyncClient() as client:
                search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company}"
                
                # Add proper headers to mimic browser
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = await client.get(search_url, headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract company information (simplified)
                    documents.append({
                        "source": "linkedin",
                        "type": "company_search",
                        "company": company,
                        "content": f"LinkedIn search results for {company}",
                        "url": search_url,
                        "timestamp": datetime.utcnow(),
                        "raw_data": {"html_length": len(response.text)}
                    })
                
        except Exception as e:
            logger.error(f"LinkedIn scan failed: {e}")
        
        return documents
    
    async def scan_news(self, company: str, deep_scan: bool = False) -> List[Dict[str, Any]]:
        """
        Scan news sources for company mentions
        """
        documents = []
        
        try:
            async with httpx.AsyncClient() as client:
                # NewsAPI search
                news_url = "https://newsapi.org/v2/everything"
                params = {
                    "q": f'"{company}"',
                    "apiKey": self.newsapi_key,
                    "sortBy": "publishedAt",
                    "pageSize": 20 if deep_scan else 10,
                    "language": "en"
                }
                
                response = await client.get(news_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for article in data.get("articles", []):
                        documents.append({
                            "source": "news",
                            "type": "news_article",
                            "company": company,
                            "content": f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}",
                            "url": article.get("url"),
                            "timestamp": datetime.fromisoformat(article.get("publishedAt", "").replace("Z", "+00:00")),
                            "raw_data": article
                        })
                
        except Exception as e:
            logger.error(f"News scan failed: {e}")
        
        return documents
    
    async def scan_twitter(self, company: str, deep_scan: bool = False) -> List[Dict[str, Any]]:
        """
        Scan Twitter/X for company mentions
        """
        documents = []
        
        try:
            if not hasattr(self, 'twitter_client'):
                logger.warning("Twitter client not available")
                return documents
            
            # Search for tweets mentioning the company
            query = f'"{company}" -is:retweet lang:en'
            max_results = 50 if deep_scan else 20
            
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'public_metrics']
            ).flatten(limit=max_results)
            
            for tweet in tweets:
                documents.append({
                    "source": "twitter",
                    "type": "tweet",
                    "company": company,
                    "content": tweet.text,
                    "url": f"https://twitter.com/i/status/{tweet.id}",
                    "timestamp": tweet.created_at,
                    "raw_data": {
                        "id": tweet.id,
                        "author_id": tweet.author_id,
                        "metrics": tweet.public_metrics
                    }
                })
                
        except Exception as e:
            logger.error(f"Twitter scan failed: {e}")
        
        return documents
    
    def _format_crunchbase_content(self, org_data: Dict[str, Any]) -> str:
        """
        Format Crunchbase organization data into readable content
        """
        properties = org_data.get("properties", {})
        
        content_parts = []
        
        if properties.get("name"):
            content_parts.append(f"Company: {properties['name']}")
        
        if properties.get("short_description"):
            content_parts.append(f"Description: {properties['short_description']}")
        
        if properties.get("categories"):
            categories = [cat.get("value", "") for cat in properties["categories"]]
            content_parts.append(f"Categories: {', '.join(categories)}")
        
        if properties.get("funding_total"):
            funding = properties["funding_total"]
            content_parts.append(f"Total Funding: {funding.get('value_usd', 'N/A')} USD")
        
        return " | ".join(content_parts)
    
    async def _scan_crunchbase_funding(
        self, 
        company: str, 
        client: httpx.AsyncClient, 
        headers: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Scan Crunchbase for funding round information
        """
        documents = []
        
        try:
            # Search for funding rounds
            search_url = "https://api.crunchbase.com/api/v4/searches/funding_rounds"
            
            search_payload = {
                "field_ids": [
                    "identifier",
                    "announced_on",
                    "investment_type",
                    "money_raised",
                    "funded_organization_identifier"
                ],
                "query": [
                    {
                        "type": "predicate",
                        "field_id": "funded_organization_identifier",
                        "operator_id": "contains",
                        "values": [company]
                    }
                ],
                "limit": 10
            }
            
            response = await client.post(search_url, json=search_payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                for funding_round in data.get("entities", []):
                    properties = funding_round.get("properties", {})
                    
                    content = f"Funding Round: {properties.get('investment_type', {}).get('value', 'Unknown')} "
                    content += f"Amount: {properties.get('money_raised', {}).get('value_usd', 'Undisclosed')} USD "
                    content += f"Date: {properties.get('announced_on', 'Unknown')}"
                    
                    documents.append({
                        "source": "crunchbase",
                        "type": "funding_round",
                        "company": company,
                        "content": content,
                        "url": f"https://www.crunchbase.com/funding_round/{funding_round['identifier']['value']}",
                        "timestamp": datetime.utcnow(),
                        "raw_data": funding_round
                    })
                    
        except Exception as e:
            logger.error(f"Crunchbase funding scan failed: {e}")
        
        return documents