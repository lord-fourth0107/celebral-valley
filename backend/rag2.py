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
                                     max_tokens: int = 500) -> Dict:
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
                "detailed_description": "Anthropic API key not provided"
            }
        
        try:
            # Convert image to base64
            image_b64 = self.image_to_base64(image)
            
            # Structured prompt for JSON-like output
            if custom_prompt is None:
                custom_prompt = """Analyze this image and provide a structured description in the following format:

                Name: A descriptive, catchy name for the main object/product
                Type: The primary category (e.g., watch, car, furniture, clothing)
                Model Number: If visible, provide the model number, serial number, or product code
                Categories: List of relevant categories like [luxury, collection, daily, vintage, modern, sport, casual, formal, premium, affordable, etc.]
                Detailed Description: A comprehensive description including:
                - Main objects and their characteristics
                - Colors, materials, and visual features
                - Style, brand, or design elements
                - Context or setting
                - Any unique or notable features

                IMPORTANT: Always provide Name, Type, and at least 2-3 categories. If Model Number is not visible, write "Not visible".
                Format your response with clear labels and values."""
            
            # Make API call to Claude
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
            
            response_text = message.content[0].text.strip()
            
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
                "categories": [],
                "detailed_description": response_text
            }
            
            # Try to extract structured information from the response
            lines = response_text.split('\n')
            current_field = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for field indicators with more flexible matching
                line_lower = line.lower()
                
                if 'name:' in line_lower:
                    structured_data["name"] = line.split(':', 1)[1].strip()
                elif 'type:' in line_lower:
                    structured_data["type"] = line.split(':', 1)[1].strip()
                elif 'model number:' in line_lower or 'model:' in line_lower:
                    structured_data["model_number"] = line.split(':', 1)[1].strip()
                elif 'categories:' in line_lower:
                    categories_text = line.split(':', 1)[1].strip()
                    # Try to parse categories (remove brackets, split by comma)
                    categories_text = categories_text.strip('[]')
                    if categories_text:
                        # Split by comma and clean up each category
                        categories = [cat.strip().strip('"').strip("'") for cat in categories_text.split(',') if cat.strip()]
                        structured_data["categories"] = [cat for cat in categories if cat and cat.lower() not in ['unknown', 'not visible']]
                elif 'detailed description:' in line_lower:
                    current_field = "detailed_description"
                    structured_data["detailed_description"] = line.split(':', 1)[1].strip()
                elif current_field == "detailed_description":
                    # Continue building detailed description
                    structured_data["detailed_description"] += " " + line
            
            # Fallback logic for better parsing
            if structured_data["name"] == "Unknown":
                # Try to extract name from the first meaningful line
                for line in lines:
                    line = line.strip()
                    if line and not line.lower().startswith(('name:', 'type:', 'categories:', 'model', 'detailed')):
                        structured_data["name"] = line[:50]  # Take first 50 chars as name
                        break
            
            if structured_data["type"] == "Unknown":
                # Try to infer type from the name or description
                name_lower = structured_data["name"].lower()
                if any(word in name_lower for word in ['watch', 'timepiece', 'clock']):
                    structured_data["type"] = "watch"
                elif any(word in name_lower for word in ['car', 'vehicle', 'automobile']):
                    structured_data["type"] = "car"
                elif any(word in name_lower for word in ['furniture', 'chair', 'table', 'sofa']):
                    structured_data["type"] = "furniture"
                elif any(word in name_lower for word in ['clothing', 'shirt', 'dress', 'jacket']):
                    structured_data["type"] = "clothing"
                else:
                    structured_data["type"] = "product"
            
            # Ensure we have at least some categories
            if not structured_data["categories"]:
                # Generate basic categories based on type
                type_lower = structured_data["type"].lower()
                if type_lower == "watch":
                    structured_data["categories"] = ["accessory", "timepiece", "fashion"]
                elif type_lower == "car":
                    structured_data["categories"] = ["vehicle", "transportation", "automotive"]
                elif type_lower == "furniture":
                    structured_data["categories"] = ["home", "interior", "decor"]
                elif type_lower == "clothing":
                    structured_data["categories"] = ["fashion", "apparel", "style"]
                else:
                    structured_data["categories"] = ["product", "item", "object"]
            
            return structured_data
            
        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            return {
                "name": "Parse error",
                "type": "Unknown",
                "model_number": "Not visible",
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
            
            # Update metadata with structured description and other info
            metadata.update({
                'source': image_source,
                'image_size': image.size,
                'timestamp': str(np.datetime64('now')),
                'structured_description': structured_description if structured_description else {
                    "name": "No description generated",
                    "type": "Unknown",
                    "model_number": "Not visible",
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
                
                # Update metadata
                metadata.update({
                    'source': data['source'],
                    'image_size': image.size,
                    'timestamp': str(np.datetime64('now')),
                    'structured_description': structured_description if structured_description else {
                        "name": "No description generated",
                        "type": "Unknown",
                        "model_number": "Not visible",
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


# Example usage with Claude descriptions
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
        print(similar_images_metadata)
        # print(f"Found {len(similar_images_metadata)} similar images")
        
        # # Print the metadata for each image
        # for i, img in enumerate(similar_images_metadata):
        #     print(f"\n--- Image {i+1} ---")
        #     print(f"Name: {img['name']}")
        #     print(f"Type: {img['type']}")
        #     print(f"Model Number: {img['model_number']}")
        #     print(f"Categories: {img['categories']}")
        #     print(f"Score: {img['score']:.3f}")
        #     print(f"Image Path: {img['image_path']}")
        #     print(f"Base64 Length: {len(img['base64_image'])} characters")
        
        # Return the metadata list for further use
        return similar_images_metadata
        
    except Exception as e:
        print(f"Error: {e}")
        return []


def insert_folder_to_qdrant(folder_path: str, 
                           source_platform: str = "local",
                           generate_descriptions: bool = True,
                           custom_description_prompt: str = None):
    """
    Insert all images from a folder into Qdrant with optional descriptions
    
    Args:
        folder_path: Path to folder containing images
        source_platform: Platform source for all images
        generate_descriptions: Whether to generate descriptions using Claude
        custom_description_prompt: Custom prompt for description generation
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
    print("Starting batch insertion...")
    
    # Prepare batch data
    image_batch = []
    for image_path in image_files:
        image_batch.append({
            'source': image_path,
            'metadata': {'source_platform': source_platform}
        })
    
    try:
        # Batch store with descriptions
        point_ids = rag_system.batch_store_images(
            image_batch, 
            generate_descriptions=generate_descriptions,
            custom_description_prompt=custom_description_prompt
        )
        
        print(f"✅ Successfully stored {len(point_ids)} images in Qdrant")
        print(f"Point IDs: {point_ids}")
        
        # Get collection info
        info = rag_system.get_collection_info()
        print(f"Collection info: {info}")
        
    except Exception as e:
        print(f"Error during batch insertion: {e}")


def example_folder_insertion():
    """Example of inserting a folder of images"""
    
    # Example folder path - change this to your actual folder
    folder_path = "/Users/yashavikasingh/Downloads/images_for_rag"
    
    print("=== Folder Insertion Example ===")
    print(f"Inserting all images from: {folder_path}")
    
    # Insert all images from folder
    insert_folder_to_qdrant(
        folder_path=folder_path,
        source_platform="local_collection",
        generate_descriptions=True,
        custom_description_prompt="Describe this image focusing on the main objects, colors, and visual characteristics for search purposes."
    )


def example_get_structured_descriptions():
    """Example of getting structured descriptions in a variable"""
    
    # Initialize the system
    rag_system = ImageRAGSystem()
    
    # Example query image
    query_image_path = "/Users/yashavikasingh/Documents/casio2.png"
    
    try:
        print("=== Getting Structured Descriptions Example ===")
        
        # Get structured descriptions list in a variable
        structured_descriptions = rag_system.get_structured_descriptions_list(query_image_path)
        
        print(f"Found {len(structured_descriptions)} similar images")
        
        print(structured_descriptions)
    finally:
        print("=== Getting Structured Descriptions Example Completed ===")


if __name__ == "__main__":
    # Run examples
    # example_folder_insertion()  # Uncomment to insert a folder of images
    simple_example()  # Simple example using find_similar_images