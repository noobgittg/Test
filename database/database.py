import asyncio
import motor.motor_asyncio
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from config import Config
import logging
from typing import List, Dict, Optional
import time
from cachetools import TTLCache
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.clients = []
        self.databases = []
        self.collections = []
        self.current_db = 0
        self.cache = TTLCache(maxsize=1000, ttl=Config.CACHE_TIME)
        self.redis_client = None
        
    async def initialize(self):
        """Initialize all 4 database connections with connection pooling"""
        db_uris = [
            Config.DATABASE_URI_1,
            Config.DATABASE_URI_2, 
            Config.DATABASE_URI_3,
            Config.DATABASE_URI_4
        ]
        
        for i, uri in enumerate(db_uris):
            if uri:
                try:
                    client = AsyncIOMotorClient(
                        uri,
                        maxPoolSize=Config.MAX_POOL_SIZE,
                        minPoolSize=Config.MIN_POOL_SIZE,
                        maxIdleTimeMS=30000,
                        waitQueueTimeoutMS=5000,
                        serverSelectionTimeoutMS=5000
                    )
                    
                    # Test connection
                    await client.admin.command('ping')
                    
                    database = client[Config.DATABASE_NAME]
                    collection = database[Config.COLLECTION_NAME]
                    
                    # Create indexes for faster queries
                    await collection.create_index([("file_name", "text")])
                    await collection.create_index("file_id")
                    await collection.create_index("chat_id")
                    
                    self.clients.append(client)
                    self.databases.append(database)
                    self.collections.append(collection)
                    
                    logger.info(f"Database {i+1} connected successfully")
                    
                except Exception as e:
                    logger.error(f"Failed to connect to database {i+1}: {e}")
        
        # Initialize Redis for caching
        try:
            self.redis_client = redis.from_url(Config.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
    
    def get_collection(self):
        """Get collection with load balancing"""
        if not self.collections:
            return None
        
        collection = self.collections[self.current_db]
        self.current_db = (self.current_db + 1) % len(self.collections)
        return collection
    
    async def save_file(self, media):
        """Save file to database with load balancing"""
        file_id, file_ref = unpack_new_file_id(media.file_id)
        
        file_data = {
            'file_id': file_id,
            'file_ref': file_ref,
            'file_name': media.file_name,
            'file_size': media.file_size,
            'file_type': media.file_type,
            'mime_type': getattr(media, 'mime_type', ''),
            'caption': getattr(media, 'caption', ''),
            'chat_id': media.chat.id,
            'message_id': media.message_id,
            'date': media.date
        }
        
        # Try to save to multiple databases for redundancy
        saved = False
        for collection in self.collections:
            try:
                await collection.insert_one(file_data)
                saved = True
                break
            except DuplicateKeyError:
                pass
            except Exception as e:
                logger.error(f"Error saving to database: {e}")
                continue
        
        if saved:
            # Clear cache for this query pattern
            await self.clear_search_cache(media.file_name)
        
        return saved
    
    async def get_search_results(self, query: str, file_type: str = None, max_results: int = Config.MAX_RESULTS):
        """Fast search with caching and load balancing"""
        cache_key = f"search:{query}:{file_type}:{max_results}"
        
        # Check Redis cache first
        if self.redis_client:
            try:
                cached_result = await self.redis_client.get(cache_key)
                if cached_result:
                    import json
                    return json.loads(cached_result)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Check local cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Search in databases
        results = []
        search_tasks = []
        
        for collection in self.collections:
            task = self._search_in_collection(collection, query, file_type, max_results)
            search_tasks.append(task)
        
        # Execute searches concurrently
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine results from all databases
        seen_file_ids = set()
        for result in search_results:
            if isinstance(result, list):
                for file_doc in result:
                    if file_doc['file_id'] not in seen_file_ids:
                        results.append(file_doc)
                        seen_file_ids.add(file_doc['file_id'])
                        
                        if len(results) >= max_results:
                            break
            
            if len(results) >= max_results:
                break
        
        # Sort by relevance (file name similarity)
        results.sort(key=lambda x: self._calculate_relevance(query, x['file_name']), reverse=True)
        results = results[:max_results]
        
        # Cache results
        self.cache[cache_key] = results
        
        # Cache in Redis
        if self.redis_client:
            try:
                import json
                await self.redis_client.setex(
                    cache_key, 
                    Config.CACHE_TIME, 
                    json.dumps(results, default=str)
                )
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        return results
    
    async def _search_in_collection(self, collection, query: str, file_type: str, max_results: int):
        """Search in a specific collection"""
        try:
            # Build search pipeline for better performance
            pipeline = []
            
            # Text search stage
            if query:
                pipeline.append({
                    "$match": {
                        "$text": {"$search": query}
                    }
                })
            
            # File type filter
            if file_type:
                pipeline.append({
                    "$match": {"file_type": file_type}
                })
            
            # Add score for text search relevance
            if query:
                pipeline.append({
                    "$addFields": {
                        "score": {"$meta": "textScore"}
                    }
                })
                pipeline.append({
                    "$sort": {"score": {"$meta": "textScore"}}
                })
            
            # Limit results
            pipeline.append({"$limit": max_results})
            
            # Execute aggregation pipeline
            cursor = collection.aggregate(pipeline)
            return await cursor.to_list(length=max_results)
            
        except Exception as e:
            logger.error(f"Search error in collection: {e}")
            return []
    
    def _calculate_relevance(self, query: str, filename: str) -> float:
        """Calculate relevance score for sorting"""
        query_lower = query.lower()
        filename_lower = filename.lower()
        
        # Exact match gets highest score
        if query_lower == filename_lower:
            return 1.0
        
        # Starts with query gets high score
        if filename_lower.startswith(query_lower):
            return 0.9
        
        # Contains query gets medium score
        if query_lower in filename_lower:
            return 0.7
        
        # Word match gets lower score
        query_words = query_lower.split()
        filename_words = filename_lower.split()
        
        matches = sum(1 for word in query_words if word in filename_words)
        if matches > 0:
            return 0.5 + (matches / len(query_words)) * 0.2
        
        return 0.0
    
    async def clear_search_cache(self, filename: str):
        """Clear cache entries related to a filename"""
        if self.redis_client:
            try:
                # Get all keys matching search pattern
                keys = await self.redis_client.keys("search:*")
                for key in keys:
                    await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Cache clear error: {e}")
    
    async def get_file_details(self, file_id: str):
        """Get file details by file_id with caching"""
        cache_key = f"file:{file_id}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Search in all databases
        for collection in self.collections:
            try:
                result = await collection.find_one({"file_id": file_id})
                if result:
                    self.cache[cache_key] = result
                    return result
            except Exception as e:
                logger.error(f"Error getting file details: {e}")
                continue
        
        return None
    
    async def get_stats(self):
        """Get database statistics"""
        total_files = 0
        for collection in self.collections:
            try:
                count = await collection.count_documents({})
                total_files += count
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
        
        return {
            'total_files': total_files,
            'active_databases': len(self.collections),
            'cache_size': len(self.cache)
        }

# Global database manager instance
db = DatabaseManager()

def unpack_new_file_id(new_file_id):
    """Unpack new file_id to get file_id and file_ref"""
    import base64
    import struct
    
    try:
        decoded = base64.urlsafe_b64decode(new_file_id + "=" * (-len(new_file_id) % 4))
        file_id = struct.unpack("<Q", decoded[:8])[0]
        file_ref = base64.urlsafe_b64encode(decoded[8:]).decode().rstrip("=")
        return str(file_id), file_ref
    except Exception:
        return new_file_id, ""