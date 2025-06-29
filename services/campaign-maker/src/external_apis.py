import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

from .config import Config

logger = logging.getLogger(__name__)

class PicaClient:
    """
    Client for Pica API - AI-powered image generation and resizing
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None
        self.base_url = config.pica_base_url
        self.api_key = config.pica_api_key
    
    async def initialize(self):
        """Initialize Pica client"""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            logger.info("Pica client initialized successfully")
            
        except Exception as e:
            logger.error(f"Pica client initialization failed: {e}")
            # Continue without Pica if not available
            self.client = None
    
    async def close(self):
        """Close Pica client"""
        try:
            if self.client:
                await self.client.aclose()
            logger.info("Pica client closed")
        except Exception as e:
            logger.error(f"Error closing Pica client: {e}")
    
    async def health_check(self) -> bool:
        """Check Pica API health"""
        try:
            if not self.client:
                return False
            
            response = await self.client.get("/health")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Pica health check failed: {e}")
            return False
    
    async def generate_social_image(
        self,
        headline: str,
        company_a: str,
        company_b: str,
        style: str = "modern_partnership",
        dimensions: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Generate social media image for partnership announcement
        """
        try:
            if not self.client:
                return self._generate_placeholder_image(dimensions or {"width": 1200, "height": 630})
            
            request_data = {
                "prompt": f"Professional partnership announcement between {company_a} and {company_b}. {headline}",
                "style": style,
                "dimensions": dimensions or {"width": 1200, "height": 630},
                "elements": {
                    "headline": headline,
                    "company_logos": [company_a, company_b],
                    "theme": "partnership_collaboration",
                    "color_scheme": "professional_blue_purple"
                }
            }
            
            response = await self.client.post("/generate/social", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "url": result.get("image_url"),
                    "dimensions": dimensions or {"width": 1200, "height": 630},
                    "format": "png",
                    "style": style,
                    "generation_id": result.get("id")
                }
            else:
                logger.warning(f"Pica social image generation failed: {response.status_code}")
                return self._generate_placeholder_image(dimensions or {"width": 1200, "height": 630})
                
        except Exception as e:
            logger.error(f"Social image generation failed: {e}")
            return self._generate_placeholder_image(dimensions or {"width": 1200, "height": 630})
    
    async def generate_email_header(
        self,
        company_a: str,
        company_b: str,
        theme: str = "partnership_announcement",
        dimensions: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Generate email header image
        """
        try:
            if not self.client:
                return self._generate_placeholder_image(dimensions or {"width": 600, "height": 200})
            
            request_data = {
                "prompt": f"Email header for partnership between {company_a} and {company_b}",
                "theme": theme,
                "dimensions": dimensions or {"width": 600, "height": 200},
                "elements": {
                    "companies": [company_a, company_b],
                    "style": "email_header",
                    "branding": "professional"
                }
            }
            
            response = await self.client.post("/generate/email-header", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "url": result.get("image_url"),
                    "dimensions": dimensions or {"width": 600, "height": 200},
                    "format": "png",
                    "theme": theme
                }
            else:
                return self._generate_placeholder_image(dimensions or {"width": 600, "height": 200})
                
        except Exception as e:
            logger.error(f"Email header generation failed: {e}")
            return self._generate_placeholder_image(dimensions or {"width": 600, "height": 200})
    
    async def resize_image(
        self,
        image_url: str,
        target_dimensions: List[Dict[str, int]],
        optimization: str = "web"
    ) -> List[Dict[str, Any]]:
        """
        Resize image to multiple dimensions
        """
        try:
            if not self.client:
                return [self._generate_placeholder_image(dim) for dim in target_dimensions]
            
            request_data = {
                "source_url": image_url,
                "target_dimensions": target_dimensions,
                "optimization": optimization,
                "format": "png",
                "quality": 90
            }
            
            response = await self.client.post("/resize", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("resized_images", [])
            else:
                return [self._generate_placeholder_image(dim) for dim in target_dimensions]
                
        except Exception as e:
            logger.error(f"Image resizing failed: {e}")
            return [self._generate_placeholder_image(dim) for dim in target_dimensions]
    
    async def generate_image(
        self,
        brief: Dict[str, Any],
        dimensions: Dict[str, int],
        style: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate image from content brief
        """
        try:
            if not self.client:
                return self._generate_placeholder_image(dimensions)
            
            request_data = {
                "prompt": brief.get("description", "Professional business image"),
                "style": style,
                "dimensions": dimensions,
                "elements": brief.get("elements", {})
            }
            
            response = await self.client.post("/generate", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "type": "image",
                    "url": result.get("image_url"),
                    "dimensions": dimensions,
                    "format": "png",
                    "style": style
                }
            else:
                return self._generate_placeholder_image(dimensions)
                
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return self._generate_placeholder_image(dimensions)
    
    def _generate_placeholder_image(self, dimensions: Dict[str, int]) -> Dict[str, Any]:
        """
        Generate placeholder image when Pica is unavailable
        """
        try:
            width = dimensions.get("width", 600)
            height = dimensions.get("height", 400)
            
            # Create simple placeholder image
            img = Image.new('RGB', (width, height), color='#f0f0f0')
            
            # Convert to base64 data URL
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "url": f"data:image/png;base64,{img_data}",
                "dimensions": dimensions,
                "format": "png",
                "placeholder": True
            }
            
        except Exception as e:
            logger.error(f"Placeholder image generation failed: {e}")
            return {
                "url": "https://via.placeholder.com/600x400/f0f0f0/333333?text=Image+Placeholder",
                "dimensions": dimensions,
                "format": "png",
                "placeholder": True
            }

class TavusClient:
    """
    Client for Tavus API - Personalized video generation
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None
        self.base_url = config.tavus_base_url
        self.api_key = config.tavus_api_key
    
    async def initialize(self):
        """Initialize Tavus client"""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0  # Video generation takes longer
            )
            
            logger.info("Tavus client initialized successfully")
            
        except Exception as e:
            logger.error(f"Tavus client initialization failed: {e}")
            self.client = None
    
    async def close(self):
        """Close Tavus client"""
        try:
            if self.client:
                await self.client.aclose()
            logger.info("Tavus client closed")
        except Exception as e:
            logger.error(f"Error closing Tavus client: {e}")
    
    async def health_check(self) -> bool:
        """Check Tavus API health"""
        try:
            if not self.client:
                return False
            
            response = await self.client.get("/health")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Tavus health check failed: {e}")
            return False
    
    async def create_video_placeholder(
        self,
        script: str,
        company_a: str = None,
        company_b: str = None,
        style: str = "professional_announcement"
    ) -> Dict[str, Any]:
        """
        Create personalized video placeholder for partnership announcement
        """
        try:
            if not self.client:
                return self._generate_video_placeholder(script)
            
            request_data = {
                "script": script,
                "style": style,
                "personalization": {
                    "company_a": company_a,
                    "company_b": company_b,
                    "tone": "professional",
                    "duration": "60-90 seconds"
                },
                "template": "partnership_announcement",
                "voice": "professional_male",
                "background": "corporate_office"
            }
            
            response = await self.client.post("/videos/create-placeholder", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "placeholder_url": result.get("placeholder_url"),
                    "video_id": result.get("video_id"),
                    "script": script,
                    "duration_estimate": result.get("duration_estimate", "60-90 seconds"),
                    "personalization_variables": result.get("variables", []),
                    "status": "placeholder_created"
                }
            else:
                logger.warning(f"Tavus video placeholder creation failed: {response.status_code}")
                return self._generate_video_placeholder(script)
                
        except Exception as e:
            logger.error(f"Video placeholder creation failed: {e}")
            return self._generate_video_placeholder(script)
    
    async def generate_personalized_video(
        self,
        template_id: str,
        personalization_data: Dict[str, Any],
        recipient_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate personalized video for specific recipient
        """
        try:
            if not self.client:
                return {"error": "Tavus client not available"}
            
            request_data = {
                "template_id": template_id,
                "personalization": personalization_data,
                "recipient": recipient_info,
                "delivery_method": "url",
                "quality": "hd"
            }
            
            response = await self.client.post("/videos/generate", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "video_url": result.get("video_url"),
                    "video_id": result.get("video_id"),
                    "status": result.get("status"),
                    "duration": result.get("duration"),
                    "thumbnail_url": result.get("thumbnail_url"),
                    "expires_at": result.get("expires_at")
                }
            else:
                return {"error": f"Video generation failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Personalized video generation failed: {e}")
            return {"error": str(e)}
    
    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get video generation status
        """
        try:
            if not self.client:
                return {"status": "unavailable"}
            
            response = await self.client.get(f"/videos/{video_id}/status")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": "Failed to get status"}
                
        except Exception as e:
            logger.error(f"Video status check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_video_placeholder(self, script: str) -> Dict[str, Any]:
        """
        Generate video placeholder when Tavus is unavailable
        """
        return {
            "placeholder_url": "https://via.placeholder.com/640x360/000000/ffffff?text=Video+Placeholder",
            "video_id": f"placeholder_{int(datetime.utcnow().timestamp())}",
            "script": script,
            "duration_estimate": "60-90 seconds",
            "personalization_variables": ["company_name", "recipient_name", "partnership_details"],
            "status": "placeholder_only",
            "note": "Tavus integration required for actual video generation"
        }

class LingoClient:
    """
    Client for Lingo API - Internationalization and localization
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None
        self.base_url = config.lingo_base_url
        self.api_key = config.lingo_api_key
    
    async def initialize(self):
        """Initialize Lingo client"""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            logger.info("Lingo client initialized successfully")
            
        except Exception as e:
            logger.error(f"Lingo client initialization failed: {e}")
            self.client = None
    
    async def close(self):
        """Close Lingo client"""
        try:
            if self.client:
                await self.client.aclose()
            logger.info("Lingo client closed")
        except Exception as e:
            logger.error(f"Error closing Lingo client: {e}")
    
    async def health_check(self) -> bool:
        """Check Lingo API health"""
        try:
            if not self.client:
                return False
            
            response = await self.client.get("/health")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Lingo health check failed: {e}")
            return False
    
    async def localize_content(
        self,
        copy_variants: List[Dict[str, Any]],
        target_languages: List[str],
        cultural_adaptations: bool = True
    ) -> Dict[str, Any]:
        """
        Localize copy variants for different languages and cultures
        """
        try:
            if not self.client:
                return self._generate_mock_localizations(copy_variants, target_languages)
            
            localization_requests = []
            
            for variant in copy_variants:
                for language in target_languages:
                    localization_requests.append({
                        "variant_id": variant.get("variant_id"),
                        "source_language": "en",
                        "target_language": language,
                        "content": {
                            "headline": variant.get("headline", ""),
                            "body_text": variant.get("body_text", ""),
                            "cta": variant.get("cta", "")
                        },
                        "context": {
                            "industry": "technology",
                            "tone": variant.get("big_five_target", "professional"),
                            "cultural_adaptation": cultural_adaptations
                        }
                    })
            
            request_data = {
                "requests": localization_requests,
                "options": {
                    "preserve_formatting": True,
                    "maintain_tone": True,
                    "cultural_adaptation": cultural_adaptations,
                    "quality_level": "professional"
                }
            }
            
            response = await self.client.post("/localize/batch", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                return self._organize_localizations(result.get("localizations", []))
            else:
                logger.warning(f"Lingo localization failed: {response.status_code}")
                return self._generate_mock_localizations(copy_variants, target_languages)
                
        except Exception as e:
            logger.error(f"Content localization failed: {e}")
            return self._generate_mock_localizations(copy_variants, target_languages)
    
    async def translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Translate individual text with context
        """
        try:
            if not self.client:
                return {"translated_text": f"[{target_language.upper()}] {text}", "confidence": 0.5}
            
            request_data = {
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
                "context": context or {},
                "options": {
                    "preserve_tone": True,
                    "business_context": True
                }
            }
            
            response = await self.client.post("/translate", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "translated_text": result.get("translated_text"),
                    "confidence": result.get("confidence", 0.8),
                    "alternatives": result.get("alternatives", []),
                    "cultural_notes": result.get("cultural_notes", [])
                }
            else:
                return {"translated_text": f"[{target_language.upper()}] {text}", "confidence": 0.5}
                
        except Exception as e:
            logger.error(f"Text translation failed: {e}")
            return {"translated_text": f"[{target_language.upper()}] {text}", "confidence": 0.5}
    
    async def get_cultural_insights(
        self,
        target_language: str,
        content_type: str = "business"
    ) -> Dict[str, Any]:
        """
        Get cultural insights for localization
        """
        try:
            if not self.client:
                return self._get_mock_cultural_insights(target_language)
            
            response = await self.client.get(f"/cultural-insights/{target_language}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._get_mock_cultural_insights(target_language)
                
        except Exception as e:
            logger.error(f"Cultural insights failed: {e}")
            return self._get_mock_cultural_insights(target_language)
    
    def _organize_localizations(self, localizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Organize localizations by language and variant
        """
        organized = {}
        
        for loc in localizations:
            language = loc.get("target_language")
            variant_id = loc.get("variant_id")
            
            if language not in organized:
                organized[language] = {}
            
            organized[language][variant_id] = {
                "headline": loc.get("content", {}).get("headline"),
                "body_text": loc.get("content", {}).get("body_text"),
                "cta": loc.get("content", {}).get("cta"),
                "confidence": loc.get("confidence", 0.8),
                "cultural_notes": loc.get("cultural_notes", [])
            }
        
        return organized
    
    def _generate_mock_localizations(
        self,
        copy_variants: List[Dict[str, Any]],
        target_languages: List[str]
    ) -> Dict[str, Any]:
        """
        Generate mock localizations when Lingo is unavailable
        """
        mock_localizations = {}
        
        language_prefixes = {
            "es": "[ES]",
            "fr": "[FR]",
            "de": "[DE]",
            "it": "[IT]",
            "pt": "[PT]",
            "ja": "[JA]",
            "ko": "[KO]",
            "zh": "[ZH]"
        }
        
        for language in target_languages:
            prefix = language_prefixes.get(language, f"[{language.upper()}]")
            mock_localizations[language] = {}
            
            for variant in copy_variants:
                variant_id = variant.get("variant_id", "unknown")
                mock_localizations[language][variant_id] = {
                    "headline": f"{prefix} {variant.get('headline', '')}",
                    "body_text": f"{prefix} {variant.get('body_text', '')}",
                    "cta": f"{prefix} {variant.get('cta', '')}",
                    "confidence": 0.5,
                    "cultural_notes": [f"Mock localization for {language}"]
                }
        
        return mock_localizations
    
    def _get_mock_cultural_insights(self, target_language: str) -> Dict[str, Any]:
        """
        Get mock cultural insights
        """
        mock_insights = {
            "es": {
                "communication_style": "Warm and personal",
                "business_etiquette": "Relationship-focused",
                "color_preferences": ["red", "yellow", "orange"],
                "avoid": ["overly direct language"]
            },
            "fr": {
                "communication_style": "Formal and elegant",
                "business_etiquette": "Protocol-conscious",
                "color_preferences": ["blue", "white", "red"],
                "avoid": ["casual tone in business context"]
            },
            "de": {
                "communication_style": "Direct and precise",
                "business_etiquette": "Efficiency-focused",
                "color_preferences": ["blue", "gray", "black"],
                "avoid": ["excessive enthusiasm"]
            },
            "ja": {
                "communication_style": "Respectful and indirect",
                "business_etiquette": "Hierarchy-conscious",
                "color_preferences": ["blue", "white", "red"],
                "avoid": ["aggressive sales language"]
            }
        }
        
        return mock_insights.get(target_language, {
            "communication_style": "Professional",
            "business_etiquette": "Standard business practices",
            "color_preferences": ["blue", "gray"],
            "avoid": ["cultural assumptions"]
        })