#!/usr/bin/env python3
"""
Synapse LaunchPad Database Seed Script

Generates realistic mock data for:
- 50 diverse startups with founder personalities
- 200 historical partnership outcomes
- 5k synthetic user engagement events

Uses Faker + mimesis for realistic data generation
"""

import asyncio
import asyncpg
import httpx
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from faker import Faker
from mimesis import Person, Address, Finance, Text, Development, Internet
from mimesis.locales import Locale
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize data generators
fake = Faker()
person = Person(Locale.EN)
address = Address(Locale.EN)
finance = Finance(Locale.EN)
text = Text(Locale.EN)
development = Development()
internet = Internet()

class DataSeeder:
    """Main data seeding class"""
    
    def __init__(self):
        self.db_pool = None
        self.feature_store_client = None
        
        # Industry verticals with characteristics
        self.industries = {
            "FinTech": {
                "keywords": ["payments", "banking", "crypto", "lending", "insurance"],
                "avg_funding": 5000000,
                "growth_rate_range": (15, 45),
                "technologies": ["blockchain", "AI", "mobile", "API", "security"]
            },
            "HealthTech": {
                "keywords": ["medical", "healthcare", "telemedicine", "diagnostics", "wellness"],
                "avg_funding": 8000000,
                "growth_rate_range": (20, 60),
                "technologies": ["AI", "IoT", "mobile", "cloud", "data analytics"]
            },
            "EdTech": {
                "keywords": ["education", "learning", "training", "skills", "online"],
                "avg_funding": 3000000,
                "growth_rate_range": (25, 70),
                "technologies": ["AI", "VR", "mobile", "cloud", "analytics"]
            },
            "E-commerce": {
                "keywords": ["retail", "marketplace", "shopping", "commerce", "delivery"],
                "avg_funding": 4000000,
                "growth_rate_range": (30, 80),
                "technologies": ["mobile", "AI", "logistics", "payments", "analytics"]
            },
            "SaaS": {
                "keywords": ["software", "platform", "automation", "productivity", "enterprise"],
                "avg_funding": 6000000,
                "growth_rate_range": (20, 50),
                "technologies": ["cloud", "API", "AI", "automation", "security"]
            },
            "AI/ML": {
                "keywords": ["artificial intelligence", "machine learning", "automation", "data"],
                "avg_funding": 7000000,
                "growth_rate_range": (35, 90),
                "technologies": ["AI", "ML", "deep learning", "NLP", "computer vision"]
            },
            "Sustainability": {
                "keywords": ["green", "renewable", "carbon", "environment", "clean"],
                "avg_funding": 5500000,
                "growth_rate_range": (25, 65),
                "technologies": ["IoT", "AI", "clean tech", "sensors", "analytics"]
            },
            "Logistics": {
                "keywords": ["supply chain", "delivery", "transportation", "warehousing"],
                "avg_funding": 4500000,
                "growth_rate_range": (20, 55),
                "technologies": ["IoT", "AI", "automation", "mobile", "tracking"]
            },
            "Cybersecurity": {
                "keywords": ["security", "privacy", "protection", "threat", "compliance"],
                "avg_funding": 6500000,
                "growth_rate_range": (30, 70),
                "technologies": ["AI", "blockchain", "encryption", "cloud", "analytics"]
            },
            "PropTech": {
                "keywords": ["real estate", "property", "construction", "smart buildings"],
                "avg_funding": 4200000,
                "growth_rate_range": (15, 40),
                "technologies": ["IoT", "AI", "mobile", "VR", "analytics"]
            }
        }
        
        # Funding stages with characteristics
        self.funding_stages = {
            "pre-seed": {"min_funding": 50000, "max_funding": 500000, "employee_range": (2, 8)},
            "seed": {"min_funding": 500000, "max_funding": 3000000, "employee_range": (5, 25)},
            "series-a": {"min_funding": 3000000, "max_funding": 15000000, "employee_range": (20, 75)},
            "series-b": {"min_funding": 15000000, "max_funding": 50000000, "employee_range": (50, 200)},
            "series-c": {"min_funding": 50000000, "max_funding": 200000000, "employee_range": (100, 500)},
            "growth": {"min_funding": 100000000, "max_funding": 1000000000, "employee_range": (200, 2000)}
        }
        
        # Big Five personality traits for founders
        self.personality_archetypes = {
            "visionary": {"openness": 0.9, "conscientiousness": 0.7, "extraversion": 0.8, "agreeableness": 0.6, "neuroticism": 0.3},
            "executor": {"openness": 0.6, "conscientiousness": 0.9, "extraversion": 0.7, "agreeableness": 0.7, "neuroticism": 0.2},
            "networker": {"openness": 0.7, "conscientiousness": 0.6, "extraversion": 0.9, "agreeableness": 0.8, "neuroticism": 0.3},
            "innovator": {"openness": 0.95, "conscientiousness": 0.5, "extraversion": 0.6, "agreeableness": 0.5, "neuroticism": 0.4},
            "builder": {"openness": 0.8, "conscientiousness": 0.8, "extraversion": 0.5, "agreeableness": 0.6, "neuroticism": 0.2},
            "strategist": {"openness": 0.8, "conscientiousness": 0.8, "extraversion": 0.6, "agreeableness": 0.5, "neuroticism": 0.3}
        }
        
        # Campaign channels and their characteristics
        self.campaign_channels = {
            "email": {"base_open_rate": 0.22, "base_click_rate": 0.035, "base_conversion": 0.018},
            "social": {"base_open_rate": 0.08, "base_click_rate": 0.012, "base_conversion": 0.008},
            "influencer": {"base_open_rate": 0.15, "base_click_rate": 0.025, "base_conversion": 0.015},
            "video": {"base_open_rate": 0.35, "base_click_rate": 0.045, "base_conversion": 0.025},
            "content": {"base_open_rate": 0.18, "base_click_rate": 0.028, "base_conversion": 0.012}
        }
    
    async def initialize(self):
        """Initialize database and API connections"""
        try:
            # Connect to PostgreSQL
            self.db_pool = await asyncpg.create_pool(
                "postgresql://postgres:password@localhost:5432/synapse_db",
                min_size=5,
                max_size=20
            )
            
            # Initialize feature store client
            self.feature_store_client = httpx.AsyncClient(
                base_url="http://localhost:8000",
                timeout=30.0
            )
            
            logger.info("Database and API connections initialized")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
    
    async def close(self):
        """Close connections"""
        try:
            if self.db_pool:
                await self.db_pool.close()
            if self.feature_store_client:
                await self.feature_store_client.aclose()
            logger.info("Connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")
    
    def generate_startup_data(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate realistic startup data"""
        startups = []
        
        for i in range(count):
            # Select industry and stage
            industry = random.choice(list(self.industries.keys()))
            industry_data = self.industries[industry]
            stage = random.choice(list(self.funding_stages.keys()))
            stage_data = self.funding_stages[stage]
            
            # Generate company name
            company_name = self._generate_company_name(industry)
            
            # Generate funding amount within stage range
            funding_amount = random.randint(stage_data["min_funding"], stage_data["max_funding"])
            
            # Generate employee count
            min_emp, max_emp = stage_data["employee_range"]
            employee_count = random.randint(min_emp, max_emp)
            
            # Generate growth rate with industry influence
            min_growth, max_growth = industry_data["growth_rate_range"]
            growth_rate = random.uniform(min_growth, max_growth)
            
            # Generate technologies
            tech_count = random.randint(2, 5)
            technologies = random.sample(industry_data["technologies"], min(tech_count, len(industry_data["technologies"])))
            
            # Generate target markets
            target_markets = self._generate_target_markets(industry)
            
            # Generate business model
            business_model = self._generate_business_model(industry)
            
            # Generate location
            location = f"{address.city()}, {address.state()}"
            
            # Generate founded date
            years_ago = random.randint(1, 8)
            founded = fake.date_between(start_date=f'-{years_ago}y', end_date='today')
            
            # Generate description
            description = self._generate_company_description(company_name, industry, industry_data["keywords"])
            
            # Generate founder personality
            personality_type = random.choice(list(self.personality_archetypes.keys()))
            founder_traits = self.personality_archetypes[personality_type].copy()
            
            # Add some noise to personality traits
            for trait in founder_traits:
                noise = random.uniform(-0.1, 0.1)
                founder_traits[trait] = max(0.0, min(1.0, founder_traits[trait] + noise))
            
            # Generate culture vector based on personality and industry
            culture_vector = self._generate_culture_vector(founder_traits, industry)
            
            startup = {
                "id": str(uuid.uuid4()),
                "name": company_name,
                "industry": industry,
                "stage": stage,
                "funding_amount": funding_amount,
                "employee_count": employee_count,
                "technologies": technologies,
                "target_market": target_markets,
                "business_model": business_model,
                "growth_rate": round(growth_rate, 2),
                "location": location,
                "founded": founded,
                "description": description,
                "founder_personality": personality_type,
                "founder_traits": founder_traits,
                "culture_vector": culture_vector,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            startups.append(startup)
        
        logger.info(f"Generated {len(startups)} startup records")
        return startups
    
    def generate_partnership_data(self, startups: List[Dict[str, Any]], count: int = 200) -> List[Dict[str, Any]]:
        """Generate historical partnership outcomes"""
        partnerships = []
        
        for i in range(count):
            # Select two different companies
            company_a, company_b = random.sample(startups, 2)
            
            # Calculate compatibility factors
            compatibility = self._calculate_partnership_compatibility(company_a, company_b)
            
            # Determine outcome based on compatibility
            success_probability = (
                compatibility["industry_synergy"] * 0.3 +
                compatibility["stage_alignment"] * 0.2 +
                compatibility["culture_fit"] * 0.25 +
                compatibility["market_overlap"] * 0.15 +
                compatibility["size_compatibility"] * 0.1
            )
            
            # Add some randomness
            success_probability += random.uniform(-0.2, 0.2)
            success_probability = max(0.0, min(1.0, success_probability))
            
            # Determine status
            if success_probability > 0.7:
                status = "active"
                outcome = 1
            elif success_probability > 0.4:
                status = random.choice(["completed", "active"])
                outcome = 1 if status == "active" else random.choice([0, 1])
            else:
                status = random.choice(["cancelled", "failed"])
                outcome = 0
            
            # Generate partnership duration
            start_date = fake.date_between(start_date='-2y', end_date='-1m')
            
            if status in ["active", "completed"]:
                duration_days = random.randint(30, 730)  # 1 month to 2 years
            else:
                duration_days = random.randint(7, 180)   # 1 week to 6 months
            
            # Generate metrics based on outcome
            if outcome == 1:
                revenue_impact = random.uniform(0.05, 0.45)  # 5-45% revenue increase
                user_growth = random.uniform(0.1, 0.8)       # 10-80% user growth
                market_expansion = random.uniform(0.05, 0.3) # 5-30% market expansion
            else:
                revenue_impact = random.uniform(-0.1, 0.1)   # -10% to 10%
                user_growth = random.uniform(-0.05, 0.2)     # -5% to 20%
                market_expansion = random.uniform(0, 0.05)   # 0-5%
            
            partnership = {
                "id": str(uuid.uuid4()),
                "company_a": company_a["id"],
                "company_b": company_b["id"],
                "status": status,
                "match_score": round(success_probability * 100, 2),
                "outcome": outcome,
                "start_date": start_date,
                "duration_days": duration_days,
                "compatibility_factors": compatibility,
                "metrics": {
                    "revenue_impact": round(revenue_impact, 3),
                    "user_growth": round(user_growth, 3),
                    "market_expansion": round(market_expansion, 3)
                },
                "created_at": start_date,
                "updated_at": datetime.utcnow()
            }
            
            partnerships.append(partnership)
        
        logger.info(f"Generated {len(partnerships)} partnership records")
        return partnerships
    
    def generate_engagement_events(self, startups: List[Dict[str, Any]], count: int = 5000) -> List[Dict[str, Any]]:
        """Generate synthetic user engagement events for marketing campaigns"""
        events = []
        
        # Create some campaigns first
        campaigns = self._generate_campaigns(startups, 25)
        
        for i in range(count):
            campaign = random.choice(campaigns)
            channel = random.choice(campaign["channels"])
            
            # Generate user profile
            user_profile = self._generate_user_profile()
            
            # Generate event type based on funnel
            event_type = self._generate_event_type(channel)
            
            # Generate timestamp within campaign period
            campaign_start = campaign["created_at"]
            campaign_end = campaign_start + timedelta(days=30)
            event_timestamp = fake.date_time_between(start_date=campaign_start, end_date=campaign_end)
            
            # Generate event data based on type and channel
            event_data = self._generate_event_data(event_type, channel, user_profile, campaign)
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(event_type, event_data, user_profile)
            
            event = {
                "id": str(uuid.uuid4()),
                "campaign_id": campaign["id"],
                "user_id": user_profile["id"],
                "session_id": str(uuid.uuid4()),
                "event_type": event_type,
                "channel": channel,
                "event_data": event_data,
                "user_profile": user_profile,
                "engagement_score": engagement_score,
                "timestamp": event_timestamp,
                "created_at": datetime.utcnow()
            }
            
            events.append(event)
        
        logger.info(f"Generated {len(events)} engagement events")
        return events, campaigns
    
    def _generate_company_name(self, industry: str) -> str:
        """Generate realistic company name based on industry"""
        prefixes = {
            "FinTech": ["Pay", "Fin", "Crypto", "Bank", "Invest", "Credit", "Money"],
            "HealthTech": ["Health", "Med", "Care", "Bio", "Vital", "Cure", "Wellness"],
            "EdTech": ["Learn", "Edu", "Skill", "Brain", "Study", "Teach", "Know"],
            "E-commerce": ["Shop", "Buy", "Market", "Trade", "Sell", "Cart", "Store"],
            "SaaS": ["Cloud", "Soft", "Auto", "Pro", "Smart", "Tech", "Digital"],
            "AI/ML": ["AI", "Neural", "Mind", "Brain", "Intel", "Cognitive", "Smart"],
            "Sustainability": ["Green", "Eco", "Clean", "Sustain", "Carbon", "Renew"],
            "Logistics": ["Ship", "Move", "Flow", "Chain", "Track", "Deliver"],
            "Cybersecurity": ["Secure", "Guard", "Shield", "Protect", "Safe", "Cyber"],
            "PropTech": ["Build", "Space", "Property", "Real", "Home", "Estate"]
        }
        
        suffixes = ["ly", "io", "ai", "tech", "labs", "works", "hub", "flow", "wise", "pro", "co", "inc"]
        
        prefix = random.choice(prefixes.get(industry, ["Tech", "Digital", "Smart"]))
        suffix = random.choice(suffixes)
        
        # Sometimes add a descriptive word
        if random.random() < 0.3:
            descriptors = ["Flow", "Hub", "Labs", "Works", "Pro", "Plus", "Max", "Core", "Base", "Link"]
            return f"{prefix}{random.choice(descriptors)}"
        
        return f"{prefix}{suffix.title()}"
    
    def _generate_target_markets(self, industry: str) -> List[str]:
        """Generate target markets based on industry"""
        market_options = {
            "FinTech": ["SMB", "Enterprise", "Consumer", "Banks", "Credit Unions"],
            "HealthTech": ["Hospitals", "Clinics", "Patients", "Insurance", "Pharma"],
            "EdTech": ["K-12", "Higher Ed", "Corporate", "Individual Learners"],
            "E-commerce": ["B2C", "B2B", "Marketplace", "Retail", "Wholesale"],
            "SaaS": ["SMB", "Enterprise", "Startups", "Agencies", "Freelancers"],
            "AI/ML": ["Enterprise", "Developers", "Data Scientists", "Researchers"],
            "Sustainability": ["Enterprise", "Government", "Consumers", "NGOs"],
            "Logistics": ["E-commerce", "Retail", "Manufacturing", "3PL"],
            "Cybersecurity": ["Enterprise", "SMB", "Government", "Healthcare"],
            "PropTech": ["Real Estate", "Property Managers", "Investors", "Tenants"]
        }
        
        options = market_options.get(industry, ["SMB", "Enterprise", "Consumer"])
        return random.sample(options, random.randint(1, min(3, len(options))))
    
    def _generate_business_model(self, industry: str) -> str:
        """Generate business model based on industry"""
        models = {
            "FinTech": ["SaaS", "Transaction fees", "Subscription", "Commission"],
            "HealthTech": ["SaaS", "Per-patient", "Subscription", "Licensing"],
            "EdTech": ["Subscription", "Per-seat", "Freemium", "Marketplace"],
            "E-commerce": ["Marketplace", "Commission", "Subscription", "Transaction fees"],
            "SaaS": ["Subscription", "Per-seat", "Usage-based", "Freemium"],
            "AI/ML": ["API calls", "Subscription", "Licensing", "Custom"],
            "Sustainability": ["SaaS", "Consulting", "Hardware + Software", "Credits"],
            "Logistics": ["Per-shipment", "Subscription", "Commission", "SaaS"],
            "Cybersecurity": ["Subscription", "Per-device", "Enterprise license"],
            "PropTech": ["Commission", "SaaS", "Transaction fees", "Subscription"]
        }
        
        return random.choice(models.get(industry, ["SaaS", "Subscription", "Commission"]))
    
    def _generate_company_description(self, name: str, industry: str, keywords: List[str]) -> str:
        """Generate realistic company description"""
        templates = [
            f"{name} is revolutionizing {industry.lower()} through innovative {random.choice(keywords)} solutions that help businesses scale efficiently.",
            f"At {name}, we're building the future of {random.choice(keywords)} with cutting-edge technology and user-centric design.",
            f"{name} provides enterprise-grade {random.choice(keywords)} platform that enables companies to streamline operations and drive growth.",
            f"Founded to transform {industry.lower()}, {name} delivers powerful {random.choice(keywords)} tools for modern businesses.",
            f"{name} is the leading {random.choice(keywords)} platform helping organizations optimize their {industry.lower()} operations."
        ]
        
        return random.choice(templates)
    
    def _generate_culture_vector(self, founder_traits: Dict[str, float], industry: str) -> List[float]:
        """Generate 128-dimensional culture vector based on founder personality and industry"""
        vector = []
        
        # Base vector from founder personality (first 40 dimensions)
        for trait, value in founder_traits.items():
            for i in range(8):  # 8 dimensions per trait
                noise = random.uniform(-0.1, 0.1)
                vector.append(max(0.0, min(1.0, value + noise)))
        
        # Industry-specific cultural factors (next 40 dimensions)
        industry_factors = {
            "FinTech": [0.8, 0.9, 0.7, 0.8, 0.6, 0.7, 0.9, 0.8],  # Trust, security, innovation
            "HealthTech": [0.9, 0.8, 0.9, 0.7, 0.8, 0.9, 0.7, 0.8],  # Care, precision, ethics
            "EdTech": [0.8, 0.7, 0.9, 0.8, 0.9, 0.7, 0.8, 0.7],  # Learning, growth, accessibility
            "AI/ML": [0.9, 0.8, 0.9, 0.7, 0.8, 0.8, 0.9, 0.8],  # Innovation, research, ethics
            "Sustainability": [0.9, 0.8, 0.8, 0.9, 0.7, 0.8, 0.7, 0.9]  # Purpose, environment
        }
        
        base_factors = industry_factors.get(industry, [0.7] * 8)
        for factor in base_factors:
            for i in range(5):  # 5 dimensions per factor
                noise = random.uniform(-0.15, 0.15)
                vector.append(max(0.0, min(1.0, factor + noise)))
        
        # Random cultural dimensions (remaining 48 dimensions)
        for i in range(48):
            vector.append(random.uniform(0.0, 1.0))
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = (np.array(vector) / norm).tolist()
        
        return vector
    
    def _calculate_partnership_compatibility(self, company_a: Dict[str, Any], company_b: Dict[str, Any]) -> Dict[str, float]:
        """Calculate compatibility factors between two companies"""
        
        # Industry synergy
        if company_a["industry"] == company_b["industry"]:
            industry_synergy = 0.6  # Same industry - moderate synergy
        else:
            # Different industries - check for complementary pairs
            complementary_pairs = [
                ("FinTech", "E-commerce"), ("HealthTech", "AI/ML"), ("EdTech", "AI/ML"),
                ("Logistics", "E-commerce"), ("Cybersecurity", "SaaS"), ("PropTech", "FinTech")
            ]
            pair = (company_a["industry"], company_b["industry"])
            reverse_pair = (company_b["industry"], company_a["industry"])
            
            if pair in complementary_pairs or reverse_pair in complementary_pairs:
                industry_synergy = 0.9  # Complementary industries
            else:
                industry_synergy = 0.3  # Unrelated industries
        
        # Stage alignment
        stage_order = ["pre-seed", "seed", "series-a", "series-b", "series-c", "growth"]
        stage_a_idx = stage_order.index(company_a["stage"])
        stage_b_idx = stage_order.index(company_b["stage"])
        stage_diff = abs(stage_a_idx - stage_b_idx)
        
        if stage_diff == 0:
            stage_alignment = 1.0
        elif stage_diff == 1:
            stage_alignment = 0.8
        elif stage_diff == 2:
            stage_alignment = 0.6
        else:
            stage_alignment = 0.3
        
        # Culture fit (cosine similarity of culture vectors)
        vector_a = np.array(company_a["culture_vector"])
        vector_b = np.array(company_b["culture_vector"])
        
        if np.linalg.norm(vector_a) > 0 and np.linalg.norm(vector_b) > 0:
            culture_fit = np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
            culture_fit = (culture_fit + 1) / 2  # Normalize to 0-1
        else:
            culture_fit = 0.5
        
        # Market overlap
        market_a = set(company_a["target_market"])
        market_b = set(company_b["target_market"])
        overlap = len(market_a.intersection(market_b))
        total_unique = len(market_a.union(market_b))
        
        if total_unique > 0:
            market_overlap = overlap / total_unique
        else:
            market_overlap = 0.0
        
        # Size compatibility
        size_a = company_a["employee_count"]
        size_b = company_b["employee_count"]
        size_ratio = min(size_a, size_b) / max(size_a, size_b, 1)
        size_compatibility = size_ratio * 0.7 + 0.3  # Boost small ratios
        
        return {
            "industry_synergy": round(industry_synergy, 3),
            "stage_alignment": round(stage_alignment, 3),
            "culture_fit": round(culture_fit, 3),
            "market_overlap": round(market_overlap, 3),
            "size_compatibility": round(size_compatibility, 3)
        }
    
    def _generate_campaigns(self, startups: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        """Generate marketing campaigns"""
        campaigns = []
        
        for i in range(count):
            startup = random.choice(startups)
            
            # Generate campaign details
            objectives = ["brand_awareness", "lead_generation", "partnership_announcement", "product_launch", "user_acquisition"]
            objective = random.choice(objectives)
            
            # Select channels based on industry and stage
            all_channels = list(self.campaign_channels.keys())
            channel_count = random.randint(2, 4)
            channels = random.sample(all_channels, channel_count)
            
            # Generate campaign dates
            start_date = fake.date_time_between(start_date='-6m', end_date='-1m')
            
            campaign = {
                "id": str(uuid.uuid4()),
                "company_id": startup["id"],
                "name": f"{startup['name']} {objective.replace('_', ' ').title()} Campaign",
                "objective": objective,
                "channels": channels,
                "target_audience": random.choice(startup["target_market"]),
                "budget": random.randint(5000, 50000),
                "created_at": start_date,
                "status": "completed"
            }
            
            campaigns.append(campaign)
        
        return campaigns
    
    def _generate_user_profile(self) -> Dict[str, Any]:
        """Generate user profile for engagement events"""
        return {
            "id": str(uuid.uuid4()),
            "age": random.randint(25, 55),
            "industry": random.choice(list(self.industries.keys())),
            "role": random.choice(["founder", "ceo", "cto", "vp", "director", "manager"]),
            "company_size": random.choice(["startup", "smb", "enterprise"]),
            "location": f"{address.city()}, {address.country()}",
            "interests": random.sample(["ai", "fintech", "saas", "growth", "partnerships", "innovation"], 3)
        }
    
    def _generate_event_type(self, channel: str) -> str:
        """Generate event type based on channel and funnel stage"""
        event_types = {
            "email": ["email_open", "email_click", "email_reply", "email_forward"],
            "social": ["post_view", "post_like", "post_share", "post_comment", "profile_visit"],
            "influencer": ["content_view", "content_like", "content_share", "profile_visit"],
            "video": ["video_view", "video_complete", "video_share", "cta_click"],
            "content": ["article_view", "article_complete", "article_share", "download"]
        }
        
        return random.choice(event_types.get(channel, ["view", "click", "engagement"]))
    
    def _generate_event_data(self, event_type: str, channel: str, user_profile: Dict[str, Any], campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Generate event-specific data"""
        base_data = {
            "campaign_id": campaign["id"],
            "channel": channel,
            "user_agent": fake.user_agent(),
            "ip_address": fake.ipv4(),
            "referrer": fake.url(),
            "device_type": random.choice(["desktop", "mobile", "tablet"]),
            "browser": random.choice(["chrome", "firefox", "safari", "edge"])
        }
        
        # Add event-specific data
        if "email" in event_type:
            base_data.update({
                "subject_line": f"Partnership Opportunity with {campaign['company_id']}",
                "email_client": random.choice(["gmail", "outlook", "apple_mail"]),
                "time_to_open": random.randint(1, 3600)  # seconds
            })
        
        elif "video" in event_type:
            base_data.update({
                "video_duration": random.randint(30, 300),  # seconds
                "watch_time": random.randint(5, 300),
                "completion_rate": random.uniform(0.1, 1.0)
            })
        
        elif "social" in event_type:
            base_data.update({
                "platform": random.choice(["linkedin", "twitter", "facebook"]),
                "post_type": random.choice(["text", "image", "video", "carousel"]),
                "engagement_time": random.randint(5, 120)  # seconds
            })
        
        return base_data
    
    def _calculate_engagement_score(self, event_type: str, event_data: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Calculate engagement score based on event and user context"""
        base_scores = {
            "email_open": 0.3,
            "email_click": 0.7,
            "email_reply": 0.9,
            "post_view": 0.2,
            "post_like": 0.5,
            "post_share": 0.8,
            "video_view": 0.4,
            "video_complete": 0.9,
            "article_view": 0.3,
            "article_complete": 0.8
        }
        
        base_score = base_scores.get(event_type, 0.5)
        
        # Adjust based on user profile
        if user_profile["role"] in ["founder", "ceo"]:
            base_score *= 1.2  # Higher value users
        
        if user_profile["company_size"] == "enterprise":
            base_score *= 1.1
        
        # Add some randomness
        noise = random.uniform(-0.1, 0.1)
        final_score = max(0.0, min(1.0, base_score + noise))
        
        return round(final_score, 3)
    
    async def seed_database(self):
        """Main seeding function"""
        try:
            logger.info("Starting database seeding...")
            
            # Generate data
            logger.info("Generating startup data...")
            startups = self.generate_startup_data(50)
            
            logger.info("Generating partnership data...")
            partnerships = self.generate_partnership_data(startups, 200)
            
            logger.info("Generating engagement events...")
            events, campaigns = self.generate_engagement_events(startups, 5000)
            
            # Insert into database
            await self._insert_startups(startups)
            await self._insert_partnerships(partnerships)
            await self._insert_campaigns(campaigns)
            await self._insert_events(events)
            
            # Send to feature store
            await self._send_to_feature_store(startups, partnerships, events)
            
            logger.info("Database seeding completed successfully!")
            
        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            raise
    
    async def _insert_startups(self, startups: List[Dict[str, Any]]):
        """Insert startups into database"""
        async with self.db_pool.acquire() as conn:
            # Insert into companies table
            for startup in startups:
                await conn.execute("""
                    INSERT INTO companies (
                        id, name, industry, stage, funding_amount, employee_count,
                        technologies, target_market, business_model, growth_rate,
                        location, founded, description, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    ON CONFLICT (id) DO NOTHING
                """,
                startup["id"], startup["name"], startup["industry"], startup["stage"],
                startup["funding_amount"], startup["employee_count"], startup["technologies"],
                startup["target_market"], startup["business_model"], startup["growth_rate"],
                startup["location"], startup["founded"], startup["description"],
                startup["created_at"], startup["updated_at"]
                )
        
        logger.info(f"Inserted {len(startups)} startups into database")
    
    async def _insert_partnerships(self, partnerships: List[Dict[str, Any]]):
        """Insert partnerships into database"""
        async with self.db_pool.acquire() as conn:
            for partnership in partnerships:
                await conn.execute("""
                    INSERT INTO partnerships (
                        id, company_a, company_b, status, match_score, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (id) DO NOTHING
                """,
                partnership["id"], partnership["company_a"], partnership["company_b"],
                partnership["status"], partnership["match_score"],
                partnership["created_at"], partnership["updated_at"]
                )
        
        logger.info(f"Inserted {len(partnerships)} partnerships into database")
    
    async def _insert_campaigns(self, campaigns: List[Dict[str, Any]]):
        """Insert campaigns into database"""
        async with self.db_pool.acquire() as conn:
            for campaign in campaigns:
                await conn.execute("""
                    INSERT INTO campaigns (
                        id, name, objective, target_audience, channels, status, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (id) DO NOTHING
                """,
                campaign["id"], campaign["name"], campaign["objective"],
                campaign["target_audience"], campaign["channels"], campaign["status"],
                campaign["created_at"], campaign["created_at"]
                )
        
        logger.info(f"Inserted {len(campaigns)} campaigns into database")
    
    async def _insert_events(self, events: List[Dict[str, Any]]):
        """Insert events into analytics_events table"""
        async with self.db_pool.acquire() as conn:
            for event in events:
                await conn.execute("""
                    INSERT INTO analytics_events (
                        id, event_type, event_data, session_id, timestamp
                    ) VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (id) DO NOTHING
                """,
                event["id"], event["event_type"], json.dumps(event["event_data"]),
                event["session_id"], event["timestamp"]
                )
        
        logger.info(f"Inserted {len(events)} events into database")
    
    async def _send_to_feature_store(self, startups: List[Dict[str, Any]], partnerships: List[Dict[str, Any]], events: List[Dict[str, Any]]):
        """Send data to feature store"""
        try:
            # Prepare features for each company
            features = []
            
            for startup in startups:
                # Calculate user overlap score (mock)
                user_overlap_score = random.uniform(0.1, 0.9)
                
                # Get partnership outcomes for this company
                company_partnerships = [p for p in partnerships if p["company_a"] == startup["id"] or p["company_b"] == startup["id"]]
                successful_partnerships = [p for p in company_partnerships if p["outcome"] == 1]
                match_outcome = 1 if len(successful_partnerships) > 0 else 0
                
                # Calculate market sentiment from events (mock)
                company_events = [e for e in events if e.get("event_data", {}).get("campaign_id") in [c["id"] for c in events if c.get("company_id") == startup["id"]]]
                avg_engagement = np.mean([e["engagement_score"] for e in company_events]) if company_events else 0.5
                market_sentiment = (avg_engagement - 0.5) * 2  # Convert to -1 to 1 range
                
                feature = {
                    "company_id": startup["name"],  # Use name as ID for feature store
                    "user_overlap_score": user_overlap_score,
                    "traction_metrics": {
                        "funding_amount": startup["funding_amount"],
                        "employee_count": startup["employee_count"],
                        "growth_rate": startup["growth_rate"],
                        "market_sentiment": market_sentiment,
                        "revenue_growth": random.uniform(0.1, 0.5),
                        "user_growth": random.uniform(0.2, 0.8)
                    },
                    "culture_vector": startup["culture_vector"],
                    "match_outcome": match_outcome,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                features.append(feature)
            
            # Send to feature store
            response = await self.feature_store_client.post("/features/write", json=features)
            
            if response.status_code == 200:
                logger.info(f"Successfully sent {len(features)} features to feature store")
            else:
                logger.warning(f"Feature store write failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send data to feature store: {e}")

async def main():
    """Main execution function"""
    seeder = DataSeeder()
    
    try:
        await seeder.initialize()
        await seeder.seed_database()
        
        print("\n" + "="*60)
        print("🎉 DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("Generated:")
        print("  • 50 diverse startups with founder personalities")
        print("  • 200 historical partnership outcomes")
        print("  • 5,000 synthetic user engagement events")
        print("  • 25 marketing campaigns")
        print("\nData loaded into:")
        print("  • PostgreSQL database")
        print("  • Feature store service")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        await seeder.close()

if __name__ == "__main__":
    asyncio.run(main())