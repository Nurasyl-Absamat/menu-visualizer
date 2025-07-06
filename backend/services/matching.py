from typing import List, Dict, Any
from fuzzywuzzy import fuzz
import logging

logger = logging.getLogger(__name__)

class MatchingService:
    """Product catalog matching service"""
    
    def __init__(self, db_service):
        self.db_service = db_service
        self.match_threshold = 80  # Fuzzy matching threshold
    
    async def match_products(self, product_names: List[str]) -> List[Dict[str, Any]]:
        """Match extracted product names against catalog"""
        try:
            matches = []
            
            for name in product_names:
                match_result = await self._find_best_match(name)
                matches.append(match_result)
            
            logger.info(f"Matched {len([m for m in matches if m['matched']])} of {len(matches)} products")
            return matches
            
        except Exception as e:
            logger.error(f"Product matching failed: {e}")
            # Return unmatched results on error
            return [{"name": name, "matched": False, "confidence": 0.0} for name in product_names]
    
    async def _find_best_match(self, product_name: str) -> Dict[str, Any]:
        """Find best match for a single product name"""
        try:
            # Get all products from catalog
            all_products = await self.db_service.get_products(limit=1000)
            
            best_match = None
            best_score = 0
            
            # Check each product for matches
            for product in all_products:
                # Check main name
                score = fuzz.ratio(product_name.lower(), product["name"].lower())
                if score > best_score:
                    best_score = score
                    best_match = product
                
                # Check aliases
                for alias in product.get("aliases", []):
                    score = fuzz.ratio(product_name.lower(), alias.lower())
                    if score > best_score:
                        best_score = score
                        best_match = product
                
                # Check partial matches for compound names
                if " " in product_name:
                    for word in product_name.split():
                        if len(word) > 3:  # Skip short words
                            score = fuzz.partial_ratio(word.lower(), product["name"].lower())
                            if score > best_score:
                                best_score = score
                                best_match = product
            
            # Determine if match is good enough
            if best_score >= self.match_threshold and best_match:
                return {
                    "name": product_name,
                    "matched": True,
                    "confidence": best_score / 100.0,
                    "product_id": best_match["_id"],
                    "matched_name": best_match["name"]
                }
            else:
                return {
                    "name": product_name,
                    "matched": False,
                    "confidence": best_score / 100.0 if best_score > 0 else 0.0
                }
                
        except Exception as e:
            logger.error(f"Error finding match for '{product_name}': {e}")
            return {
                "name": product_name,
                "matched": False,
                "confidence": 0.0
            } 