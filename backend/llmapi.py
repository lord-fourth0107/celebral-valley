import anthropic
import os
import base64
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env file
    def load_dotenv():
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    load_dotenv()

class ProductPriceResult(BaseModel):
    product_name: str
    price_range: str
    currency: str
    marketplace: str
    confidence: str
    additional_info: Optional[str] = None

class AnthropicClient:
    def __init__(self):
        try: 
            API_KEY = os.getenv("ANTHROPIC_API_KEY")
            if not API_KEY:
                raise Exception("ANTHROPIC_API_KEY is not set")
        except Exception as e:
            raise Exception(f"Error setting up API key: {e}")
        
        self.client = anthropic.Anthropic(api_key=API_KEY)
        
        # Original pricing tool
        self.pricing_tool = {
            "name": "get_used_product_price",
            "description": "Looks up the current market price for a used or vintage product on marketplaces like eBay. Requires a specific product name and its condition.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The specific name, brand, and model of the product. Example: 'Sony a7 III Mirrorless Camera'."
                    },
                    "condition": {
                        "type": "string",
                        "description": "The condition and age of the item. Example: 'used, 5 years old, good condition'."
                    },
                    "category": {
                        "type": "string",
                        "description": "The product's category, e.g., 'Electronics', 'Handbags', 'Watches'."
                    }
                },
                "required": ["product_name", "condition"]
            }
        }
        
        # New tool for image-based web search
        self.image_web_search_tool = {
            "name": "search_product_price_from_image",
            "description": "Analyzes an image of a product and performs a web search to find current market prices and price ranges for that product.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "Base64 encoded image data of the product"
                    },
                    "image_format": {
                        "type": "string",
                        "description": "Image format (e.g., 'jpeg', 'png', 'webp')"
                    },
                    "additional_context": {
                        "type": "string",
                        "description": "Any additional context about the product or search requirements"
                    }
                },
                "required": ["image_data", "image_format"]
            }
        }
        
        # Tool for web search with product description
        self.web_search_tool = {
            "name": "web_search",
            "description": "Perform a web search to find current market prices and availability for a specific product",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find product prices and market information"
                    },
                    "search_type": {
                        "type": "string",
                        "description": "Type of search: 'price_comparison', 'market_analysis', 'availability'",
                        "enum": ["price_comparison", "market_analysis", "availability"]
                    }
                },
                "required": ["query"]
            }
        }

    def get_response_from_claude(self, prompt: str, stop_sequences: Optional[List[str]] = None) -> str:
        """
        Get a response from Claude using text prompt
        """
        try:
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
                stop_sequences=stop_sequences
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Error getting response from Claude: {e}")

    def search_product_price_from_image(self, image_path: str, additional_context: str = "") -> ProductPriceResult:
        """
        Analyze an image and search for product price information using Claude's web search capability
        
        Args:
            image_path: Path to the image file
            additional_context: Additional context about the product or search requirements
            
        Returns:
            ProductPriceResult with price information
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine image format from file extension
            image_format = image_path.split('.')[-1].lower()
            
            # Create the prompt for Claude
            prompt = f"""
            Analyze this product image and perform a web search to find the current market price range.
            
            Focus on:
            1. Identify the exact product (brand, model, specifications)
            2. Search current market prices across major retailers and marketplaces
            3. Provide a clear price range (e.g., "$150-$250" or "Starting at $199")
            4. List 2-3 specific sources where this product is available
            5. Note if this is a new, used, or refurbished item
            6. From the additional context {additional_context}, make an estimate of the price of the product after depreciating its values as per its age.
            
            Additional context: {additional_context}
            
            Format your response with clear price information and sources. Be specific about price ranges.
            """
            
            # Create the message with image and web search capability
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{image_format}",
                                    "data": image_data
                                }
                            }
                        ]
                    }
                ]
            )
            
            # Parse the response to extract price information
            response_text = message.content[0].text
            
            # Extract product information from the response
            product_name = self._extract_product_name(response_text)
            price_range = self._extract_price_range(response_text)
            currency = self._extract_currency(response_text)
            marketplace = self._extract_marketplace(response_text)
            
            return ProductPriceResult(
                product_name=product_name,
                price_range=price_range,
                currency=currency,
                marketplace=marketplace,
                confidence="high" if price_range else "medium",
                additional_info=response_text
            )
            
        except Exception as e:
            raise Exception(f"Error searching product price from image: {e}")

    def get_price_range_from_description(self, product_description: str, search_context: str = "") -> ProductPriceResult:
        """
        Get price range for a product based on its description using web search
        
        Args:
            product_description: Detailed description of the product
            search_context: Additional context for the search (e.g., "new", "used", "refurbished")
            
        Returns:
            ProductPriceResult with price information
        """
        try:
            # Create a focused prompt for price search
            prompt = f"""
            I need to find the current market price range for this product:
            
            Product Description: {product_description}
            Search Context: {search_context}
            
            Please perform a web search to find:
            1. Current market prices across major retailers
            2. A clear price range (e.g., "$150-$250")
            3. 2-3 specific sources with prices
            4. Whether prices are for new, used, or refurbished items
            
            Focus on getting accurate, current pricing information.
            """
            
            # Use Claude with web search capability
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Extract information from the response
            product_name = self._extract_product_name(response_text)
            price_range = self._extract_price_range(response_text)
            currency = self._extract_currency(response_text)
            marketplace = self._extract_marketplace(response_text)
            
            return ProductPriceResult(
                product_name=product_name,
                price_range=price_range,
                currency=currency,
                marketplace=marketplace,
                confidence="high" if price_range else "medium",
                additional_info=response_text
            )
            
        except Exception as e:
            raise Exception(f"Error getting price range from description: {e}")

    def get_used_product_price(self, product_name: str, condition: str, category: str = "") -> Dict[str, Any]:
        """
        Get used product price using the existing pricing tool
        """
        try:
            prompt = f"""
            Please search for the current market price of this used product:
            Product: {product_name}
            Condition: {condition}
            Category: {category}
            
            Provide the price range and any relevant market information.
            """
            
            response = self.get_response_from_claude(prompt)
            
            return {
                "product_name": product_name,
                "condition": condition,
                "category": category,
                "response": response,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "product_name": product_name,
                "condition": condition,
                "category": category,
                "error": str(e),
                "status": "error"
            }

    def _extract_product_name(self, text: str) -> str:
        """Extract product name from Claude's response"""
        # Simple extraction - you might want to use more sophisticated NLP
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['product', 'item', 'brand', 'model']):
                return line.strip()
        return "Product name not found"

    def _extract_price_range(self, text: str) -> str:
        """Extract price range from Claude's response"""
        import re
        # Look for price patterns like $100-$200, $100 to $200, etc.
        price_patterns = [
            r'\$\d+(?:\.\d{2})?\s*[-–—]\s*\$\d+(?:\.\d{2})?',
            r'\$\d+(?:\.\d{2})?\s+to\s+\$\d+(?:\.\d{2})?',
            r'\$\d+(?:\.\d{2})?\s*-\s*\$\d+(?:\.\d{2})?'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        # Look for single prices
        single_price = re.search(r'\$\d+(?:\.\d{2})?', text)
        if single_price:
            return f"Starting at {single_price.group()}"
        
        return "Price range not found"

    def _extract_currency(self, text: str) -> str:
        """Extract currency from Claude's response"""
        if '$' in text:
            return "USD"
        elif '€' in text:
            return "EUR"
        elif '£' in text:
            return "GBP"
        elif '₹' in text:
            return "INR"
        return "USD"  # Default

    def _extract_marketplace(self, text: str) -> str:
        """Extract marketplace information from Claude's response"""
        marketplaces = ['eBay', 'Amazon', 'Craigslist', 'Facebook Marketplace', 'Etsy']
        for marketplace in marketplaces:
            if marketplace.lower() in text.lower():
                return marketplace
        return "Various marketplaces"

# Example usage functions
def analyze_product_image_and_get_price(image_path: str, context: str = "") -> ProductPriceResult:
    """
    Convenience function to analyze a product image and get price information
    
    Args:
        image_path: Path to the image file
        context: Additional context about the product
        
    Returns:
        ProductPriceResult with price information
    """
    client = AnthropicClient()
    return client.search_product_price_from_image(image_path, context)

def get_product_price_from_description(product_description: str, search_context: str = "") -> ProductPriceResult:
    """
    Convenience function to get price range from product description using web search
    
    Args:
        product_description: Detailed description of the product
        search_context: Additional context for the search
        
    Returns:
        ProductPriceResult with price information
    """
    client = AnthropicClient()
    return client.get_price_range_from_description(product_description, search_context)

if __name__ == "__main__":
    # Example usage
    try:
        print("=== Image-based Price Search ===")
        # Replace with actual image path
        image_path = "/Users/uttamsingh/Desktop/hackathon/celebral-valley/backend/rolex.jpeg"
        result = analyze_product_image_and_get_price(image_path, "Looking for current market prices")
        print(f"Product: {result.product_name}")
        print(f"Price Range: {result.price_range}")
        print(f"Currency: {result.currency}")
        print(f"Marketplace: {result.marketplace}")
        print(f"Additional Info: {result.additional_info}")
        
        print("\n=== Description-based Price Search ===")
        # Example with product description
        product_desc = "Used Rolex watch for 1 year"
        desc_result = get_product_price_from_description(product_desc, " looks like a new watch, current market prices")
        print(f"Product: {desc_result.product_name}")
        print(f"Price Range: {desc_result.price_range}")
        print(f"Currency: {desc_result.currency}")
        print(f"Marketplace: {desc_result.marketplace}")
        print(f"Additional Info: {desc_result.additional_info}")
        
    except Exception as e:
        print(f"Error: {e}")
        
        