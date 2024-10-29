"""
Podcastfy CLI
"""

import os
import uuid
import typer
import yaml
import asyncio
from moviepy.editor import AudioFileClip
from podcastfy.content_parser.content_extractor import ContentExtractor
from podcastfy.content_generator import ContentGenerator
from podcastfy.text_to_speech import TextToSpeech
from podcastfy.utils.config import Config, load_config
from podcastfy.utils.config_conversation import (
    ConversationConfig,
    load_conversation_config,
)
from podcastfy.utils.logger import setup_logger
from podcastfy.utils.image_generator import ImageGenerator
from podcastfy.utils.video_generator import VideoGenerator
from typing import List, Optional, Dict, Any
import copy
import re

logger = setup_logger(__name__)
logger.setLevel('DEBUG')
app = typer.Typer()

def extract_audio_segments(qa_content: str) -> List[Dict[str, float]]:
    """Extract audio segment timings from the transcript."""
    try:
        segments = []
        current_time = 0.0
        
        # Split content into speaker segments
        pattern = r'<(.*?)>(.*?)</\1>'
        matches = re.findall(pattern, qa_content, re.DOTALL)
        
        for speaker, text in matches:
            # Estimate duration based on word count (rough approximation)
            words = len(text.split())
            duration = (words * 0.4)  # Average speaking rate
            
            segments.append({
                "start": current_time,
                "end": current_time + duration,
                "speaker": speaker,
                "text": text.strip()
            })
            current_time += duration
        
        return segments
    except Exception as e:
        logger.error(f"Error extracting audio segments: {str(e)}")
        raise

async def process_content(
    urls=None,
    transcript_file=None,
    tts_model="openai",
    generate_audio=True,
    config=None,
    conversation_config: Optional[Dict[str, Any]] = None,
    image_paths: Optional[List[str]] = None,
    is_local: bool = False,
    custom_prompt: Optional[str] = None,
    generate_images: bool = False,
    generate_video: bool = False,
):
    """Process content with optional custom prompt."""
    try:
        logger.debug("Starting process_content")
        if config is None:
            config = load_config()
        
        conv_config = load_conversation_config()
        if conversation_config:
            conv_config.configure(conversation_config)

        if transcript_file:
            logger.info(f"Using transcript file: {transcript_file}")
            with open(transcript_file, "r") as file:
                qa_content = file.read()
        else:
            content_generator = ContentGenerator(
                api_key=config.GEMINI_API_KEY,
                conversation_config=conv_config.to_dict(),
                custom_prompt_path=custom_prompt
            )

            if custom_prompt and not urls and not image_paths:
                logger.debug(f"Loading custom prompt from {custom_prompt}")
                with open(custom_prompt, 'r') as f:
                    custom_config = yaml.safe_load(f)
                    combined_content = custom_config.get('topic', '')
                    if custom_config.get('background'):
                        combined_content += "\n\n" + custom_config['background']
            elif urls:
                logger.info(f"Processing {len(urls)} links")
                content_extractor = ContentExtractor()
                contents = [content_extractor.extract_content(link) for link in urls]
                combined_content = "\n\n".join(contents)
            else:
                combined_content = ""

            random_filename = f"transcript_{uuid.uuid4().hex}.txt"
            transcript_filepath = os.path.join(
                config.get("output_directories")["transcripts"], random_filename
            )
            qa_content = content_generator.generate_qa_content(
                combined_content,
                image_file_paths=image_paths or [],
                output_filepath=transcript_filepath,
                is_local=is_local,
            )

        output_file = None
        if generate_audio:
            # Extract audio segments before TTS
            audio_segments = extract_audio_segments(qa_content)
            logger.info(f"Extracted {len(audio_segments)} audio segments")

            api_key = None
            if tts_model != "edge":
                api_key = getattr(config, f"{tts_model.upper()}_API_KEY")

            text_to_speech = TextToSpeech(model=tts_model, api_key=api_key)
            random_filename = f"podcast_{uuid.uuid4().hex}.mp3"
            audio_file = os.path.join(
                config.get("output_directories")["audio"], random_filename
            )
            text_to_speech.convert_to_speech(qa_content, audio_file)
            logger.info(f"Podcast generated successfully using {tts_model} TTS model")
            output_file = audio_file

            # Generate images if requested
            if generate_images:
                logger.info("Generating images from transcript")
                image_generator = ImageGenerator(config.GEMINI_API_KEY)
                video_generator = VideoGenerator()  # Create early to clear old images
                video_generator.clear_old_images()  # Clear old images before generating new ones
                await image_generator.generate_images(qa_content, audio_segments)

                # Generate video if requested
                if generate_video:
                    logger.info("Generating video slideshow")
                    output_file = video_generator.create_slideshow(audio_file)
                    logger.info(f"Video generated successfully: {output_file}")

        else:
            logger.info(f"Transcript generated successfully: {transcript_filepath}")
            output_file = transcript_filepath

        return output_file

    except Exception as e:
        logger.error(f"An error occurred in the process_content function: {str(e)}")
        raise

@app.command()
def main(
    urls: list[str] = typer.Option(None, "--url", "-u", help="URLs to process"),
    file: typer.FileText = typer.Option(
        None, "--file", "-f", help="File containing URLs, one per line"
    ),
    transcript: typer.FileText = typer.Option(
        None, "--transcript", "-t", help="Path to a transcript file"
    ),
    tts_model: str = typer.Option(
        None,
        "--tts-model",
        "-tts",
        help="TTS model to use (openai, elevenlabs or edge)",
    ),
    transcript_only: bool = typer.Option(
        False, "--transcript-only", help="Generate only a transcript without audio"
    ),
    conversation_config_path: str = typer.Option(
        None,
        "--conversation-config",
        "-cc",
        help="Path to custom conversation configuration YAML file",
    ),
    image_paths: List[str] = typer.Option(
        None, "--image", "-i", help="Paths to image files to process"
    ),
    is_local: bool = typer.Option(
        False,
        "--local",
        "-l",
        help="Use a local LLM instead of a remote one",
    ),
    custom_prompt: str = typer.Option(
        None,
        "--custom-prompt",
        "-cp",
        help="Path to custom prompt YAML to append to main prompt",
    ),
    generate_images: bool = typer.Option(
        False,
        "--generate-images",
        "-gi",
        help="Generate images from transcript using Gemini and Flux",
    ),
    generate_video: bool = typer.Option(
        False,
        "--generate-video",
        "-gv",
        help="Generate video slideshow from images and audio",
    ),
):
    """Generate a podcast or transcript with optional image and video generation."""
    try:
        logger.debug("Starting main")
        config = load_config()

        conversation_config = None
        if conversation_config_path:
            with open(conversation_config_path, "r") as f:
                conversation_config = yaml.safe_load(f)
                
        if tts_model is None:
            tts_config = load_conversation_config().get('text_to_speech', {})
            tts_model = tts_config.get('default_tts_model', 'openai')
            
        if transcript:
            if image_paths:
                logger.warning("Image paths are ignored when using a transcript file.")
            final_output = asyncio.run(process_content(
                transcript_file=transcript.name,
                tts_model=tts_model,
                generate_audio=not transcript_only,
                conversation_config=conversation_config,
                config=config,
                is_local=is_local,
                custom_prompt=custom_prompt,
                generate_images=generate_images,
                generate_video=generate_video,
            ))
        else:
            urls_list = urls or []
            if file:
                urls_list.extend([line.strip() for line in file if line.strip()])

            if not urls_list and not image_paths and not custom_prompt:
                raise typer.BadParameter(
                    "No input provided. Use --url to specify URLs, --file to specify a file containing URLs, --transcript for a transcript file, --image for image files, or --custom-prompt for a custom prompt."
                )

            final_output = asyncio.run(process_content(
                urls=urls_list,
                tts_model=tts_model,
                generate_audio=not transcript_only,
                config=config,
                conversation_config=conversation_config,
                image_paths=image_paths,
                is_local=is_local,
                custom_prompt=custom_prompt,
                generate_images=generate_images,
                generate_video=generate_video,
            ))

        if transcript_only:
            typer.echo(f"Transcript generated successfully: {final_output}")
        else:
            if generate_video:
                typer.echo(f"Video generated successfully: {final_output}")
            else:
                typer.echo(
                    f"Podcast generated successfully using {tts_model} TTS model: {final_output}"
                )

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
