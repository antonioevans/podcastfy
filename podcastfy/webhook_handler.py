"""Webhook Handler Module"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any, Tuple
import os
import shutil
import json
import asyncio
from datetime import datetime
from .content_generator import ContentGenerator
from .text_to_speech import TextToSpeech
from .utils.image_generator import ImageGenerator
from .utils.video_generator import VideoGenerator
from .utils.config import load_config
import logging
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VideoRequest(BaseModel):
    input_text: str
    scene_config: Dict[str, int]  # Required scene configuration from webhook
    image_paths: Optional[List[str]] = None
    scene_settings: Optional[Dict[str, Any]] = None
    character_profiles: Optional[Dict[str, Any]] = None
    visual_style: Optional[Dict[str, Any]] = None
    shot_types: Optional[List[Dict[str, Any]]] = None

app = FastAPI(
    title="Podcastfy API",
    description="API for generating video podcasts",
    version="1.0.0"
)

def ensure_directories():
    """Ensure all required directories exist."""
    base_dir = os.path.join('C:\\', 'appz', 'podcastfy', 'data')
    dirs = {
        'transcripts': os.path.join(base_dir, 'transcripts'),
        'images': os.path.join(base_dir, 'images'),
        'audio': os.path.join(base_dir, 'audio'),
        'videos': os.path.join(base_dir, 'videos')
    }
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Ensured directory exists: {dir_path}")
    return dirs

def archive_old_files():
    """Move old files to archive directories."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dirs = ensure_directories()
        for dir_name, dir_path in dirs.items():
            archive_dir = os.path.join(dir_path, 'old', timestamp)
            if os.path.exists(dir_path):
                os.makedirs(archive_dir, exist_ok=True)
                for item in os.listdir(dir_path):
                    if item != 'old':
                        src = os.path.join(dir_path, item)
                        dst = os.path.join(archive_dir, item)
                        if os.path.exists(src):
                            shutil.move(src, dst)
                            logger.debug(f"Archived {src} to {dst}")
        logger.info(f"Archived old files to timestamp: {timestamp}")
    except Exception as e:
        logger.error(f"Error archiving old files: {str(e)}")
        raise

async def generate_title_card(scene_index: int, scene_data: Dict[str, Any], llm: ChatGoogleGenerativeAI) -> str:
    """Generate a noir-style title card for a scene."""
    try:
        title_prompt = f"""Create a noir-style title card for scene {scene_index + 1}.

Scene Details:
- Location: {scene_data['location']}
- Tone: {scene_data['tone']}
- Key Elements: {', '.join(scene_data['key_elements'])}

Requirements:
1. Create a short, dramatic chapter title (2-4 words)
2. Capture the noir atmosphere
3. Reflect the scene's mood and setting
4. Use classic noir film chapter style

Example Format:
"Shadows of Truth" or "Midnight Confessions"

Return ONLY the title text, no quotes or additional formatting."""

        messages = [
            SystemMessage(content="""You are a noir film title writer.
Create dramatic, atmospheric chapter titles.
Return ONLY the title text - no other text or formatting."""),
            HumanMessage(content=title_prompt)
        ]
        
        response = llm.invoke(messages)
        title = response.content.strip()
        logger.debug(f"Generated title for scene {scene_index + 1}: {title}")
        
        return title
        
    except Exception as e:
        logger.error(f"Error generating title for scene {scene_index + 1}: {str(e)}")
        return f"Chapter {scene_index + 1}"

async def process_single_scene(scene_index: int, scene_config: Dict[str, int], dialog_content: str, gemini_api_key: str) -> Dict[str, Any]:
    """Process a single scene with its own Gemini instance."""
    try:
        logger.info(f"Processing scene {scene_index + 1} with dedicated Gemini instance")
        
        # Create a new Gemini instance for this scene
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest",
            temperature=0.7,
            google_api_key=gemini_api_key
        )
        
        scene_prompt = f"""Create a noir scene description for scene {scene_index + 1} of {scene_config["num_scenes"]}.
This scene should have EXACTLY {scene_config["shots_per_scene"]} distinct camera shots.

Return ONLY this JSON structure:

{{
  "scene": {{
    "start_time": {scene_index * scene_config["scene_duration"]},
    "duration": {scene_config["scene_duration"]},
    "location": "Unique location for this scene",
    "tone": "Specific noir mood and atmosphere",
    "characters": ["DetectiveSarah", "OfficerMike"],
    "key_elements": ["Three", "Distinct", "Visual elements"],
    "transitions": "How this scene transitions",
    "shots": {scene_config["shots_per_scene"]}
  }}
}}

Requirements:
1. Create a UNIQUE location and tone
2. Include relevant characters
3. Specify exactly 3 key visual elements
4. Focus on noir atmosphere
5. Return ONLY valid JSON

Context from dialog:
{dialog_content}"""

        messages = [
            SystemMessage(content=f"""You are a noir film director creating scene {scene_index + 1} of {scene_config["num_scenes"]}.
Focus on creating a unique and atmospheric scene.
Return ONLY a valid JSON object.
The response must start with {{ and end with }} - no other text allowed."""),
            HumanMessage(content=scene_prompt)
        ]
        
        logger.debug(f"Sending scene prompt to Gemini instance {scene_index + 1}")
        response = llm.invoke(messages)
        
        # Clean and validate JSON response
        response_text = response.content.strip()
        try:
            # Try to parse the response as JSON
            scene_data = json.loads(response_text)
            if "scene" not in scene_data:
                raise ValueError("Missing 'scene' key in response")
            scene_data = scene_data["scene"]
            logger.debug(f"Generated scene {scene_index + 1}: {json.dumps(scene_data, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Gemini for scene {scene_index + 1}: {response_text}")
            logger.error(f"JSON error: {str(e)}")
            # Create default scene data
            scene_data = {
                "start_time": scene_index * scene_config["scene_duration"],
                "duration": scene_config["scene_duration"],
                "location": f"Scene {scene_index + 1}",
                "tone": "Noir, mysterious",
                "characters": ["DetectiveSarah", "OfficerMike"],
                "key_elements": ["Shadows", "Rain", "City lights"],
                "transitions": "Fade to next scene",
                "shots": scene_config["shots_per_scene"]
            }
        
        # Generate title card for this scene
        title = await generate_title_card(scene_index, scene_data, llm)
        
        # Generate shots for this scene with the same Gemini instance
        shots = await generate_scene_shots(scene_data, llm, scene_index)
        
        # Create the final scene segment
        segment = {
            "title": title,
            "start": scene_data["start_time"],
            "end": scene_data["start_time"] + scene_data["duration"],
            "scene_descriptions": shots
        }
        
        return segment
        
    except Exception as e:
        logger.error(f"Error processing scene {scene_index + 1}: {str(e)}")
        raise

async def generate_scene_shots(scene: Dict[str, Any], llm: ChatGoogleGenerativeAI, scene_index: int) -> List[str]:
    """Generate shots for a single scene using the same Gemini instance."""
    try:
        shots = []
        num_shots = scene["shots"]
        logger.debug(f"Generating {num_shots} shots for scene {scene_index + 1} in {scene['location']}")
        
        # Base shot types to cycle through
        base_shot_types = [
            {
                "type": "Establishing shot",
                "purpose": "Set the scene and atmosphere",
                "focus": "Wide view of location and mood",
                "angles": ["Wide shot", "High angle", "Dutch angle", "Crane shot"]
            },
            {
                "type": "Character shot",
                "purpose": "Show character interactions",
                "focus": "Medium or close-up on characters",
                "angles": ["Medium shot", "Close-up", "Over-the-shoulder", "Two-shot"]
            },
            {
                "type": "Detail shot",
                "purpose": "Highlight key elements",
                "focus": "Specific objects or atmospheric details",
                "angles": ["Extreme close-up", "Insert shot", "Low angle", "Macro shot"]
            }
        ]
        
        for shot_index in range(num_shots):
            base_shot = base_shot_types[shot_index % len(base_shot_types)]
            variation_num = (shot_index // len(base_shot_types)) + 1
            
            shot_prompt = f"""Create a detailed noir visual description for shot {shot_index + 1} of {num_shots} in scene {scene_index + 1}:

Scene Details:
- Location: {scene['location']}
- Tone: {scene['tone']}
- Key Elements: {', '.join(scene['key_elements'])}
- Characters: {', '.join(scene['characters'])}

Shot Requirements:
- Type: {base_shot['type']} (Variation {variation_num})
- Purpose: {base_shot['purpose']}
- Focus: {base_shot['focus']}
- Suggested Angles: {', '.join(base_shot['angles'])}

Create a cinematic description that:
1. Uses specific camera angles and movements
2. Describes lighting and shadows in detail
3. Places characters and elements precisely
4. Maintains noir atmosphere
5. Creates a unique variation of the base shot type

Example Format:
Low angle shot through rain-streaked windows, harsh neon light cutting diagonal shadows across detective's face as she studies case files, city lights blurred in background.

IMPORTANT: Return ONLY the visual description, no other text."""

            messages = [
                SystemMessage(content=f"""You are a noir cinematographer creating shot {shot_index + 1} of {num_shots} for scene {scene_index + 1}.
Focus on powerful visuals and dramatic composition.
Create a unique variation of {base_shot['type']}.
Return ONLY the shot description, no other text."""),
                HumanMessage(content=shot_prompt)
            ]
            
            response = llm.invoke(messages)
            shot_description = response.content.strip()
            logger.debug(f"Generated shot {shot_index + 1} for scene {scene_index + 1}:\n{shot_description}")
            shots.append(shot_description)
        
        if len(shots) != num_shots:
            raise ValueError(f"Generated {len(shots)} shots instead of {num_shots} for scene {scene_index + 1}")
        
        return shots
        
    except Exception as e:
        logger.error(f"Error generating shots for scene {scene_index + 1}: {str(e)}")
        raise

@app.post("/generate_video")
async def generate_video(request: VideoRequest):
    """Generate video content via webhook"""
    try:
        # Ensure all directories exist and get paths
        dirs = ensure_directories()
            
        # Archive old files
        archive_old_files()
        
        config = load_config()
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Step 1: Generate dialog content
        logger.info("Generating dialog content...")
        content_generator = ContentGenerator(api_key=gemini_api_key)
        dialog_content = content_generator.generate_qa_content(
            input_texts=request.input_text
        )
        logger.debug(f"Generated dialog content:\n{dialog_content}")
        
        # Save dialog content
        transcript_path = os.path.join(dirs['transcripts'], 'dialog.txt')
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(dialog_content)
        logger.info(f"Dialog saved to {transcript_path}")
        
        # Step 2: Process each scene with its own Gemini instance
        logger.info(f"Processing {request.scene_config['num_scenes']} scenes with dedicated Gemini instances")
        
        # Create tasks for processing each scene
        scene_tasks = []
        for i in range(request.scene_config["num_scenes"]):
            task = process_single_scene(i, request.scene_config, dialog_content, gemini_api_key)
            scene_tasks.append(task)
        
        # Process all scenes concurrently
        scene_segments = await asyncio.gather(*scene_tasks)
        logger.info(f"Generated {len(scene_segments)} scene segments")
        
        # Save scene structure
        scenes_path = os.path.join(dirs['transcripts'], 'scenes.json')
        with open(scenes_path, 'w', encoding='utf-8') as f:
            json.dump(scene_segments, f, indent=2)
        logger.info(f"Scene structure saved to {scenes_path}")
        
        # Step 3: Generate audio
        logger.info("Generating audio...")
        tts = TextToSpeech(model='openai')
        audio_path = os.path.join(dirs['audio'], 'output.mp3')
        tts.convert_to_speech(dialog_content, audio_path)
        logger.info(f"Audio saved to {audio_path}")
        
        # Step 4: Generate scene visualizations
        logger.info("Generating scene visualizations...")
        image_generator = ImageGenerator(
            gemini_api_key=gemini_api_key,
            scene_settings=request.scene_settings,
            character_profiles=request.character_profiles,
            visual_style=request.visual_style,
            shot_types=request.shot_types
        )
        
        # Generate images for all scenes
        await image_generator.generate_images(dialog_content, scene_segments)
        
        # Step 5: Create final video with title cards
        logger.info("Creating video...")
        video_generator = VideoGenerator(scene_config=request.scene_config)
        video_path = video_generator.create_slideshow(audio_path)
        logger.info(f"Video saved to {video_path}")
        
        return {
            "status": "success",
            "message": "Video podcast generated successfully",
            "transcript_path": transcript_path,
            "scenes_path": scenes_path,
            "audio_path": audio_path,
            "video_path": video_path
        }
        
    except Exception as e:
        logger.error(f"Error generating video podcast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
