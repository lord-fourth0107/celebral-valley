import os
import uuid
import numpy as np
from PIL import Image
import torch
import clip
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import requests
from io import BytesIO
import base64
from typing import List, Dict, Optional
import anthropic
import time

class ImageRAGSystem:
    def __init__(self, 
                 qdrant_host: str = "localhost", 
                 qdrant_port: int = 6333,
                 collection_name: str = "image_embeddings",
                 anthropic_api_key: str = None):
        """
        Initialize the Image RAG System
        
        Args:
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port  
            collection_name: Name of the collection to store embeddings
            anthropic_api_key: Anthropic API key for Claude descriptions
        """
        self.collection_name = collection_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        # Load CLIP model
        self.clip_model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        
        # Get embedding dimension
        self.embedding_dim = 512  # CLIP ViT-B/32 embedding dimension
        
        # Initialize Anthropic client for image descriptions
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        else:
            # Try to get from environment variable
            api_key = os.getenv('ANTHROPIC_API_KEY')
            print(f"api_key: {api_key}")
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            else:
                self.anthropic_client = None
                print("Warning: No Anthropic API key provided. Image descriptions will not be generated.")
        
        # Create collection if it doesn't exist
        self._create_collection()
    
    def _create_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                
        except Exception as e:
            raise
    
    def load_image(self, image_source: str) -> Image.Image:
        """
        Load image from various sources
        
        Args:
            image_source: Can be local file path, URL, or base64 string
            
        Returns:
            PIL Image object
        """
        try:
            # Check if it's a URL
            if image_source.startswith(('http://', 'https://')):
                response = requests.get(image_source)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            
            # Check if it's base64
            elif image_source.startswith('data:image'):
                # Handle data URI format
                base64_data = image_source.split(',')[1]
                image_data = base64.b64decode(base64_data)
                image = Image.open(BytesIO(image_data))
            
            # Assume it's a local file path
            else:
                image = Image.open(image_source)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            return image
            
        except Exception as e:
            raise
    
    def image_to_base64(self, image: Image.Image, format: str = "PNG") -> str:
        """
        Convert PIL Image to base64 string for API calls
        
        Args:
            image: PIL Image object
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Base64 encoded image string
        """
        try:
            buffered = BytesIO()
            image.save(buffered, format=format)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except Exception as e:
            raise Exception(f"Error converting image to base64: {e}")
    
    def generate_structured_description(self, image: Image.Image, 
                                     custom_prompt: str = None,
                                     max_tokens: int = 600) -> Dict:
        """
        Generate structured image description using Claude API
        
        Args:
            image: PIL Image object
            custom_prompt: Optional custom prompt for description generation
            max_tokens: Maximum tokens for the description
            
        Returns:
            Dictionary with structured description fields
        """
        if not self.anthropic_client:
            return {
                "name": "Description unavailable",
                "type": "Unknown",
                "categories": [],
                "user_description": "Anthropic API key not provided",
                "detailed_description": "Anthropic API key not provided"
            }
        
        try:
            # Convert image to base64
            image_b64 = self.image_to_base64(image)
            
            # Improved structured prompt for better parsing
            if custom_prompt is None:
                custom_prompt = """Analyze this image and provide a structured description. Please format your response with EXACTLY these labels and structure:

NAME: [A short, descriptive name for the main object/product]

TYPE: [The primary category like watch, phone, bag, car, furniture, etc.]

MODEL_NUMBER: [If visible, provide model number/serial number, otherwise write "Not visible"]

USER_DESCRIPTION: [Write exactly ONE sentence that sounds like a user describing their item, including approximate age/era. Examples: "This is my vintage Casio watch from the 1990s", "This is a modern iPhone 15 from 2023", "This is my leather bag that's about 2 years old", "This is a classic car from the 1960s"]

CATEGORIES: [List 3-4 relevant categories separated by commas, like: vintage, luxury, daily-use, electronics]

DETAILED_DESCRIPTION: [Write a comprehensive description including colors, materials, condition, brand elements, and unique features]

Please follow this exact format with these exact labels. Make the USER_DESCRIPTION sound natural and personal, as if the owner is describing it."""
            
            # Make API call to Claude with retry logic
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    message = self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=max_tokens,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": image_b64
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": custom_prompt
                                    }
                                ]
                            }
                        ]
                    )
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    if attempt < max_retries - 1:  # Not the last attempt
                        print(f"API call attempt {attempt + 1} failed: {e}")
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        # Last attempt failed, raise the exception
                        raise e
            
            response_text = message.content[0].text.strip()
            print(f"Claude Response:\n{response_text}\n")  # Debug print
            
            # Parse the response to extract structured information
            structured_data = self._parse_claude_response(response_text)
            
            # Add base64 image to the structured data
            structured_data["base64_image"] = image_b64
            
            return structured_data
            
        except Exception as e:
            print(f"Error generating structured description with Claude: {e}")
            return {
                "name": "Description generation failed",
                "type": "Unknown",
                "categories": [],
                "user_description": f"Error generating description: {str(e)}",
                "detailed_description": f"Error: {str(e)}",
                "base64_image": self.image_to_base64(image) if 'image' in locals() else ""
            }
    
    def _parse_claude_response(self, response_text: str) -> Dict:
        """
        Parse Claude's response to extract structured information
        
        Args:
            response_text: Raw response from Claude
            
        Returns:
            Parsed structured data
        """
        try:
            # Initialize default values
            structured_data = {
                "name": "Unknown",
                "type": "Unknown", 
                "model_number": "Not visible",
                "user_description": "Unknown item",
                "categories": [],
                "detailed_description": response_text
            }
            
            # Split response into lines for processing
            lines = response_text.split('\n')
            current_field = None
            detailed_description_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                line_upper = line.upper()
                
                # Check for field indicators with exact matching
                if line_upper.startswith('NAME:'):
                    structured_data["name"] = line.split(':', 1)[1].strip()
                    current_field = None
                    
                elif line_upper.startswith('TYPE:'):
                    structured_data["type"] = line.split(':', 1)[1].strip()
                    current_field = None
                    
                elif line_upper.startswith('MODEL_NUMBER:') or line_upper.startswith('MODEL NUMBER:'):
                    structured_data["model_number"] = line.split(':', 1)[1].strip()
                    current_field = None
                    
                elif line_upper.startswith('USER_DESCRIPTION:') or line_upper.startswith('USER DESCRIPTION:'):
                    structured_data["user_description"] = line.split(':', 1)[1].strip()
                    current_field = None
                    
                elif line_upper.startswith('CATEGORIES:'):
                    categories_text = line.split(':', 1)[1].strip()
                    # Parse categories (remove brackets if present, split by comma)
                    categories_text = categories_text.strip('[]')
                    if categories_text:
                        categories = [cat.strip().strip('"').strip("'") for cat in categories_text.split(',') if cat.strip()]
                        structured_data["categories"] = [cat for cat in categories if cat and cat.lower() not in ['unknown', 'not visible']]
                    current_field = None
                    
                elif line_upper.startswith('DETAILED_DESCRIPTION:') or line_upper.startswith('DETAILED DESCRIPTION:'):
                    detailed_desc_start = line.split(':', 1)[1].strip()
                    if detailed_desc_start:
                        detailed_description_lines = [detailed_desc_start]
                    current_field = "detailed_description"
                    
                elif current_field == "detailed_description":
                    # Continue building detailed description
                    detailed_description_lines.append(line)
            
            # Join detailed description lines
            if detailed_description_lines:
                structured_data["detailed_description"] = " ".join(detailed_description_lines)
            
            # Clean up the fields
            structured_data["name"] = structured_data["name"].strip('[]"\'')
            structured_data["type"] = structured_data["type"].strip('[]"\'')
            structured_data["model_number"] = structured_data["model_number"].strip('[]"\'')
            structured_data["user_description"] = structured_data["user_description"].strip('[]"\'')
            
            # Fallback processing if fields are still empty
            if structured_data["name"] == "Unknown" or not structured_data["name"]:
                # Try to extract from the first meaningful content
                for line in lines:
                    line = line.strip()
                    if line and not any(field in line.upper() for field in ['NAME:', 'TYPE:', 'MODEL:', 'USER:', 'CATEGORIES:', 'DETAILED:']):
                        structured_data["name"] = line[:50]  # Take first 50 chars as name
                        break
            
            # Ensure we have basic categories if none were found
            if not structured_data["categories"]:
                type_lower = structured_data["type"].lower()
                if any(word in type_lower for word in ["watch", "timepiece"]):
                    structured_data["categories"] = ["accessory", "timepiece", "fashion"]
                elif any(word in type_lower for word in ["phone", "smartphone"]):
                    structured_data["categories"] = ["electronics", "mobile", "technology"]
                elif any(word in type_lower for word in ["bag", "purse", "backpack"]):
                    structured_data["categories"] = ["accessory", "fashion", "storage"]
                elif any(word in type_lower for word in ["car", "vehicle"]):
                    structured_data["categories"] = ["vehicle", "transportation", "automotive"]
                else:
                    structured_data["categories"] = ["product", "item", "object"]
            
            # Ensure user_description is not the fallback programmatic one
            if structured_data["user_description"] in ["Unknown item", "Unknown product"] or not structured_data["user_description"]:
                # If Claude didn't provide a good user description, create a generic one
                structured_data["user_description"] = f"This is a {structured_data['type'].lower()} with distinctive characteristics"
            
            print(f"Parsed structured data: {structured_data}")  # Debug print
            
            return structured_data
            
        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            return {
                "name": "Parse error",
                "type": "Unknown",
                "model_number": "Not visible", 
                "user_description": "Error parsing product description",
                "categories": ["error", "unknown"],
                "detailed_description": response_text
            }
    
    def extract_embeddings(self, image: Image.Image) -> np.ndarray:
        """
        Extract CLIP embeddings from an image
        
        Args:
            image: PIL Image object
            
        Returns:
            Numpy array of embeddings
        """
        try:
            # Preprocess image
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_tensor)
                
            # Normalize embeddings
            image_features = image_features / image_features.norm(dim=1, keepdim=True)
            
            # Convert to numpy
            embeddings = image_features.cpu().numpy().flatten()
            
            return embeddings
            
        except Exception as e:
            raise
    
    def store_image(self, 
                   image_source: str, 
                   metadata: Dict = None, 
                   point_id: str = None,
                   generate_description: bool = True,
                   custom_description_prompt: str = None,
                   skip_duplicates: bool = True) -> str:
        """
        Store image embeddings in Qdrant with optional Claude-generated description
        
        Args:
            image_source: Image source (file path, URL, or base64)
            metadata: Additional metadata to store with the image
            point_id: Optional custom point ID
            generate_description: Whether to generate description using Claude
            custom_description_prompt: Custom prompt for description generation
            skip_duplicates: Whether to skip storing if image already exists
            
        Returns:
            Point ID of stored embedding, or None if skipped
        """
        try:
            # Check if image already exists
            if skip_duplicates and self.image_exists(image_source):
                print(f"Image already exists in database: {image_source}")
                return None
            
            # Generate point ID if not provided
            if point_id is None:
                point_id = str(uuid.uuid4())
            
            # Load and process image
            image = self.load_image(image_source)
            embeddings = self.extract_embeddings(image)
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Generate structured description using Claude if requested
            structured_description = None
            if generate_description:
                print("Generating structured image description with Claude...")
                structured_description = self.generate_structured_description(
                    image, 
                    custom_prompt=custom_description_prompt
                )
                print(f"Generated structured description: {structured_description['name']} - {structured_description['type']}")
                print(f"User description: {structured_description['user_description']}")
            
            # Update metadata with structured description and other info
            metadata.update({
                'source': image_source,
                'image_size': image.size,
                'timestamp': str(np.datetime64('now')),
                'structured_description': structured_description if structured_description else {
                    "name": "No description generated",
                    "type": "Unknown",
                    "model_number": "Not visible",
                    "user_description": "No description available",
                    "categories": ["unknown"],
                    "detailed_description": "No description available",
                    "base64_image": ""
                }
            })
            
            # Create point
            point = PointStruct(
                id=point_id,
                vector=embeddings.tolist(),
                payload=metadata
            )
            
            # Store in Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            return point_id
            
        except Exception as e:
            raise
    
    def batch_store_images(self, 
                          image_data: List[Dict], 
                          generate_descriptions: bool = True,
                          custom_description_prompt: str = None) -> List[str]:
        """
        Store multiple images in batch with optional Claude-generated descriptions
        
        Args:
            image_data: List of dicts with 'source', 'metadata', and optional 'id' keys
            generate_descriptions: Whether to generate descriptions using Claude
            custom_description_prompt: Custom prompt for description generation
            
        Returns:
            List of point IDs
        """
        try:
            points = []
            point_ids = []
            
            for i, data in enumerate(image_data):
                print(f"Processing image {i+1}/{len(image_data)}: {data['source']}")
                
                # Generate point ID if not provided
                point_id = data.get('id', str(uuid.uuid4()))
                point_ids.append(point_id)
                
                # Check if image already exists
                if self.image_exists(data['source']):
                    print(f"Skipping duplicate image: {data['source']}")
                    continue
                
                # Load and process image
                image = self.load_image(data['source'])
                embeddings = self.extract_embeddings(image)
                
                # Prepare metadata
                metadata = data.get('metadata', {})
                
                # Generate structured description using Claude if requested
                structured_description = None
                if generate_descriptions:
                    print(f"Generating structured description for image {i+1}...")
                    structured_description = self.generate_structured_description(
                        image, 
                        custom_prompt=custom_description_prompt
                    )
                    print(f"Structured description generated: {structured_description['name']} - {structured_description['type']}")
                    print(f"User description: {structured_description['user_description']}")
                
                # Update metadata
                metadata.update({
                    'source': data['source'],
                    'image_size': image.size,
                    'timestamp': str(np.datetime64('now')),
                    'structured_description': structured_description if structured_description else {
                        "name": "No description generated",
                        "type": "Unknown",
                        "model_number": "Not visible",
                        "user_description": "No description available",
                        "categories": ["unknown"],
                        "detailed_description": "No description available",
                        "base64_image": ""
                    }
                })
                
                # Create point
                point = PointStruct(
                    id=point_id,
                    vector=embeddings.tolist(),
                    payload=metadata
                )
                points.append(point)
            
            # Batch upsert
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            return point_ids
            
        except Exception as e:
            raise
    
    def find_similar_images(self, 
                          query_image_source: str, 
                          top_k: int = 3,
                          score_threshold: float = 0.0,
                          exclude_query_image: bool = True) -> List[Dict]:
        """
        Find similar images in the vector database
        
        Args:
            query_image_source: Source of query image
            top_k: Number of similar images to return (default: 3)
            score_threshold: Minimum similarity score threshold
            exclude_query_image: Whether to exclude the query image from results
            
        Returns:
            List of similar images with scores, structured descriptions, and base64 images
        """
        try:
            # Check if collection is empty
            collection_info = self.get_collection_info()
            if collection_info.get('vectors_count', 0) == 0:
                raise ValueError("Vector database is empty. Please store some images before searching.")
            
            # Load and process query image
            query_image = self.load_image(query_image_source)
            query_embeddings = self.extract_embeddings(query_image)
            
            # Search in Qdrant with more results to account for filtering
            search_limit = top_k + 1 if exclude_query_image else top_k
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embeddings.tolist(),
                limit=search_limit,
                score_threshold=score_threshold,
                with_payload=True
            )
            
            # Format results with structured descriptions and base64 images
            results = []
            seen_images = set()  # Track seen images to avoid duplicates
            
            for result in search_results:
                # Skip the query image if exclude_query_image is True
                if exclude_query_image and result.payload.get('source') == query_image_source:
                    continue
                
                # Get image path and check for duplicates
                image_path = result.payload.get('source', '')
                if image_path in seen_images:
                    continue  # Skip duplicate images
                
                seen_images.add(image_path)
                
                # Get structured description from metadata
                structured_desc = result.payload.get('structured_description', {})
                
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'image_path': image_path,
                    'name': structured_desc.get('name', 'Unknown'),
                    'type': structured_desc.get('type', 'Unknown'),
                    'model_number': structured_desc.get('model_number', 'Not visible'),
                    'user_description': structured_desc.get('user_description', 'Unknown product'),
                    'categories': structured_desc.get('categories', []),
                    'detailed_description': structured_desc.get('detailed_description', 'No description available'),
                    'base64_image': structured_desc.get('base64_image', ''),
                    'metadata': result.payload
                })
                
                # Stop if we have enough results
                if len(results) >= top_k:
                    break
            
            return results
            
        except Exception as e:
            raise
    
    def remove_duplicate_images(self) -> Dict:
        """
        Remove duplicate images from the database based on file paths
        
        Returns:
            Dictionary with removal statistics
        """
        try:
            # Get all points from the collection
            all_points = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=1000,  # Adjust based on your collection size
                with_payload=True,
                with_vectors=False
            )
            
            if not all_points[0]:  # No points found
                return {"removed": 0, "total": 0, "message": "No images found"}
            
            # Group by image path to find duplicates
            path_groups = {}
            for point in all_points[0]:
                image_path = point.payload.get('source', '')
                if image_path:
                    if image_path not in path_groups:
                        path_groups[image_path] = []
                    path_groups[image_path].append(point.id)
            
            # Find duplicates (more than one point with same path)
            duplicates = {path: ids for path, ids in path_groups.items() if len(ids) > 1}
            
            if not duplicates:
                return {"removed": 0, "total": len(all_points[0]), "message": "No duplicates found"}
            
            # Remove duplicates (keep the first one, remove the rest)
            removed_count = 0
            for path, ids in duplicates.items():
                # Keep the first ID, remove the rest
                ids_to_remove = ids[1:]
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=ids_to_remove
                )
                removed_count += len(ids_to_remove)
                print(f"Removed {len(ids_to_remove)} duplicate(s) for: {path}")
            
            return {
                "removed": removed_count,
                "total": len(all_points[0]),
                "duplicates_found": len(duplicates),
                "message": f"Removed {removed_count} duplicate images"
            }
            
        except Exception as e:
            print(f"Error removing duplicate images: {e}")
            return {"error": str(e)}
    
    def image_exists(self, image_source: str) -> bool:
        """
        Check if an image already exists in the database
        
        Args:
            image_source: Image source (file path, URL, or base64)
            
        Returns:
            True if image exists, False otherwise
        """
        try:
            # Search for images with the same source path
            all_points = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=1000,
                with_payload=True,
                with_vectors=False
            )
            
            if not all_points[0]:
                return False
            
            # Check if any point has the same source
            for point in all_points[0]:
                if point.payload.get('source') == image_source:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking if image exists: {e}")
            return False
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            return {
                'name': info.config.params.vectors.size,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            return {}
    
    def display_images(self, image_paths: List[str], titles: List[str] = None):
        """
        Display multiple images using PIL
        
        Args:
            image_paths: List of image file paths
            titles: Optional list of titles for each image
        """
        try:
            n_images = len(image_paths)
            if n_images == 0:
                print("No images to display")
                return
            
            print(f"\nDisplaying {n_images} images:")
            print("=" * 60)
            
            for i, img_path in enumerate(image_paths):
                try:
                    # Load and display image info
                    img = Image.open(img_path)
                    title = titles[i] if titles and i < len(titles) else f"Image {i+1}"
                    
                    print(f"\n{title}:")
                    print(f"Path: {img_path}")
                    print(f"Size: {img.size}")
                    print(f"Mode: {img.mode}")
                    
                    # Show image (this will open in your default image viewer)
                    img.show()
                    
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")
            
            print("\n" + "=" * 60)
            print("Images have been opened in your default image viewer.")
            print("Check your desktop/taskbar for opened image windows.")
            
        except Exception as e:
            print(f"Error displaying images: {e}")


# Test function to verify the fix
def test_user_description():
    """Test function to verify that user_description is properly generated by Claude"""
    
    # Initialize the system
    rag_system = ImageRAGSystem()
    
    # Test with a single image
    test_image_path = "/Users/yashavikasingh/Documents/casio2.png"  # Update with your test image
    
    try:
        print("=== Testing User Description Generation ===")
        
        # Load image and generate description
        image = rag_system.load_image(test_image_path)
        structured_desc = rag_system.generate_structured_description(image)
        
        print(f"Name: {structured_desc['name']}")
        print(f"Type: {structured_desc['type']}")
        print(f"Model Number: {structured_desc['model_number']}")
        print(f"User Description: {structured_desc['user_description']}")
        print(f"Categories: {structured_desc['categories']}")
        print(f"Detailed Description: {structured_desc['detailed_description'][:100]}...")
        
        return structured_desc
        
    except Exception as e:
        print(f"Error testing user description: {e}")
        return None


# Example usage with improved user descriptions
def simple_example():
    """Simple example of using find_similar_images to get metadata list"""
    
    # Initialize the system
    rag_system = ImageRAGSystem()
    
    # Example query image
    query_image_path = "/Users/yashavikasingh/Documents/casio2.png"
    
    try:
        print("=== Simple Example: Getting Similar Images Metadata ===")
        
        # Find similar images - this returns the metadata list directly
        similar_images_metadata = rag_system.find_similar_images(query_image_path, top_k=3)
        print(f"Found {len(similar_images_metadata)} similar images")
        
        # Print the metadata for each image
        for i, img in enumerate(similar_images_metadata):
            print(f"\n--- Image {i+1} ---")
            print(f"Name: {img['name']}")
            print(f"Type: {img['type']}")
            print(f"Model Number: {img['model_number']}")
            print(f"User Description: {img['user_description']}")
            print(f"Categories: {img['categories']}")
            print(f"Score: {img['score']:.3f}")
            print(f"Image Path: {img['image_path']}")
            print(f"Base64 Length: {len(img['base64_image'])} characters")
        
        # Return the metadata list for further use
        return similar_images_metadata
        
    except Exception as e:
        print(f"Error: {e}")
        return []


def insert_folder_to_qdrant(folder_path: str, 
                           source_platform: str = "local",
                           generate_descriptions: bool = True,
                           custom_description_prompt: str = None,
                           batch_size: int = 5):
    """
    Insert all images from a folder into Qdrant with optional descriptions
    
    Args:
        folder_path: Path to folder containing images
        source_platform: Platform source for all images
        generate_descriptions: Whether to generate descriptions using Claude
        custom_description_prompt: Custom prompt for description generation
        batch_size: Number of images to process at once (default: 5)
    """
    
    # Initialize the system
    rag_system = ImageRAGSystem()
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    # Get all image files from folder
    image_files = []
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in image_extensions:
                    image_files.append(file_path)
    except Exception as e:
        print(f"Error reading folder {folder_path}: {e}")
        return
    
    if not image_files:
        print(f"No image files found in {folder_path}")
        return
    
    print(f"Found {len(image_files)} images in {folder_path}")
    print(f"Processing in batches of {batch_size} images...")
    
    # Process images in batches
    total_processed = 0
    total_failed = 0
    all_point_ids = []
    
    for i in range(0, len(image_files), batch_size):
        batch_start = i + 1
        batch_end = min(i + batch_size, len(image_files))
        current_batch = image_files[i:batch_end]
        
        print(f"\n--- Processing Batch {batch_start}-{batch_end} of {len(image_files)} ---")
        
        # Prepare batch data
        image_batch = []
        for image_path in current_batch:
            image_batch.append({
                'source': image_path,
                'metadata': {'source_platform': source_platform}
            })
        
        try:
            # Process current batch
            point_ids = rag_system.batch_store_images(
                image_batch, 
                generate_descriptions=generate_descriptions,
                custom_description_prompt=custom_description_prompt
            )
            
            if point_ids:
                all_point_ids.extend(point_ids)
                total_processed += len(point_ids)
                print(f"✅ Batch {batch_start}-{batch_end}: Successfully processed {len(point_ids)} images")
            else:
                print(f"⚠️  Batch {batch_start}-{batch_end}: No images processed")
                
        except Exception as e:
            print(f"❌ Batch {batch_start}-{batch_end}: Error - {e}")
            total_failed += len(current_batch)
            
            # Try processing images individually in this batch
            print(f"🔄 Attempting individual processing for batch {batch_start}-{batch_end}...")
            for image_path in current_batch:
                try:
                    metadata = {'source_platform': source_platform}
                    point_id = rag_system.store_image(
                        image_path, 
                        metadata, 
                        generate_description=generate_descriptions,
                        custom_description_prompt=custom_description_prompt
                    )
                    if point_id:
                        all_point_ids.append(point_id)
                        total_processed += 1
                        print(f"  ✅ Individual: {os.path.basename(image_path)}")
                    else:
                        print(f"  ⚠️  Individual: {os.path.basename(image_path)} - Already exists")
                except Exception as individual_error:
                    print(f"  ❌ Individual: {os.path.basename(image_path)} - {individual_error}")
                    total_failed += 1
        
        # Small delay between batches to avoid overwhelming the API
        if i + batch_size < len(image_files):
            print("⏳ Waiting 2 seconds before next batch...")
            time.sleep(2)
    
    # Final summary
    print(f"\n{'='*60}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Total images found: {len(image_files)}")
    print(f"Successfully processed: {total_processed}")
    print(f"Failed: {total_failed}")
    print(f"Success rate: {(total_processed/len(image_files)*100):.1f}%")
    
    if all_point_ids:
        print(f"Total point IDs: {len(all_point_ids)}")
        
        # Get collection info
        try:
            info = rag_system.get_collection_info()
            print(f"Collection info: {info}")
        except Exception as e:
            print(f"Could not retrieve collection info: {e}")
    
    return all_point_ids


def example_folder_insertion():
    """Example of inserting a folder of images"""
    
    # Example folder path - change this to your actual folder
    folder_path = "/Users/yashavikasingh/Downloads/images_for_rag3"
    
    print("=== Folder Insertion Example ===")
    print(f"Inserting all images from: {folder_path}")
    
    # Insert all images from folder with improved prompt for better user descriptions
    insert_folder_to_qdrant(
        folder_path=folder_path,
        source_platform="local_collection",
        generate_descriptions=True,
        custom_description_prompt=None  # Use the improved default prompt
    )


def integrate_rag3_with_llampi(input_image_path: str, 
                              user_description: str = "",
                              top_k: int = 3,
                              score_threshold: float = 0.0) -> Dict:
    """
    Integrate rag3 with llampi to process images through RAG system and calculate prices
    
    Args:
        input_image_path: Path to the input image
        user_description: User's description of the input image
        top_k: Number of similar images to find
        score_threshold: Minimum similarity score threshold
        
    Returns:
        Dictionary containing:
        - input_image_analysis: Analysis and price for input image
        - similar_images_analysis: List of similar images with prices
        - summary: Summary of all findings
    """
    try:
        print("=" * 80)
        print("🔄 INTEGRATING RAG3 WITH LLAMPI")
        print("=" * 80)
        
        # Step 1: Initialize RAG3 system
        print("\n📊 Step 1: Initializing RAG3 system...")
        rag_system = ImageRAGSystem()
        
        # Step 2: Find similar images using RAG3
        print(f"\n🔍 Step 2: Finding {top_k} similar images...")
        similar_images = rag_system.find_similar_images(
            input_image_path, 
            top_k=top_k, 
            score_threshold=score_threshold
        )
        
        print(f"✅ Found {len(similar_images)} similar images")
        
        # Step 3: Initialize LLM API client
        print("\n🤖 Step 3: Initializing LLM API client...")
        try:
            from llmapi import AnthropicClient
            llm_client = AnthropicClient()
            print("✅ LLM API client initialized successfully")
        except ImportError as e:
            print(f"❌ Error importing llmapi: {e}")
            return {"error": f"Could not import llmapi: {e}"}
        except Exception as e:
            print(f"❌ Error initializing LLM API client: {e}")
            return {"error": f"Could not initialize LLM API client: {e}"}
        
        # Step 4: Analyze input image and get price
        print(f"\n💰 Step 4: Analyzing input image and calculating price...")
        print(f"Input image: {input_image_path}")
        print(f"User description: {user_description}")
        
        try:
            input_image_price = llm_client.search_product_price_from_image(
                input_image_path, 
                additional_context=user_description
            )
            print(f"✅ Input image price calculated: {input_image_price.price_range}")
        except Exception as e:
            print(f"❌ Error calculating input image price: {e}")
            input_image_price = None
        
        # Step 5: Analyze similar images and get prices
        print(f"\n🔍 Step 5: Analyzing {len(similar_images)} similar images and calculating prices...")
        similar_images_analysis = []
        
        for i, similar_img in enumerate(similar_images):
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
                        'price_range': similar_img_price.price_range,
                        'currency': similar_img_price.currency,
                        'marketplace': similar_img_price.marketplace,
                        'confidence': similar_img_price.confidence,
                        'additional_info': similar_img_price.additional_info
                    }
                }
                
                similar_images_analysis.append(combined_analysis)
                print(f"✅ Price calculated: {similar_img_price.price_range}")
                
            except Exception as e:
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
                        'price_range': 'Price calculation failed',
                        'currency': 'Unknown',
                        'marketplace': 'Unknown',
                        'confidence': 'low',
                        'additional_info': f'Error: {str(e)}'
                    }
                }
                similar_images_analysis.append(combined_analysis)
        
        # Step 6: Prepare results
        print(f"\n📋 Step 6: Preparing final results...")
        
        # Input image analysis
        input_image_analysis = {
            'image_path': input_image_path,
            'user_description': user_description,
            'price_data': input_image_price,
            'analysis_summary': {
                'name': input_image_price.product_name if input_image_price else 'Unknown',
                'price_range': input_image_price.price_range if input_image_price else 'Price calculation failed',
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
        
        # Step 7: Print comprehensive results
        print(f"\n{'='*80}")
        print("📊 FINAL RESULTS SUMMARY")
        print(f"{'='*80}")
        
        print(f"\n🎯 INPUT IMAGE ANALYSIS:")
        print(f"   Image: {input_image_path}")
        print(f"   User Description: {user_description}")
        if input_image_price:
            print(f"   Product Name: {input_image_price.product_name}")
            print(f"   Price Range: {input_image_price.price_range}")
            print(f"   Currency: {input_image_price.currency}")
            print(f"   Marketplace: {input_image_price.marketplace}")
            print(f"   Confidence: {input_image_price.confidence}")
        else:
            print(f"   ❌ Price calculation failed")
        
        print(f"\n🔍 SIMILAR IMAGES ANALYSIS ({len(similar_images_analysis)} images):")
        for i, img_analysis in enumerate(similar_images_analysis):
            print(f"\n   --- Similar Image {i+1} ---")
            print(f"   Name: {img_analysis['combined_info']['name']}")
            print(f"   Type: {img_analysis['combined_info']['type']}")
            print(f"   User Description: {img_analysis['combined_info']['user_description']}")
            print(f"   Similarity Score: {img_analysis['combined_info']['similarity_score']:.3f}")
            print(f"   Price Range: {img_analysis['combined_info']['price_range']}")
            print(f"   Currency: {img_analysis['combined_info']['currency']}")
            print(f"   Marketplace: {img_analysis['combined_info']['marketplace']}")
            print(f"   Confidence: {img_analysis['combined_info']['confidence']}")
        
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
        
        return results
        
    except Exception as e:
        error_msg = f"Error in rag3-llampi integration: {str(e)}"
        print(f"\n❌ {error_msg}")
        return {"error": error_msg}


def example_integration():
    """Example usage of the rag3-llampi integration function"""
    
    # Example input image path - change this to your actual image
    input_image_path = "/Users/yashavikasingh/Desktop/hackathon/celebral-valley/backend/rolex.jpeg"
    
    # Example user description
    user_description = "This is my vintage Rolex watch from the 1980s, it's in excellent condition"
    
    print("=== RAG3-LLAMPI Integration Example ===")
    print(f"Input Image: {input_image_path}")
    print(f"User Description: {user_description}")
    
    try:
        # Run the integration
        results = integrate_rag3_with_llampi(
            input_image_path=input_image_path,
            user_description=user_description,
            top_k=3,
            score_threshold=0.0
        )
        
        if "error" not in results:
            print("\n🎉 Integration completed successfully!")
            print(f"Results returned: {len(results)} main sections")
        else:
            print(f"\n❌ Integration failed: {results['error']}")
            
    except Exception as e:
        print(f"\n❌ Example failed: {e}")


if __name__ == "__main__":
    # Run examples
    # example_folder_insertion()  # Uncomment to insert a folder of images
    # simple_example()  # Simple example using find_similar_images
    example_integration()  # Run the integration example