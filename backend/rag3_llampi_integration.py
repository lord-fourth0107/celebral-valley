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
from typing import Dict, List, Optional
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from rag3 import ImageRAGSystem
    from llmapi import AnthropicClient, ProductPriceResult
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure rag3.py and llmapi.py are in the same directory")
    sys.exit(1)


def integrate_rag3_with_llampi(input_image_path: str, 
                              user_description: str = "",
                              top_k: int = 3,
                              score_threshold: float = 0.0,
                              verbose: bool = True,
                              return_json: bool = False) -> Dict:
    """
    Integrate rag3 with llampi to process images through RAG system and calculate prices
    
    Args:
        input_image_path: Path to the input image
        user_description: User's description of the input image
        top_k: Number of similar images to find
        score_threshold: Minimum similarity score threshold
        verbose: Whether to print detailed progress information
        
    Returns:
        Dictionary containing:
        - input_image_analysis: Analysis and price for input image
        - similar_images_analysis: List of similar images with prices
        - summary: Summary of all findings
    """
    if verbose:
        print("=" * 80)
        print("🔄 INTEGRATING RAG3 WITH LLAMPI")
        print("=" * 80)
    
    try:
        # Step 1: Initialize RAG3 system
        if verbose:
            print("\n📊 Step 1: Initializing RAG3 system...")
        print("   Loading CLIP model and connecting to Qdrant...")
        rag_system = ImageRAGSystem()
        print("   ✅ RAG3 system initialized successfully")
        
        # Step 2: Find similar images using RAG3
        if verbose:
            print(f"\n🔍 Step 2: Finding {top_k} similar images...")
        print(f"   Processing image: {input_image_path}")
        print("   Extracting embeddings and searching database...")
        print("   ⏳ This may take a few minutes on first run...")
        
        try:
            similar_images = rag_system.find_similar_images(
                input_image_path, 
                top_k=top_k, 
                score_threshold=score_threshold
            )
            print("   ✅ Database search completed")
        except Exception as e:
            print(f"   ❌ Database search failed: {e}")
            raise
        
        if verbose:
            print(f"✅ Found {len(similar_images)} similar images")
        
        # Step 3: Initialize LLM API client
        if verbose:
            print("\n🤖 Step 3: Initializing LLM API client...")
        print("   Initializing Anthropic client...")
        try:
            llm_client = AnthropicClient()
            print("   ✅ LLM API client initialized successfully")
        except Exception as e:
            error_msg = f"Could not initialize LLM API client: {e}"
            if verbose:
                print(f"❌ {error_msg}")
            return {"error": error_msg}
        
        # Step 4: Analyze input image and get price
        if verbose:
            print(f"\n💰 Step 4: Analyzing input image and calculating price...")
            print(f"Input image: {input_image_path}")
            print(f"User description: {user_description}")
        
        try:
            print("   🔍 Analyzing image with Claude...")
            print("   ⏳ This may take 1-2 minutes for API calls...")
            input_image_price = llm_client.search_product_price_from_image(
                input_image_path, 
                additional_context=user_description
            )
            print(f"   ✅ Input image price calculated: {input_image_price.initial_price}")
            print(f"   💰 Collateral value: {input_image_price.collateral_price}")
        except Exception as e:
            print(f"   ❌ Error calculating input image price: {e}")
            input_image_price = None
        
        # Step 5: Analyze similar images and get prices
        if verbose:
            print(f"\n🔍 Step 5: Analyzing {len(similar_images)} similar images and calculating prices...")
        similar_images_analysis = []
        
        for i, similar_img in enumerate(similar_images):
            if verbose:
                print(f"\n--- Processing Similar Image {i+1}/{len(similar_images)} ---")
                print(f"Name: {similar_img['name']}")
                print(f"Type: {similar_img['type']}")
                print(f"User Description: {similar_img['user_description']}")
                print(f"Similarity Score: {similar_img['score']:.3f}")
            
            try:
                # Get price for similar image using its description
                similar_img_price = llm_client.get_price_range_from_description(
                    similar_img['detailed_description'],
                    search_context=f"Similar to {similar_img['name']}, {similar_img['user_description']}"
                )
                
                # Combine RAG3 data with price data
                combined_analysis = {
                    'rag3_data': similar_img,
                    'price_data': similar_img_price,
                    'combined_info': {
                        'name': similar_img['name'],
                        'type': similar_img['type'],
                        'user_description': similar_img['user_description'],
                        'detailed_description': similar_img['detailed_description'],
                        'similarity_score': similar_img['score'],
                        'initial_price': similar_img_price.initial_price,
                        'collateral_price': similar_img_price.collateral_price,
                        'price_range': similar_img_price.price_range,  # For backward compatibility
                        'currency': similar_img_price.currency,
                        'marketplace': similar_img_price.marketplace,
                        'confidence': similar_img_price.confidence,
                        'additional_info': similar_img_price.additional_info
                    }
                }
                
                similar_images_analysis.append(combined_analysis)
                if verbose:
                    print(f"✅ Price calculated: {similar_img_price.price_range}")
                
            except Exception as e:
                if verbose:
                    print(f"❌ Error calculating price for similar image {i+1}: {e}")
                # Add image without price data
                combined_analysis = {
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
                        'price_range': 'Price calculation failed',  # For backward compatibility
                        'currency': 'Unknown',
                        'marketplace': 'Unknown',
                        'confidence': 'low',
                        'additional_info': f'Error: {str(e)}'
                    }
                }
                similar_images_analysis.append(combined_analysis)
        
        # Step 6: Prepare results
        if verbose:
            print(f"\n📋 Step 6: Preparing final results...")
        
        # Input image analysis
        input_image_analysis = {
            'image_path': input_image_path,
            'user_description': user_description,
            'price_data': input_image_price,
            'analysis_summary': {
                'name': input_image_price.product_name if input_image_price else 'Unknown',
                'initial_price': input_image_price.initial_price if input_image_price else 'Price calculation failed',
                'collateral_price': input_image_price.collateral_price if input_image_price else 'Price calculation failed',
                'price_range': input_image_price.price_range if input_image_price else 'Price calculation failed',  # For backward compatibility
                'currency': input_image_price.currency if input_image_price else 'Unknown',
                'marketplace': input_image_price.marketplace if input_image_price else 'Unknown',
                'confidence': input_image_price.confidence if input_image_price else 'low'
            }
        }
        
        # Summary statistics
        total_images = len(similar_images_analysis) + 1  # +1 for input image
        successful_price_calculations = sum(1 for img in similar_images_analysis if img['price_data'] is not None)
        if input_image_price:
            successful_price_calculations += 1
        
        summary = {
            'total_images_processed': total_images,
            'successful_price_calculations': successful_price_calculations,
            'failed_price_calculations': total_images - successful_price_calculations,
            'success_rate': f"{(successful_price_calculations/total_images)*100:.1f}%",
            'input_image_found': input_image_price is not None,
            'similar_images_found': len(similar_images_analysis)
        }
        
        # Final results
        results = {
            'input_image_analysis': input_image_analysis,
            'similar_images_analysis': similar_images_analysis,
            'summary': summary
        }
        
        # Step 7: Print comprehensive results if verbose
        if verbose:
            _print_comprehensive_results(results, input_image_path, user_description)
        
        # Return JSON if requested, otherwise return the regular results
        if return_json:
            return _convert_results_to_json(results)
        else:
            return results
        
    except Exception as e:
        error_msg = f"Error in rag3-llampi integration: {str(e)}"
        if verbose:
            print(f"\n❌ {error_msg}")
        return {"error": error_msg}


def _print_comprehensive_results(results: Dict, input_image_path: str, user_description: str):
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
        
        # Display brief collateral value explanation
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
        
        # No detailed analysis display for similar images - keep it clean and focused
    
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


def quick_price_check(image_path: str, description: str = "") -> Optional[ProductPriceResult]:
    """
    Quick function to just get price for a single image without RAG search
    
    Args:
        image_path: Path to the image
        description: Optional description
        
    Returns:
        ProductPriceResult or None if failed
    """
    try:
        llm_client = AnthropicClient()
        return llm_client.search_product_price_from_image(image_path, description)
    except Exception as e:
        print(f"Quick price check failed: {e}")
        return None


def find_similar_only(image_path: str, top_k: int = 3) -> List[Dict]:
    """
    Find similar images only, without price calculation
    
    Args:
        image_path: Path to the input image
        top_k: Number of similar images to find
        
    Returns:
        List of similar images with RAG3 data
    """
    try:
        rag_system = ImageRAGSystem()
        return rag_system.find_similar_images(image_path, top_k=top_k)
    except Exception as e:
        print(f"Similar image search failed: {e}")
        return []


def example_usage():
    """Example usage of the integration functions"""
    
    # Example input image path - change this to your actual image
    input_image_path = "/Users/yashavikasingh/Documents/Screenshot 2025-08-23 at 17.51.01.png"
    
    # Example user description
    user_description = "This is my iphone 13, it's three years old"
    
    print("=== RAG3-LLAMPI Integration Example ===")
    print(f"Input Image: {input_image_path}")
    print(f"User Description: {user_description}")
    
    try:
        # Run the full integration
        results = integrate_rag3_with_llampi(
            input_image_path=input_image_path,
            user_description=user_description,
            top_k=3,
            score_threshold=0.0,
            verbose=True
        )
        
        if "error" not in results:
            print("\n🎉 Integration completed successfully!")
            print(f"Results returned: {len(results)} main sections")
            
            # You can access specific parts of the results:
            print(f"\nInput image price: {results['input_image_analysis']['analysis_summary']['price_range']}")
            print(f"Similar images found: {results['summary']['similar_images_found']}")
            
        else:
            print(f"\n❌ Integration failed: {results['error']}")
            
    except Exception as e:
        print(f"\n❌ Example failed: {e}")


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
        results = integrate_rag3_with_llampi(
            input_image_path=image_path,
            user_description=description,
            top_k=top_k,
            verbose=True
        )
        
        if "error" not in results:
            print("\n🎉 Analysis completed successfully!")
            
            # Ask if user wants to save results
            save_results = input("\n💾 Would you like to save results to a file? (y/n): ").strip().lower()
            if save_results in ['y', 'yes']:
                save_format = input("📁 Save as: (1) Text file, (2) JSON file, or (3) Both? Enter 1, 2, or 3: ").strip()
                
                if save_format == "1":
                    _save_results_to_file(results, image_path)
                elif save_format == "2":
                    _save_results_to_json(results, image_path)
                elif save_format == "3":
                    _save_results_to_file(results, image_path)
                    _save_results_to_json(results, image_path)
                else:
                    print("❌ Invalid choice. Saving as text file.")
                    _save_results_to_file(results, image_path)
        else:
            print(f"\n❌ Analysis failed: {results['error']}")
            
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")


def _save_results_to_file(results: Dict, image_path: str):
    """Save results to a text file"""
    try:
        # Create filename based on image path
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
                
                # Save collateral value explanation for input image
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
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")


def _save_results_to_json(results: Dict, image_path: str):
    """Save results to a JSON file"""
    try:
        # Create filename based on image path
        image_name = Path(image_path).stem
        timestamp = str(int(time.time()))
        filename = f"rag3_llampi_results_{image_name}_{timestamp}.json"
        
        # Convert results to JSON-serializable format
        json_results = _convert_results_to_json(results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON results saved to: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error saving JSON results: {e}")
        return None


def _convert_results_to_json(results: Dict) -> Dict:
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
            
            if hasattr(price_data, 'additional_info') and price_data.additional_info:
                # Get the brief collateral value explanation
                collateral_explanation = price_data.additional_info
            
            json_results['input_image_analysis']['price_data'] = {
                'product_name': price_data.product_name,
                'initial_price': price_data.initial_price,
                'collateral_price': price_data.collateral_price,
                'price_range': price_data.price_range,  # For backward compatibility
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
                'price_range': combined_info['price_range'],  # For backward compatibility
                'currency': combined_info['currency'],
                'marketplace': combined_info['marketplace'],
                'confidence': combined_info['confidence']
            }
            
            # No additional_info for similar images - keep JSON clean
            json_results['similar_images_analysis'].append(json_img)
        
        # Add summary
        json_results['summary'] = results['summary']
        
        # Add metadata
        json_results['metadata'] = {
            'timestamp': str(int(time.time())),
            'version': '1.0',
            'integration_type': 'RAG3-LLAMPI'
        }
        
        return json_results
        
    except Exception as e:
        print(f"❌ Error converting results to JSON: {e}")
        return {"error": f"Failed to convert results to JSON: {str(e)}"}


def get_results_as_json(results: Dict) -> str:
    """Get results as a JSON string"""
    try:
        json_results = _convert_results_to_json(results)
        return json.dumps(json_results, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Failed to convert results to JSON: {str(e)}"})


def save_results_to_json(results: Dict, image_path: str) -> Optional[str]:
    """Save results to JSON file - convenience function"""
    return _save_results_to_json(results, image_path)


def get_json_results(input_image_path: str, 
                    user_description: str = "",
                    top_k: int = 3,
                    score_threshold: float = 0.0) -> Dict:
    """
    Get results directly as JSON data (no file saving, no verbose output)
    
    Args:
        input_image_path: Path to the input image
        user_description: User's description of the input image
        top_k: Number of similar images to find
        score_threshold: Minimum similarity score threshold
        
    Returns:
        JSON-formatted dictionary with all results
    """
    return integrate_rag3_with_llampi(
        input_image_path=input_image_path,
        user_description=user_description,
        top_k=top_k,
        score_threshold=score_threshold,
        verbose=False,  # No console output
        return_json=True  # Return JSON format
    )


if __name__ == "__main__":
    import time
    
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
        # Default: run example
        json_data = get_json_results("/Users/yashavikasingh/celebral-valley/backend/rolex.jpeg", "Vintage watch from 1980s")
        print(json.dumps(json_data, indent=2))
        # example_usage()
