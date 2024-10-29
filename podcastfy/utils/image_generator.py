"""Image Generator Module"""

import os
import asyncio
import json
import uuid
import requests
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import logging
from typing import List, Dict, Tuple, Optional, Any
from podcastfy.utils.config import load_config
import re

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self, gemini_api_key: str, scene_settings: Dict = None, 
                 character_profiles: Dict = None, visual_style: Dict = None,
                 shot_types: List = None):
        """Initialize the ImageGenerator."""
        self.gemini_api_key = gemini_api_key
        self.config = load_config()
        self.flux_api_key = self.config.FLUX_API_KEY
        logger.info(f"Flux API Key: {self.flux_api_key[:5]}...")
        
        # Base seed for consistent image generation
        self.base_seed = 456739965
        
        # Store configurations passed from webhook
        self.scene_settings = scene_settings or {}
        self.character_profiles = character_profiles or {}
        self.visual_style = visual_style or {
            "base_prompt": "high-resolution digital photography",
            "composition": "rule of thirds",
            "lighting": "dramatic lighting"
        }
        self.shot_types = shot_types or []
        
        # Initialize Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest",
            temperature=0.7,
            google_api_key=gemini_api_key
        )
        
        # Ensure images directory exists
        self.images_dir = os.path.join('C:\\', 'appz', 'podcastfy', 'data', 'images')
        os.makedirs(self.images_dir, exist_ok=True)
        logger.info(f"Images directory: {self.images_dir}")

    def _format_prompt(self, description: str) -> str:
        """Format description into Flux-style prompt."""
        return f"{description}, {self.visual_style['base_prompt']} ::8 | {self.visual_style['lighting']} ::7 | {self.visual_style['composition']} ::7 --ar 16:9 --s 1000"

    async def _generate_image(self, scene_index: int, shot_index: int, prompt: str) -> str:
        """Generate a single image using Flux API."""
        try:
            formatted_prompt = self._format_prompt(prompt)
            logger.info(f"Generating image for scene {scene_index + 1}, shot {shot_index + 1}")
            
            # Generate seed based on scene and shot indices
            seed = self.base_seed + (scene_index * 100) + shot_index
            
            url = "https://fal.run/fal-ai/flux/schnell"
            headers = {
                "Authorization": f"Key {self.flux_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "prompt": formatted_prompt,
                "seed": seed
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            image_url = None
            if 'image' in result:
                image_url = result['image']
            elif 'images' in result and result['images']:
                if isinstance(result['images'][0], dict):
                    image_url = result['images'][0].get('url')
                else:
                    image_url = result['images'][0]
            
            if image_url:
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                
                # Use scene and shot indices in filename
                image_id = str(uuid.uuid4())[:8]
                image_file = os.path.join(self.images_dir, f"scene_{scene_index + 1}_shot_{shot_index + 1}_{image_id}.png")
                
                with open(image_file, 'wb') as f:
                    f.write(image_response.content)
                
                metadata = {
                    "scene_index": scene_index,
                    "shot_index": shot_index,
                    "prompt": formatted_prompt,
                    "original_prompt": prompt,
                    "image_url": image_url,
                    "seed": seed,
                    "timestamp": datetime.now().isoformat()
                }
                metadata_file = os.path.join(self.images_dir, f"scene_{scene_index + 1}_shot_{shot_index + 1}_{image_id}.json")
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Generated image for scene {scene_index + 1}, shot {shot_index + 1}")
                return image_file
            else:
                raise Exception("No image URL in response")

        except Exception as e:
            logger.error(f"Error generating image for scene {scene_index + 1}, shot {shot_index + 1}: {str(e)}")
            raise

    async def generate_images(self, transcript: str, dialog_segments: List[Dict[str, Any]]) -> None:
        """Generate images from transcript with dialog segments."""
        try:
            logger.info("Starting image generation...")
            logger.debug(f"Processing {len(dialog_segments)} segments")
            
            tasks = []
            total_images = 0
            
            # Process each scene
            for scene_index, segment in enumerate(dialog_segments):
                logger.debug(f"Processing scene {scene_index + 1}:")
                logger.debug(f"Start time: {segment['start']}")
                logger.debug(f"End time: {segment['end']}")
                logger.debug(f"Number of descriptions: {len(segment.get('scene_descriptions', []))}")
                
                # Process each shot in the scene
                if "scene_descriptions" in segment:
                    for shot_index, description in enumerate(segment["scene_descriptions"]):
                        logger.debug(f"Creating task for scene {scene_index + 1}, shot {shot_index + 1}")
                        task = self._generate_image(
                            scene_index=scene_index,
                            shot_index=shot_index,
                            prompt=description
                        )
                        tasks.append(task)
                        total_images += 1
            
            logger.info(f"Created {len(tasks)} image generation tasks")
            
            # Generate all images concurrently
            image_files = await asyncio.gather(*tasks)
            logger.info(f"Generated {len(image_files)} images")
            
            # Verify image count
            expected_images = sum(len(segment["scene_descriptions"]) for segment in dialog_segments)
            if len(image_files) != expected_images:
                logger.warning(f"Expected {expected_images} images but generated {len(image_files)}")
                raise ValueError(f"Image count mismatch: expected {expected_images}, got {len(image_files)}")

        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            raise

def main():
    """Test the ImageGenerator."""
    try:
        config = load_config()
        generator = ImageGenerator(config.GEMINI_API_KEY)
        
        # Test dialog segments
        dialog_segments = [
            {
                "start": 0.0,
                "end": 15.0,
                "scene_descriptions": [
                    "Detective's office, night. Rain streaks the windows.",
                    "Close-up of case files under desk lamp.",
                    "Detective stares at evidence wall."
                ]
            }
        ]

        # Run image generation
        asyncio.run(generator.generate_images("", dialog_segments))
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
