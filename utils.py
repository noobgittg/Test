import asyncio
import aiohttp
import aiofiles
from pyrogram import Client
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from config import Config
import logging
from typing import Optional, List, Dict
import re

logger = logging.getLogger(__name__)

async def is_subscribed(bot: Client, message) -> bool:
    """Check if user is subscribed to auth channel"""
    if not Config.AUTH_CHANNEL:
        return True
    
    try:
        user_id = message.from_user.id if hasattr(message, 'from_user') else message.user.id
        await bot.get_chat_member(Config.AUTH_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception as e:
        logger.error(f"Subscription check error: {e}")
        return True  # Allow access if check fails

async def get_poster(query: str, bulk: bool = False, id: bool = False, file=None):
    """Get movie poster from TMDB API"""
    if not query:
        return None
    
    try:
        # This would require TMDB API key - implement based on your needs
        # For now, return None to avoid API dependency
        return None
    except Exception as e:
        logger.error(f"Poster fetch error: {e}")
        return None

def extract_year(title: str) -> tuple:
    """Extract year from movie title"""
    year_pattern = r'\b(19|20)\d{2}\b'
    match = re.search(year_pattern, title)
    
    if match:
        year = match.group()
        clean_title = re.sub(year_pattern, '', title).strip()
        return clean_title, year
    
    return title, None

def clean_filename(filename: str) -> str:
    """Clean filename for better search results"""
    # Remove file extensions
    filename = re.sub(r'\.[a-zA-Z0-9]+$', '', filename)
    
    # Remove quality indicators
    quality_patterns = [
        r'\b(720p|1080p|480p|360p|240p|4K|2K|HD|FHD|UHD)\b',
        r'\b(BluRay|BRRip|DVDRip|WEBRip|HDRip|CAMRip|TS|TC)\b',
        r'\b(x264|x265|H264|H265|HEVC|AVC)\b',
        r'\b(AAC|AC3|DTS|MP3|FLAC)\b',
        r'\[(.*?)\]',  # Remove content in brackets
        r'\((.*?)\)',  # Remove content in parentheses (be careful with years)
    ]
    
    for pattern in quality_patterns:
        filename = re.sub(pattern, ' ', filename, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    filename = re.sub(r'\s+', ' ', filename).strip()
    
    return filename

async def get_search_results(query: str, file_type: str = None, max_results: int = 50) -> List[Dict]:
    """Get search results with caching - wrapper for database function"""
    from database.database import db
    return await db.get_search_results(query, file_type, max_results)

async def get_file_details(file_id: str) -> Optional[Dict]:
    """Get file details - wrapper for database function"""
    from database.database import db
    return await db.get_file_details(file_id)

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    async def acquire(self):
        """Acquire rate limit token"""
        import time
        now = time.time()
        
        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        if len(self.calls) >= self.max_calls:
            sleep_time = self.time_window - (now - self.calls[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.calls.append(now)

# Global rate limiter for external API calls
api_rate_limiter = RateLimiter(max_calls=10, time_window=60)  # 10 calls per minute