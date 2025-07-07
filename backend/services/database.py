import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """MongoDB database service"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.products_collection = None
        self.sessions_collection = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://mongo:27017")
            database_name = os.getenv("MONGODB_DATABASE", "menu_matcher")
            
            self.client = MongoClient(mongodb_url)
            # Test connection
            self.client.admin.command('ismaster')
            
            self.db = self.client[database_name]
            self.products_collection = self.db.products
            self.sessions_collection = self.db.ocr_sessions
            
            # Create indexes
            self.products_collection.create_index("name")
            self.sessions_collection.create_index("upload_time")
            
            logger.info(f"Connected to MongoDB: {mongodb_url}")
            
            # Seed initial data if collections are empty
            await self._seed_initial_data()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _seed_initial_data(self):
        """Seed initial product catalog data"""
        if self.products_collection.count_documents({}) == 0:
            initial_products = [
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Caesar Salad",
                    "aliases": ["caesar", "caesar salad", "salad caesar"],
                    "image_url": None,
                    "tags": ["salad", "appetizer", "healthy"]
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Minestrone Soup",
                    "aliases": ["minestrone", "vegetable soup", "italian soup"],
                    "image_url": None,
                    "tags": ["soup", "italian", "vegetarian"]
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Margherita Pizza",
                    "aliases": ["margherita", "pizza margherita", "cheese pizza"],
                    "image_url": None,
                    "tags": ["pizza", "italian", "vegetarian"]
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Grilled Chicken",
                    "aliases": ["chicken", "grilled chicken", "chicken breast"],
                    "image_url": None,
                    "tags": ["chicken", "grilled", "protein"]
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Fish and Chips",
                    "aliases": ["fish chips", "fried fish", "fish & chips"],
                    "image_url": None,
                    "tags": ["fish", "fried", "british"]
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Chocolate Cake",
                    "aliases": ["chocolate cake", "cake", "dessert"],
                    "image_url": None,
                    "tags": ["dessert", "chocolate", "sweet"]
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Pasta Carbonara",
                    "aliases": ["carbonara", "pasta carbonara", "spaghetti carbonara"],
                    "image_url": None,
                    "tags": ["pasta", "italian", "carbonara"]
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Beef Burger",
                    "aliases": ["burger", "hamburger", "beef burger", "cheeseburger"],
                    "image_url": None,
                    "tags": ["burger", "beef", "american"]
                }
            ]
            
            self.products_collection.insert_many(initial_products)
            logger.info(f"Seeded {len(initial_products)} initial products")
    
    async def get_products(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get products from catalog"""
        try:
            cursor = self.products_collection.find().skip(offset).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            raise
    
    async def get_product(self, product_id: str) -> Optional[Dict]:
        """Get specific product by ID"""
        try:
            return self.products_collection.find_one({"_id": product_id})
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            raise
    
    async def find_products_by_name(self, name: str) -> List[Dict]:
        """Find products by name or aliases"""
        try:
            # Search in name and aliases
            query = {
                "$or": [
                    {"name": {"$regex": name, "$options": "i"}},
                    {"aliases": {"$regex": name, "$options": "i"}}
                ]
            }
            return list(self.products_collection.find(query))
        except Exception as e:
            logger.error(f"Error searching products by name '{name}': {e}")
            raise
    
    async def store_session(self, session_data: Dict) -> str:
        """Store OCR session results"""
        try:
            session_id = str(uuid.uuid4())
            session_doc = {
                "_id": session_id,
                "upload_time": datetime.utcnow(),
                **session_data
            }
            
            self.sessions_collection.insert_one(session_doc)
            logger.info(f"Stored session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error storing session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get OCR session by ID"""
        try:
            return self.sessions_collection.find_one({"_id": session_id})
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {e}")
            raise
    
    async def update_session(self, session_id: str, update_data: Dict) -> bool:
        """Update OCR session data"""
        try:
            result = self.sessions_collection.update_one(
                {"_id": session_id}, 
                {"$set": update_data}
            )
            if result.modified_count > 0:
                logger.info(f"Updated session: {session_id}")
                return True
            else:
                logger.warning(f"No session found to update: {session_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            raise 