import os
from typing import List

class Config:
    # Bot Configuration
    API_ID = int(os.environ.get("API_ID", ""))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # Database Configuration - 4 DB Support
    DATABASE_URI_1 = os.environ.get("DATABASE_URI_1", "")
    DATABASE_URI_2 = os.environ.get("DATABASE_URI_2", "")
    DATABASE_URI_3 = os.environ.get("DATABASE_URI_3", "")
    DATABASE_URI_4 = os.environ.get("DATABASE_URI_4", "")
    
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "autofilter")
    COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "files")
    
    # Redis Configuration for Caching
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
    
    # Performance Settings
    MAX_RESULTS = int(os.environ.get("MAX_RESULTS", "50"))
    CACHE_TIME = int(os.environ.get("CACHE_TIME", "300"))  # 5 minutes
    MAX_LIST_ELM = int(os.environ.get("MAX_LIST_ELM", "4"))
    
    # Channel/Group Settings
    CHANNELS = [int(ch) if ch.startswith("-") else ch for ch in os.environ.get("CHANNELS", "").split()]
    AUTH_USERS = [int(user) for user in os.environ.get("AUTH_USERS", "").split()]
    AUTH_CHANNEL = int(os.environ.get("AUTH_CHANNEL", "0"))
    
    # IMDB Settings
    IMDB = bool(os.environ.get("IMDB", True))
    SPELL_CHECK = bool(os.environ.get("SPELL_CHECK", True))
    
    # Performance Optimization
    WORKERS = int(os.environ.get("WORKERS", "8"))
    BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "100"))
    
    # Connection Pool Settings
    MAX_POOL_SIZE = int(os.environ.get("MAX_POOL_SIZE", "50"))
    MIN_POOL_SIZE = int(os.environ.get("MIN_POOL_SIZE", "10"))