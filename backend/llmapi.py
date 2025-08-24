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
            You are an expert asset valuation agent working to assess the value of assets so they can be used as collateral for loans or financial instruments. Your assessment must be accurate, conservative, and suitable for collateral purposes.
            
            Analyze this product image and perform a web search to find the current market price range.
            
            Focus on:
            1. Identify the exact product (brand, model, specifications)
            2. Search current market prices across major retailers and marketplaces
            3. Provide a clear price range (e.g., "$150-$250" or "Starting at $199")
            4. List 2-3 specific sources where this product is available
            5. Note if this is a new, used, or refurbished item
            6. From the additional context {additional_context}, make an estimate of the price of the product after depreciating its values as per its age.
            7. Assess the asset's suitability as collateral (liquidity, market stability, depreciation factors)
            8. CRITICAL: Account for depreciation according to the item's age - older items should have significantly lower values than new ones, considering factors like:
                - Technology obsolescence (electronics, phones, computers)
                - Fashion/trend changes (clothing, accessories)
                - Mechanical wear and tear (watches, vehicles, machinery)
                - Market demand shifts over time
                - Brand value changes and market positioning
            
            Additional context: {additional_context}
            
            IMPORTANT: As a collateral assessment agent, prioritize accuracy and conservatism. Your valuation will be used for financial decision-making, so ensure all price information is current and well-sourced. Always factor in age-based depreciation to provide realistic, conservative values suitable for collateral purposes.
            
            Format your response with clear price information, sources, collateral assessment details, and explicit depreciation calculations based on age. Be specific about price ranges and include risk factors that could affect collateral value.
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
            You are an expert asset valuation agent working to assess the value of assets so they can be used as collateral for loans or financial instruments. Your assessment must be accurate, conservative, and suitable for collateral purposes.
            
            I need to find the current market price range for this product:
            
            Product Description: {product_description}
            Search Context: {search_context}
            
            Please perform a web search to find:
            1. Current market prices across major retailers
            2. A clear price range (e.g., "$150-$250")
            3. 2-3 specific sources with prices
            4. Whether prices are for new, used, or refurbished items
            5. Assess the asset's suitability as collateral (liquidity, market stability, depreciation factors)
            6. Provide a conservative collateral value estimate (typically 60-80% of market value for risk assessment)
            7. CRITICAL: Account for depreciation according to the item's age - older items should have significantly lower values than new ones, considering factors like:
                - Technology obsolescence (electronics, phones, computers)
                - Fashion/trend changes (clothing, accessories)
                - Mechanical wear and tear (watches, vehicles, machinery)
                - Market demand shifts over time
                - Brand value changes and market positioning
            
            IMPORTANT: As a collateral assessment agent, prioritize accuracy and conservatism. Your valuation will be used for financial decision-making, so ensure all price information is current and well-sourced. Always factor in age-based depreciation to provide realistic, conservative values suitable for collateral purposes.
            
            Focus on getting accurate, current pricing information suitable for collateral assessment, with explicit depreciation calculations based on age.
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
        
        # First, look for price patterns like $100-$200, $100 to $200, etc.
        price_patterns = [
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*[-–—]\s*\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s+to\s+\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*-\s*\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        # Look for single prices with better pattern matching
        # This will match $4,000, $4000, $4.99, etc.
        single_price_pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        single_prices = re.findall(single_price_pattern, text)
        
        if single_prices:
            # If multiple prices found, use the highest one (likely the main price)
            # Convert to numbers for comparison
            def price_to_number(price_str):
                return float(price_str.replace('$', '').replace(',', ''))
            
            # Sort by price value and take the highest
            sorted_prices = sorted(single_prices, key=price_to_number, reverse=True)
            highest_price = sorted_prices[0]
            
            # Check if it's a reasonable price for luxury items
            price_num = price_to_number(highest_price)
            if price_num < 100:  # If price is suspiciously low
                # Look for context clues about the actual price
                if any(word in text.lower() for word in ['luxury', 'rolex', 'expensive', 'premium', 'high-end']):
                    # Try to find a more reasonable price
                    for price in sorted_prices:
                        if price_to_number(price) > 100:
                            return f"Starting at {price}"
            
            return f"Starting at {highest_price}"
        
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
        
        