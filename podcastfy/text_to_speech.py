"""Text to Speech Module"""

import os
import logging
import asyncio
import edge_tts
import requests
import json
import time
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from podcastfy.utils.config_conversation import load_conversation_config
from podcastfy.utils.config import load_config
from pydub import AudioSegment
import re
from typing import List, Tuple, Optional, Union

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1024
TARGET_DBFS = -20  # Target volume level
CROSSFADE_DURATION = 500  # 500ms crossfade
FADE_DURATION = 1000  # 1s fade in/out
MAX_RETRIES = 3  # Maximum number of retries for API calls
RETRY_DELAY = 5  # Delay between retries in seconds

class TextToSpeech:
    def __init__(self, model: str = 'openai', api_key: Optional[str] = None):
        """Initialize the TextToSpeech class."""
        self.model = model.lower()
        self.config = load_config()
        self.conversation_config = load_conversation_config()
        self.tts_config = self.conversation_config.get('text_to_speech', {})

        # Character voice mappings
        self.character_voices = {
            "DetectiveSarah": {
                "openai": "onyx",  # Deep, authoritative female voice
                "elevenlabs": "pBZVCk298iJlHAcHQwLr",  # Latina detective voice
                "style": "Professional, commanding"
            },
            "OfficerMike": {
                "openai": "echo",  # Young male voice
                "elevenlabs": "JVmMgKJbp4ER2bqrITpV",  # Young officer voice
                "style": "Energetic, nervous"
            },
            "EmmaLawson": {
                "openai": "nova",  # Cold female voice
                "elevenlabs": "9xDZ0uWK4h0mYOKCXBnw",  # Cold, calculated voice
                "style": "Detached, precise"
            },
            "Maria": {
                "openai": "alloy",  # Professional narrator voice
                "elevenlabs": "IvUzQuODMwxmPUiKQ7DJ",  # Narrator voice
                "style": "Professional, atmospheric"
            }
        }

        # Initialize API keys
        if self.model == 'openai':
            self.openai_key = api_key or self.config.OPENAI_API_KEY
            if not self.openai_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.elevenlabs_key = self.config.ELEVENLABS_API_KEY
        if not self.elevenlabs_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")

        self.audio_format = self.tts_config.get('audio_format', 'mp3')
        self.temp_audio_dir = self.tts_config.get('temp_audio_dir', 'data/audio/tmp/')
        os.makedirs(self.temp_audio_dir, exist_ok=True)

        logger.info("Initialized TTS with character voices:")
        for char, voices in self.character_voices.items():
            logger.info(f"{char}: OpenAI={voices['openai']}, ElevenLabs={voices['elevenlabs']}")

    def __normalize_audio(self, audio: AudioSegment) -> AudioSegment:
        """Simple volume normalization."""
        change_in_dbfs = TARGET_DBFS - audio.dBFS
        normalized = audio.apply_gain(change_in_dbfs)
        logger.debug(f"Normalized audio from {audio.dBFS:.1f} to {normalized.dBFS:.1f} dBFS")
        return normalized

    def __speech_to_speech(self, input_file: str, output_file: str, voice_id: str, style: str) -> None:
        """Convert speech to speech using ElevenLabs with retry logic."""
        retries = 0
        while retries < MAX_RETRIES:
            try:
                logger.info(f"Converting speech to speech with voice {voice_id} ({style}) - Attempt {retries + 1}")
                
                sts_url = f"https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}/stream"
                
                headers = {
                    "Accept": "application/json",
                    "xi-api-key": self.elevenlabs_key
                }
                
                data = {
                    "model_id": "eleven_english_sts_v2",
                    "voice_settings": json.dumps({
                        "stability": 0.5,
                        "similarity_boost": 0.8,
                        "style": 1.0,  # Increased style to better match character
                        "use_speaker_boost": True
                    })
                }
                
                with open(input_file, "rb") as audio_file:
                    files = {"audio": audio_file}
                    response = requests.post(sts_url, headers=headers, data=data, files=files, stream=True)
                
                if response.ok:
                    with open(output_file, "wb") as f:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            f.write(chunk)
                    logger.info(f"Successfully converted to {style} voice")
                    return
                elif response.status_code == 502:
                    retries += 1
                    if retries < MAX_RETRIES:
                        logger.warning(f"ElevenLabs server error (502), retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        logger.error("Max retries reached, falling back to OpenAI voice")
                        # Copy the initial OpenAI audio as fallback
                        with open(input_file, "rb") as src, open(output_file, "wb") as dst:
                            dst.write(src.read())
                        return
                else:
                    raise Exception(f"Speech-to-speech conversion failed: {response.text}")
                    
            except Exception as e:
                retries += 1
                if retries < MAX_RETRIES:
                    logger.warning(f"Error in speech-to-speech conversion, retrying in {RETRY_DELAY} seconds: {str(e)}")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Max retries reached, falling back to OpenAI voice: {str(e)}")
                    # Copy the initial OpenAI audio as fallback
                    with open(input_file, "rb") as src, open(output_file, "wb") as dst:
                        dst.write(src.read())
                    return

    def split_dialogues(self, input_text: str) -> List[Tuple[str, str]]:
        """Split the input text into a list of (speaker, dialogue) tuples."""
        logger.debug("Splitting dialogues")
        pattern = r'<(.*?)>(.*?)</\1>'
        matches = re.findall(pattern, input_text, re.DOTALL)
        
        processed_matches = []
        for speaker, text in matches:
            # Remove emotes from the spoken text
            clean_text = re.sub(r'\*[^*]+\*', '', text)
            # Remove extra whitespace
            clean_text = ' '.join(clean_text.split())
            if clean_text.strip():  # Only add if there's actual dialog
                processed_matches.append((speaker.strip(), clean_text.strip()))
        
        logger.info(f"Found {len(processed_matches)} dialogue segments")
        for speaker, text in processed_matches:
            logger.debug(f"Speaker: {speaker}, Text length: {len(text)}")
        return processed_matches

    def convert_to_speech(self, text: str, output_file: str) -> None:
        """Convert input text to speech with normalization."""
        try:
            logger.info("Starting text to speech conversion")
            dialogues = self.split_dialogues(text)
            
            audio_segments = []
            counter = 0

            # Load and normalize theme music if exists
            theme_music_path = os.path.join('C:\\', 'appz', 'podcastfy', 'data', 'audio', 'theme_music.mp3')
            if os.path.exists(theme_music_path):
                theme_music = AudioSegment.from_mp3(theme_music_path)
                theme_music = self.__normalize_audio(theme_music)
                theme_music = theme_music.fade_in(FADE_DURATION).fade_out(FADE_DURATION)
                audio_segments.append(theme_music)

            # Process each dialogue segment
            for speaker, content in dialogues:
                if not content.strip():
                    continue  # Skip empty lines
                    
                logger.info(f"Processing speaker: {speaker}")
                
                # Get character voice settings
                char_voices = self.character_voices.get(speaker)
                if not char_voices:
                    logger.warning(f"No voice configuration for {speaker}, using default")
                    char_voices = self.character_voices["Maria"]
                
                # Generate initial speech with OpenAI
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                }

                data = {
                    "model": "tts-1-hd",
                    "input": content,
                    "voice": char_voices["openai"],
                    "response_format": self.audio_format,
                    "speed": 1.0
                }

                logger.info(f"Generating OpenAI speech with voice: {char_voices['openai']}")
                response = requests.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers=headers,
                    json=data
                )

                if response.status_code != 200:
                    raise Exception(f"OpenAI API error: {response.text}")

                # Save initial audio
                counter += 1
                initial_file = os.path.join(self.temp_audio_dir, f"initial_{counter}.{self.audio_format}")
                with open(initial_file, "wb") as out:
                    out.write(response.content)
                
                # Convert through ElevenLabs for character voice
                final_file = os.path.join(self.temp_audio_dir, f"{counter}.{self.audio_format}")
                self.__speech_to_speech(
                    initial_file, 
                    final_file, 
                    char_voices["elevenlabs"],
                    char_voices["style"]
                )
                
                # Load and normalize the segment
                segment = AudioSegment.from_file(final_file, format=self.audio_format)
                normalized_segment = self.__normalize_audio(segment)
                
                # Add small pause between segments
                pause = AudioSegment.silent(duration=200)  # 200ms pause
                audio_segments.append(normalized_segment)
                audio_segments.append(pause)
                
                # Clean up temp files
                os.remove(initial_file)
                os.remove(final_file)

            # Add theme music at end if exists
            if os.path.exists(theme_music_path):
                audio_segments.append(theme_music)

            # Combine segments with crossfade
            if audio_segments:
                final_audio = audio_segments[0]
                for segment in audio_segments[1:]:
                    if len(final_audio) > CROSSFADE_DURATION and len(segment) > CROSSFADE_DURATION:
                        final_audio = final_audio.append(segment, crossfade=CROSSFADE_DURATION)
                    else:
                        final_audio = final_audio.append(segment)

                # Final normalization and export
                final_audio = self.__normalize_audio(final_audio)
                final_audio.export(output_file, format=self.audio_format)
                logger.info(f"Final audio saved to {output_file}")
            else:
                logger.warning("No audio segments to combine")

        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            raise

def main():
    """Test the TextToSpeech class."""
    try:
        with open('test_input.txt', 'r', encoding='utf-8') as file:
            input_text = file.read()

        tts = TextToSpeech(model='openai')
        tts.convert_to_speech(input_text, 'test_output.mp3')
        logger.info("Test completed successfully")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
