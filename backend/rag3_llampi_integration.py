#!/usr/bin/env python3
"""
RAG3-LLAMPI Integration Script

This script integrates the RAG3 image similarity system with the LLAMPI price calculation system.
It allows users to:
1. Input an image and user description
2. Find similar images using RAG3 vector database
3. Calculate prices for both input and similar images using LLAMPI
4. Display comprehensive results

Usage:
    python rag3_llampi_integration.py
    # or import and use the functions
    from rag3_llampi_integration import integrate_rag3_with_llampi
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
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

# Import required modules
try:
    from rag3 import ImageRAGSystem
    from llmapi import AnthropicClient, ProductPriceResult
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure rag3.py and llmapi.py are in the same directory")
    sys.exit(1)


class RAG3LLAMPIIntegrator:
    """Main integration class for RAG3 and LLAMPI systems"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.rag_system = None
        self.llm_client = None
    
    def initialize_systems(self) -> bool:
        """Initialize RAG3 and LLM systems"""
        try:
            if self.verbose:
                print("📊 Initializing RAG3 system...")
                print("   Loading CLIP model and connecting to Qdrant...")
            
            self.rag_system = ImageRAGSystem()
            
            if self.verbose:
                print("🤖 Initializing LLM API client...")
                print("   Initializing Anthropic client...")
            
            self.llm_client = AnthropicClient()
            
            if self.verbose:
                print("   ✅ RAG3 system initialized successfully")
                print("   ✅ LLM API client initialized successfully")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize systems: {e}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return False
    
    def find_similar_images(self, image_path: str, top_k: int = 3, 
                           score_threshold: float = 0.0) -> List[Dict]:
        """Find similar images using RAG3 system"""
        if not self.rag_system:
            raise RuntimeError("RAG3 system not initialized")
        
        if self.verbose:
            print(f"🔍 Finding {top_k} similar images...")
            print(f"   Processing image: {image_path}")
            print("   Extracting embeddings and searching database...")
            print("   ⏳ This may take a few minutes on first run...")
        
        try:
            similar_images = self.rag_system.find_similar_images(
                image_path, 
                top_k=top_k, 
                score_threshold=score_threshold
            )
            
            if self.verbose:
                print("   ✅ Database search completed")
                print(f"   Found {len(similar_images)} similar images")
            
            return similar_images
            
        except Exception as e:
            error_msg = f"Database search failed: {e}"
            if self.verbose:
                print(f"   ❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def analyze_image_pricing(self, image_path: str, 
                             user_description: str = "") -> Optional[ProductPriceResult]:
        """Analyze image and get pricing using LLM API"""
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")
        
        if self.verbose:
            print(f"💰 Analyzing image and calculating price...")
            print(f"   Input image: {image_path}")
            print(f"   User description: {user_description}")
            print("   🔍 Analyzing image with Claude...")
            print("   ⏳ This may take 1-2 minutes for API calls...")
        
        try:
            # Log the API call details
            print(f"\n🤖 ANTHROPIC API CALL DETAILS:")
            print(f"   Method: search_product_price_from_image")
            print(f"   Image path: {image_path}")
            print(f"   Additional context: {user_description}")
            print(f"   API Key: {os.getenv('ANTHROPIC_API_KEY', 'Not set')[:10]}...")
            
            pricing_result = self.llm_client.search_product_price_from_image(
                image_path, 
                additional_context=user_description
            )
            
            if self.verbose:
                print(f"   ✅ Input image price calculated: {pricing_result.initial_price}")
                print(f"   💰 Collateral value: {pricing_result.collateral_price}")
            
            return pricing_result
            
        except Exception as e:
            error_msg = f"Error calculating input image price: {e}"
            if self.verbose:
                print(f"   ❌ {error_msg}")
            return None
    
    def analyze_similar_images_pricing(self, similar_images: List[Dict]) -> List[Dict]:
        """Analyze pricing for similar images"""
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")
        
        if self.verbose:
            print(f"🔍 Analyzing {len(similar_images)} similar images and calculating prices...")
        
        similar_images_analysis = []
        
        for i, similar_img in enumerate(similar_images):
            if self.verbose:
                print(f"\n--- Processing Similar Image {i+1}/{len(similar_images)} ---")
                print(f"Name: {similar_img['name']}")
                print(f"Type: {similar_img['type']}")
                print(f"User Description: {similar_img['user_description']}")
                print(f"Similarity Score: {similar_img['score']:.3f}")
            
            try:
                # Log the API call details for similar images
                if self.verbose:
                    print(f"\n🤖 ANTHROPIC API CALL for Similar Image {i+1}:")
                    print(f"   Method: get_price_range_from_description")
                    print(f"   Description: {similar_img['detailed_description'][:100]}...")
                    print(f"   Search context: Similar to {similar_img['name']}, {similar_img['user_description']}")
                    print(f"   API Key: {os.getenv('ANTHROPIC_API_KEY', 'Not set')[:10]}...")
                
                # Get price for similar image using its description
                similar_img_price = self.llm_client.get_price_range_from_description(
                    similar_img['detailed_description'],
                    search_context=f"Similar to {similar_img['name']}, {similar_img['user_description']}"
                )
                
                # Combine RAG3 data with price data
                combined_analysis = self._create_combined_analysis(similar_img, similar_img_price)
                similar_images_analysis.append(combined_analysis)
                
                if self.verbose:
                    print(f"✅ Price calculated: {similar_img_price.price_range}")
                
            except Exception as e:
                if self.verbose:
                    print(f"❌ Error calculating price for similar image {i+1}: {e}")
                
                # Add image without price data
                combined_analysis = self._create_combined_analysis(similar_img, None, error=str(e))
                similar_images_analysis.append(combined_analysis)
        
        return similar_images_analysis
    
    def _create_combined_analysis(self, similar_img: Dict, 
                                 price_data: Optional[ProductPriceResult], 
                                 error: str = None) -> Dict:
        """Create combined analysis data structure"""
        if price_data:
            return {
                'rag3_data': similar_img,
                'price_data': price_data,
                'combined_info': {
                    'name': similar_img['name'],
                    'type': similar_img['type'],
                    'user_description': similar_img['user_description'],
                    'detailed_description': similar_img['detailed_description'],
                    'similarity_score': similar_img['score'],
                    'initial_price': price_data.initial_price,
                    'collateral_price': price_data.collateral_price,
                    'price_range': price_data.price_range,
                    'currency': price_data.currency,
                    'marketplace': price_data.marketplace,
                    'confidence': price_data.confidence,
                    'additional_info': getattr(price_data, 'additional_info', None)
                }
            }
        else:
            return {
                'rag3_data': similar_img,
                'price_data': None,
                'combined_info': {
                    'name': similar_img['name'],
                    'type': similar_img['type'],
                    'user_description': similar_img['user_description'],
                    'detailed_description': similar_img['detailed_description'],
                    'similarity_score': similar_img['score'],
                    'initial_price': 'Price calculation failed',
                    'collateral_price': 'Price calculation failed',
                    'price_range': 'Price calculation failed',
                    'currency': 'Unknown',
                    'marketplace': 'Unknown',
                    'confidence': 'low',
                    'additional_info': f'Error: {error}' if error else 'Price calculation failed'
                }
            }
    
    def create_input_image_analysis(self, image_path: str, user_description: str, 
                                   pricing_result: Optional[ProductPriceResult]) -> Dict:
        """Create input image analysis structure"""
        return {
            'image_path': image_path,
            'user_description': user_description,
            'price_data': pricing_result,
            'analysis_summary': {
                'name': pricing_result.product_name if pricing_result else 'Unknown',
                'initial_price': pricing_result.initial_price if pricing_result else 'Price calculation failed',
                'collateral_price': pricing_result.collateral_price if pricing_result else 'Price calculation failed',
                'price_range': pricing_result.price_range if pricing_result else 'Price calculation failed',
                'currency': pricing_result.currency if pricing_result else 'Unknown',
                'marketplace': pricing_result.marketplace if pricing_result else 'Unknown',
                'confidence': pricing_result.confidence if pricing_result else 'low'
            }
        }
    
    def create_summary(self, input_image_price: Optional[ProductPriceResult], 
                      similar_images_analysis: List[Dict]) -> Dict:
        """Create summary statistics"""
        total_images = len(similar_images_analysis) + 1  # +1 for input image
        successful_price_calculations = sum(1 for img in similar_images_analysis if img['price_data'] is not None)
        
        if input_image_price:
            successful_price_calculations += 1
        
        return {
            'total_images_processed': total_images,
            'successful_price_calculations': successful_price_calculations,
            'failed_price_calculations': total_images - successful_price_calculations,
            'success_rate': f"{(successful_price_calculations/total_images)*100:.1f}%",
            'input_image_found': input_image_price is not None,
            'similar_images_found': len(similar_images_analysis)
        }
    
    def integrate(self, input_image_path: str, 
                 user_description: str = "",
                 top_k: int = 3,
                 score_threshold: float = 0.0,
                 return_json: bool = False) -> Dict:
        """Main integration method"""
        if self.verbose:
            print("=" * 80)
            print("🔄 INTEGRATING RAG3 WITH LLAMPI")
            print("=" * 80)
        
        try:
            # Step 1: Initialize systems
            if not self.initialize_systems():
                return {"error": "Failed to initialize systems"}
            
            # Step 2: Find similar images
            similar_images = self.find_similar_images(input_image_path, top_k, score_threshold)
            
            # Step 3: Analyze input image pricing
            input_image_price = self.analyze_image_pricing(input_image_path, user_description)
            
            # Step 4: Analyze similar images pricing
            similar_images_analysis = self.analyze_similar_images_pricing(similar_images)
            
            # Step 5: Prepare results
            if self.verbose:
                print(f"\n📋 Preparing final results...")
            
            input_image_analysis = self.create_input_image_analysis(
                input_image_path, user_description, input_image_price
            )
            
            summary = self.create_summary(input_image_price, similar_images_analysis)
            
            results = {
                'input_image_analysis': input_image_analysis,
                'similar_images_analysis': similar_images_analysis,
                'summary': summary
            }
            
            # Step 6: Print results if verbose
            if self.verbose:
                self._print_comprehensive_results(results, input_image_path, user_description)
            
            # Return JSON if requested
            if return_json:
                return self._convert_results_to_json(results)
            else:
                return results
        
        except Exception as e:
            error_msg = f"Error in rag3-llampi integration: {str(e)}"
            if self.verbose:
                print(f"\n❌ {error_msg}")
            return {"error": error_msg}
    
    def _print_comprehensive_results(self, results: Dict, input_image_path: str, user_description: str):
        """Print comprehensive results in a formatted way"""
        print(f"\n{'='*80}")
        print("📊 FINAL RESULTS SUMMARY")
        print(f"{'='*80}")
        
        # Input image analysis
        input_analysis = results['input_image_analysis']
        print(f"\n🎯 INPUT IMAGE ANALYSIS:")
        print(f"   Image: {input_image_path}")
        print(f"   User Description: {user_description}")
        
        price_data = input_analysis['price_data']
        if price_data:
            print(f"   Product Name: {price_data.product_name}")
            print(f"   Initial Price: {price_data.initial_price}")
            print(f"   Collateral Price: {price_data.collateral_price}")
            print(f"   Currency: {price_data.currency}")
            print(f"   Marketplace: {price_data.marketplace}")
            print(f"   Confidence: {price_data.confidence}")
            
            if hasattr(price_data, 'additional_info') and price_data.additional_info:
                print(f"\n   💰 COLLATERAL VALUE EXPLANATION:")
                print(f"   {price_data.additional_info}")
        else:
            print(f"   ❌ Price calculation failed")
        
        # Similar images analysis
        similar_images = results['similar_images_analysis']
        print(f"\n🔍 SIMILAR IMAGES ANALYSIS ({len(similar_images)} images):")
        for i, img_analysis in enumerate(similar_images):
            combined_info = img_analysis['combined_info']
            print(f"\n   --- Similar Image {i+1} ---")
            print(f"   Name: {combined_info['name']}")
            print(f"   Type: {combined_info['type']}")
            print(f"   User Description: {combined_info['user_description']}")
            print(f"   Similarity Score: {combined_info['similarity_score']:.3f}")
            print(f"   Initial Price: {combined_info['initial_price']}")
            print(f"   Collateral Price: {combined_info['collateral_price']}")
            print(f"   Currency: {combined_info['currency']}")
            print(f"   Marketplace: {combined_info['marketplace']}")
            print(f"   Confidence: {combined_info['confidence']}")
        
        # Summary statistics
        summary = results['summary']
        print(f"\n📈 SUMMARY STATISTICS:")
        print(f"   Total Images Processed: {summary['total_images_processed']}")
        print(f"   Successful Price Calculations: {summary['successful_price_calculations']}")
        print(f"   Failed Price Calculations: {summary['failed_price_calculations']}")
        print(f"   Success Rate: {summary['success_rate']}")
        print(f"   Input Image Analysis: {'✅ Success' if summary['input_image_found'] else '❌ Failed'}")
        print(f"   Similar Images Found: {summary['similar_images_found']}")
        
        print(f"\n{'='*80}")
        print("✅ INTEGRATION COMPLETED SUCCESSFULLY")
        print(f"{'='*80}")
    
    def _convert_results_to_json(self, results: Dict) -> Dict:
        """Convert results to JSON-serializable format"""
        try:
            json_results = {}
            
            # Convert input image analysis
            input_analysis = results['input_image_analysis']
            json_results['input_image_analysis'] = {
                'image_path': input_analysis['image_path'],
                'user_description': input_analysis['user_description'],
                'analysis_summary': input_analysis['analysis_summary']
            }
            
            # Add detailed price data if available
            if input_analysis['price_data']:
                price_data = input_analysis['price_data']
                collateral_explanation = getattr(price_data, 'additional_info', None)
                
                json_results['input_image_analysis']['price_data'] = {
                    'product_name': price_data.product_name,
                    'initial_price': price_data.initial_price,
                    'collateral_price': price_data.collateral_price,
                    'price_range': price_data.price_range,
                    'currency': price_data.currency,
                    'marketplace': price_data.marketplace,
                    'confidence': price_data.confidence,
                    'collateral_explanation': collateral_explanation
                }
            
            # Convert similar images analysis
            similar_images = results['similar_images_analysis']
            json_results['similar_images_analysis'] = []
            
            for img_analysis in similar_images:
                combined_info = img_analysis['combined_info']
                json_img = {
                    'name': combined_info['name'],
                    'type': combined_info['type'],
                    'user_description': combined_info['user_description'],
                    'similarity_score': combined_info['similarity_score'],
                    'initial_price': combined_info['initial_price'],
                    'collateral_price': combined_info['collateral_price'],
                    'price_range': combined_info['price_range'],
                    'currency': combined_info['currency'],
                    'marketplace': combined_info['marketplace'],
                    'confidence': combined_info['confidence']
                }
                json_results['similar_images_analysis'].append(json_img)
            
            # Add summary and metadata
            json_results['summary'] = results['summary']
            json_results['metadata'] = {
                'timestamp': int(time.time()),
                'version': '2.0',
                'integration_type': 'RAG3-LLAMPI'
            }
            
            return json_results
            
        except Exception as e:
            return {"error": f"Failed to convert results to JSON: {str(e)}"}


# Convenience functions for backward compatibility
def integrate_rag3_with_llampi(input_image_path: str, 
                              user_description: str = "",
                              top_k: int = 3,
                              score_threshold: float = 0.0,
                              verbose: bool = True,
                              return_json: bool = False) -> Dict:
    """Backward compatibility function"""
    integrator = RAG3LLAMPIIntegrator(verbose=verbose)
    return integrator.integrate(
        input_image_path=input_image_path,
        user_description=user_description,
        top_k=top_k,
        score_threshold=score_threshold,
        return_json=return_json
    )


def quick_price_check(image_path: str, description: str = "") -> Optional[ProductPriceResult]:
    """Quick function to get price for a single image without RAG search"""
    try:
        print(f"\n🤖 QUICK PRICE CHECK - ANTHROPIC API CALL:")
        print(f"   Method: search_product_price_from_image")
        print(f"   Image path: {image_path}")
        print(f"   Description: {description}")
        print(f"   API Key: {os.getenv('ANTHROPIC_API_KEY', 'Not set')[:10]}...")
        
        llm_client = AnthropicClient()
        return llm_client.search_product_price_from_image(image_path, description)
    except Exception as e:
        print(f"Quick price check failed: {e}")
        return None


def find_similar_only(image_path: str, top_k: int = 3) -> List[Dict]:
    """Find similar images only, without price calculation"""
    try:
        print(f"\n🔍 RAG3 API CALL - Finding Similar Images:")
        print(f"   Method: find_similar_images")
        print(f"   Image path: {image_path}")
        print(f"   Top K: {top_k}")
        print(f"   Qdrant Host: localhost:6333")
        
        rag_system = ImageRAGSystem()
        return rag_system.find_similar_images(image_path, top_k=top_k)
    except Exception as e:
        print(f"Similar image search failed: {e}")
        return []


def get_json_results(input_image_path: str, 
                    user_description: str = "",
                    top_k: int = 3,
                    score_threshold: float = 0.0) -> Dict:
    """Get results directly as JSON data"""
    return integrate_rag3_with_llampi(
        input_image_path=input_image_path,
        user_description=user_description,
        top_k=top_k,
        score_threshold=score_threshold,
        verbose=False,
        return_json=True
    )


class ResultsManager:
    """Class for managing and saving results"""
    
    @staticmethod
    def save_to_text_file(results: Dict, image_path: str, filename: str = None) -> str:
        """Save results to a text file"""
        try:
            if not filename:
                image_name = Path(image_path).stem
                timestamp = str(int(time.time()))
                filename = f"rag3_llampi_results_{image_name}_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("RAG3-LLAMPI Integration Results\n")
                f.write("=" * 50 + "\n\n")
                
                # Input image analysis
                f.write("INPUT IMAGE ANALYSIS:\n")
                f.write(f"Image: {image_path}\n")
                f.write(f"User Description: {results['input_image_analysis']['user_description']}\n")
                
                price_data = results['input_image_analysis']['price_data']
                if price_data:
                    f.write(f"Product Name: {price_data.product_name}\n")
                    f.write(f"Initial Price: {price_data.initial_price}\n")
                    f.write(f"Collateral Price: {price_data.collateral_price}\n")
                    f.write(f"Currency: {price_data.currency}\n")
                    f.write(f"Marketplace: {price_data.marketplace}\n")
                    f.write(f"Confidence: {price_data.confidence}\n")
                    
                    if hasattr(price_data, 'additional_info') and price_data.additional_info:
                        f.write(f"\nCollateral Value Explanation:\n{price_data.additional_info}\n")
                else:
                    f.write("Price calculation failed\n")
                
                f.write("\n" + "=" * 50 + "\n\n")
                
                # Similar images
                f.write(f"SIMILAR IMAGES ({len(results['similar_images_analysis'])}):\n\n")
                for i, img in enumerate(results['similar_images_analysis']):
                    combined_info = img['combined_info']
                    f.write(f"Similar Image {i+1}:\n")
                    f.write(f"  Name: {combined_info['name']}\n")
                    f.write(f"  Type: {combined_info['type']}\n")
                    f.write(f"  Description: {combined_info['user_description']}\n")
                    f.write(f"  Similarity Score: {combined_info['similarity_score']:.3f}\n")
                    f.write(f"  Initial Price: {combined_info['initial_price']}\n")
                    f.write(f"  Collateral Price: {combined_info['collateral_price']}\n")
                    f.write(f"  Currency: {combined_info['currency']}\n")
                    f.write(f"  Marketplace: {combined_info['marketplace']}\n")
                    f.write(f"  Confidence: {combined_info['confidence']}\n")
                    f.write("\n")
                
                # Summary
                summary = results['summary']
                f.write("SUMMARY:\n")
                f.write(f"Total Images: {summary['total_images_processed']}\n")
                f.write(f"Successful Calculations: {summary['successful_price_calculations']}\n")
                f.write(f"Success Rate: {summary['success_rate']}\n")
            
            print(f"✅ Results saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return ""
    
    @staticmethod
    def save_to_json_file(results: Dict, image_path: str, filename: str = None) -> str:
        """Save results to a JSON file"""
        try:
            if not filename:
                image_name = Path(image_path).stem
                timestamp = str(int(time.time()))
                filename = f"rag3_llampi_results_{image_name}_{timestamp}.json"
            
            integrator = RAG3LLAMPIIntegrator(verbose=False)
            json_results = integrator._convert_results_to_json(results)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ JSON results saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving JSON results: {e}")
            return ""


def interactive_mode():
    """Interactive mode for user input"""
    print("=== RAG3-LLAMPI Interactive Mode ===")
    
    # Get input image path
    while True:
        image_path = input("\n📁 Enter the path to your image: ").strip()
        if os.path.exists(image_path):
            break
        else:
            print("❌ File not found. Please enter a valid path.")
    
    # Get user description
    description = input("\n📝 Enter a description of your image (optional): ").strip()
    
    # Get number of similar images
    while True:
        try:
            top_k = int(input("\n🔢 How many similar images to find? (1-10): ").strip())
            if 1 <= top_k <= 10:
                break
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\n🚀 Starting analysis...")
    print(f"Image: {image_path}")
    print(f"Description: {description or 'None provided'}")
    print(f"Finding {top_k} similar images...")
    
    try:
        integrator = RAG3LLAMPIIntegrator(verbose=True)
        results = integrator.integrate(
            input_image_path=image_path,
            user_description=description,
            top_k=top_k
        )
        
        if "error" not in results:
            print("\n🎉 Analysis completed successfully!")
            
            # Ask if user wants to save results
            save_results = input("\n💾 Would you like to save results to a file? (y/n): ").strip().lower()
            if save_results in ['y', 'yes']:
                save_format = input("📁 Save as: (1) Text file, (2) JSON file, or (3) Both? Enter 1, 2, or 3: ").strip()
                
                if save_format == "1":
                    ResultsManager.save_to_text_file(results, image_path)
                elif save_format == "2":
                    ResultsManager.save_to_json_file(results, image_path)
                elif save_format == "3":
                    ResultsManager.save_to_text_file(results, image_path)
                    ResultsManager.save_to_json_file(results, image_path)
                else:
                    print("❌ Invalid choice. Saving as text file.")
                    ResultsManager.save_to_text_file(results, image_path)
        else:
            print(f"\n❌ Analysis failed: {results['error']}")
            
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")


def example_usage():
    """Example usage of the integration functions"""
    input_image_path = "rolex.jpeg"  # Use local image
    user_description = "Vintage luxury timepiece from the 1980s, perfect for collateral"
    
    print("=== RAG3-LLAMPI Integration Example ===")
    print(f"Input Image: {input_image_path}")
    print(f"User Description: {user_description}")
    
    try:
        integrator = RAG3LLAMPIIntegrator(verbose=True)
        results = integrator.integrate(
            input_image_path=input_image_path,
            user_description=user_description,
            top_k=3
        )
        
        if "error" not in results:
            print("\n🎉 Integration completed successfully!")
            print(f"Results returned: {len(results)} main sections")
            
            # Access specific parts of the results
            print(f"\nInput image price: {results['input_image_analysis']['analysis_summary']['price_range']}")
            print(f"Similar images found: {results['summary']['similar_images_found']}")
            
        else:
            print(f"\n❌ Integration failed: {results['error']}")
            
    except Exception as e:
        print(f"\n❌ Example failed: {e}")


if __name__ == "__main__":
    print("RAG3-LLAMPI Integration Tool")
    print("=" * 40)
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_mode()
        elif sys.argv[1] == "--example":
            example_usage()
        elif sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python rag3_llampi_integration.py                    # Run example")
            print("  python rag3_llampi_integration.py --interactive     # Interactive mode")
            print("  python rag3_llampi_integration.py --example         # Run example")
            print("  python rag3_llampi_integration.py --help            # Show this help")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Default: run example with local rolex.jpeg
        if os.path.exists("rolex.jpeg"):
            example_usage()
        else:
            print("❌ rolex.jpeg not found in current directory")
            print("Please place an image file named 'rolex.jpeg' in the current directory")
            print("Or use --interactive mode to specify a different image path")
