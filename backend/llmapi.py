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

    def comprehensive_product_search(self, image_base64: str, image_format: str, 
                                   product_description: str, search_context: str = "") -> ProductPriceResult:
        """
        Comprehensive search combining base64 image analysis with product description for enhanced price search
        
        Args:
            image_base64: Base64 encoded image data
            image_format: Image format (e.g., 'jpeg', 'png', 'webp')
            product_description: Detailed description of the product
            search_context: Additional context for the search (e.g., "new", "used", "refurbished", age, condition)
            
        Returns:
            ProductPriceResult with comprehensive price information
        """
        try:
            # Clean the base64 string if it has a data URL prefix
            if image_base64.startswith('data:image/'):
                image_base64 = image_base64.split(',')[1]
            
            # Create a comprehensive prompt that combines image analysis with description search
            prompt = f"""
            I have both an image and a description of a product. Please analyze both and perform a comprehensive web search.
            
            PRODUCT DESCRIPTION: {product_description}
            SEARCH CONTEXT: {search_context}
            
            Please:
            1. Analyze the image to identify the exact product (brand, model, specifications)
            2. Compare the image analysis with the provided description
            3. Perform a web search using BOTH the visual information and description
            4. Find current market prices across major retailers and marketplaces
            5. Provide a clear price range (e.g., "$150-$250" or "Starting at $199")
            6. List 3-4 specific sources with prices
            7. Note if prices are for new, used, or refurbished items
            8. Consider depreciation based on age/condition mentioned in context
            9. Provide confidence level in your price assessment
            10. Include any relevant market trends or pricing insights
            
            Focus on getting the most accurate, current pricing information by combining visual and textual analysis.
            Be specific about price ranges and provide actionable market intelligence.
            """
            
            # Create the message with image, description, and web search capability
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=4000,  # Increased for comprehensive analysis
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
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            )
            
            # Parse the response to extract comprehensive information
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
            raise Exception(f"Error in comprehensive product search: {e}")

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
        marketplaces = ['eBay', 'Amazon', 'Craigslist', 'Facebook Marketplace', 'Etsy', 'Craigslist', 'OfferUp', 'Mercari']
        for marketplace in marketplaces:
            if marketplace.lower() in text.lower():
                return marketplace
        return "Various marketplaces"

# Convenience function for comprehensive search
def analyze_product_comprehensive(image_base64: str, image_format: str, 
                                product_description: str, search_context: str = "") -> ProductPriceResult:
    """
    Comprehensive analysis combining base64 image with product description for enhanced price search
    
    Args:
        image_base64: Base64 encoded image data
        image_format: Image format (e.g., 'jpeg', 'png', 'webp')
        product_description: Detailed description of the product
        search_context: Additional context for the search
        
    Returns:
        ProductPriceResult with comprehensive price information
    """
    client = AnthropicClient()
    return client.comprehensive_product_search(
        image_base64, image_format, product_description, search_context
    )

if __name__ == "__main__":
    # Example usage with actual function call
    try:
        print("=== Comprehensive Product Search Demo ===")
        
        # Image path - change this to your actual image path
        image_path = "/Users/uttamsingh/Desktop/hackathon/celebral-valley/backend/rolex.jpeg"
        
        print(f"\n Loading image from: {image_path}")
        
        # Check if image exists
        if not os.path.exists(image_path):
            print(f"\n Image not found: {image_path}")
            print(f"\n Please update the image_path variable with a valid image file")
            exit(1)
        
        print(f"\nImage found!")
        
        # Read and convert image to base64
        print(f"\n Converting image to base64...")
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        print(f"\n Image converted to base64 (length: {len(image_base64)} characters)")
        
        # Determine image format from file extension
        image_format = image_path.split('.')[-1].lower()
        print(f"\n Image format detected: {image_format}")
        
        # Product description and context
        product_description = "Rolex Submariner Date, stainless steel case, black dial, date display, automatic movement, water resistant to 300m"
        search_context = "Used condition, approximately 2 years old, excellent condition with minor wear on bracelet, authentic Rolex with original box and papers"
        
        print(f"\n Product Description: {product_description}")
        print(f"\n Search Context: {search_context}")
        
        # Call the comprehensive search function
        print("\n Starting comprehensive product analysis...")
        result = analyze_product_comprehensive(
            image_base64,
            image_format,
            product_description,
            search_context
        )
        
        # Display results
        print("\n Analysis Results:")
        print("=" * 50)
        print(f"Product: {result.product_name}")
        print(f"Price Range: {result.price_range}")
        print(f"Currency: {result.currency}")
        print(f"Marketplace: {result.marketplace}")
        print(f"Confidence: {result.confidence}")
        print(f"\n Detailed Analysis:")
        print("-" * 30)
        print(result.additional_info)
        
        print("\n Analysis Complete!")
        
    except Exception as e:
        print(f" Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        