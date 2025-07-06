import os
import httpx
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class ImageSearchService:
    """Image search service for Pexels and Unsplash"""
    
    def __init__(self):
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.timeout = 10.0
    
    async def search_product_images(self, product_name: str, count: int = 3) -> List[Dict]:
        """Search for multiple product images, trying Pexels first, then Unsplash"""
        try:
            logger.info(f"Starting image search for product: '{product_name}' (requesting {count} images)")
            
            images = []
            
            # Try Pexels first
            if self.pexels_api_key:
                logger.info(f"Searching Pexels for: '{product_name}'")
                pexels_images = await self._search_pexels_multiple(product_name, count)
                images.extend(pexels_images)
                logger.info(f"✅ Pexels found {len(pexels_images)} images for '{product_name}'")
            else:
                logger.warning("Pexels API key not configured, skipping Pexels search")
            
            # If we don't have enough images, try Unsplash
            if len(images) < count and self.unsplash_access_key:
                remaining_count = count - len(images)
                logger.info(f"Searching Unsplash for: '{product_name}' (need {remaining_count} more images)")
                unsplash_images = await self._search_unsplash_multiple(product_name, remaining_count)
                images.extend(unsplash_images)
                logger.info(f"✅ Unsplash found {len(unsplash_images)} images for '{product_name}'")
            elif len(images) >= count:
                logger.info(f"Already have {len(images)} images, skipping Unsplash")
            else:
                logger.warning("Unsplash API key not configured, skipping Unsplash search")
            
            # Fill remaining slots with placeholders if needed
            while len(images) < count:
                placeholder_image = {
                    "url": self._get_placeholder_image(product_name),
                    "source": "placeholder",
                    "photographer": "System Generated",
                    "photographer_url": None
                }
                images.append(placeholder_image)
                logger.info(f"🔄 Added placeholder image for '{product_name}'")
            
            # Ensure we don't exceed the requested count
            images = images[:count]
            
            logger.info(f"✅ Total images found for '{product_name}': {len(images)}")
            return images
            
        except Exception as e:
            logger.error(f"Image search failed for '{product_name}': {e}")
            # Return placeholders on error
            placeholder_images = []
            for i in range(count):
                placeholder_images.append({
                    "url": self._get_placeholder_image(product_name),
                    "source": "placeholder",
                    "photographer": "System Generated",
                    "photographer_url": None
                })
            logger.info(f"🔄 Using {count} placeholder images due to error for '{product_name}'")
            return placeholder_images
    
    async def search_product_image(self, product_name: str) -> Optional[str]:
        """Legacy method for backward compatibility - returns single image URL"""
        images = await self.search_product_images(product_name, 1)
        if images and len(images) > 0:
            return images[0]["url"]
        return None
    
    async def _search_pexels_multiple(self, query: str, count: int) -> List[Dict]:
        """Search Pexels for multiple product images"""
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {
                "Authorization": self.pexels_api_key
            }
            params = {
                "query": f"{query} food",
                "per_page": min(count, 15),  # Pexels allows max 80, but we'll limit to 15
                "orientation": "landscape"
            }
            
            logger.debug(f"Pexels API request: {url} with query: '{query} food' (requesting {count} images)")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                
                logger.debug(f"Pexels API response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    total_results = data.get("total_results", 0)
                    photos = data.get("photos", [])
                    
                    logger.debug(f"Pexels API returned {total_results} total results, {len(photos)} photos")
                    
                    images = []
                    for photo in photos[:count]:  # Limit to requested count
                        image_data = {
                            "url": photo["src"]["medium"],
                            "source": "pexels",
                            "photographer": photo.get("photographer", "Unknown"),
                            "photographer_url": photo.get("photographer_url")
                        }
                        images.append(image_data)
                        logger.debug(f"Pexels image added: {image_data['url']} (by {image_data['photographer']})")
                    
                    return images
                else:
                    logger.warning(f"Pexels API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Pexels search failed for '{query}': {e}")
        
        return []
    
    async def _search_unsplash_multiple(self, query: str, count: int) -> List[Dict]:
        """Search Unsplash for multiple product images"""
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {
                "Authorization": f"Client-ID {self.unsplash_access_key}"
            }
            params = {
                "query": f"{query} food",
                "per_page": min(count, 30),  # Unsplash allows max 30
                "orientation": "landscape"
            }
            
            logger.debug(f"Unsplash API request: {url} with query: '{query} food' (requesting {count} images)")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                
                logger.debug(f"Unsplash API response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    total_results = data.get("total", 0)
                    results = data.get("results", [])
                    
                    logger.debug(f"Unsplash API returned {total_results} total results, {len(results)} photos")
                    
                    images = []
                    for photo in results[:count]:  # Limit to requested count
                        user = photo.get("user", {})
                        image_data = {
                            "url": photo["urls"]["regular"],
                            "source": "unsplash",
                            "photographer": user.get("name", "Unknown"),
                            "photographer_url": user.get("links", {}).get("html")
                        }
                        images.append(image_data)
                        logger.debug(f"Unsplash image added: {image_data['url']} (by {image_data['photographer']})")
                    
                    return images
                else:
                    logger.warning(f"Unsplash API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Unsplash search failed for '{query}': {e}")
        
        return []
    
    def _get_placeholder_image(self, product_name: str) -> str:
        """Generate placeholder image URL"""
        # Create a clean product name for placeholder
        clean_name = product_name.replace(" ", "+")
        return f"https://via.placeholder.com/400x300/e5e7eb/6b7280?text={clean_name}" 