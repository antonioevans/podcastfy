"""Video generation module."""
import os
import json
import glob
import shutil
from typing import List, Dict, Any
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, TextClip, concatenate_videoclips
from moviepy.config import change_settings
import numpy as np
from PIL import Image
import logging
import subprocess
from datetime import datetime
import platform

logger = logging.getLogger(__name__)

def configure_imagemagick():
    """Configure ImageMagick for the current environment."""
    try:
        # Check if we're on Replit
        is_replit = 'REPL_ID' in os.environ
        
        if is_replit:
            # Replit environment
            imagemagick_binary = '/nix/store/rwjrr9rk55xhm57x7dyrk3n8k6vjjc6n-imagemagick-7.1.1-11/bin/convert'
            if os.path.exists(imagemagick_binary):
                change_settings({"IMAGEMAGICK_BINARY": imagemagick_binary})
                logger.info("Configured ImageMagick for Replit environment")
                return True
        else:
            # Local environment
            if platform.system() == 'Windows':
                # Try common Windows installation paths
                paths = [
                    r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe",
                    r"C:\Program Files\ImageMagick-7.0.11-Q16\magick.exe",
                    r"C:\Program Files (x86)\ImageMagick-7.1.1-Q16\magick.exe"
                ]
                for path in paths:
                    if os.path.exists(path):
                        change_settings({"IMAGEMAGICK_BINARY": path})
                        logger.info(f"Configured ImageMagick for Windows: {path}")
                        return True
            else:
                # Unix-like systems
                try:
                    # Check if ImageMagick is in PATH
                    subprocess.run(['convert', '--version'], capture_output=True, check=True)
                    logger.info("ImageMagick found in system PATH")
                    return True
                except subprocess.CalledProcessError:
                    logger.warning("ImageMagick not found in system PATH")
                    return False
        
        logger.error("ImageMagick not found in expected locations")
        return False
        
    except Exception as e:
        logger.error(f"Error configuring ImageMagick: {str(e)}")
        return False

class VideoGenerator:
    def __init__(self, scene_config: Dict[str, int] = None):
        """Initialize the VideoGenerator."""
        self.project_root = os.path.join('C:\\', 'appz', 'podcastfy')
        self.images_dir = os.path.join(self.project_root, 'data', 'images')
        self.videos_dir = os.path.join(self.project_root, 'data', 'videos')
        os.makedirs(self.videos_dir, exist_ok=True)
        
        # Configure ImageMagick
        if not configure_imagemagick():
            raise RuntimeError("Failed to configure ImageMagick. Please ensure it is installed correctly.")
        
        # Scene configuration
        self.scene_config = scene_config or {
            "num_scenes": 3,
            "scene_duration": 1,
            "shots_per_scene": 12
        }
        
        # Calculate timing constants based on scene config
        self.shot_duration = self.scene_config["scene_duration"] / self.scene_config["shots_per_scene"]
        self.title_duration = 2.0  # Title cards show for 2 seconds
        self.crossfade_duration = min(0.5, self.shot_duration / 2)  # Crossfade should not exceed half shot duration
        
        # Visual constants
        self.target_width = 1920  # HD resolution
        self.target_height = 1080
        
        # Ken Burns effect constants
        self.zoom_range = (1.1, 1.2)  # Start with 110-120% size to ensure no black edges
        
        # Check for NVIDIA GPU
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            self.has_nvidia = result.returncode == 0
            logger.info("NVIDIA GPU detected" if self.has_nvidia else "No NVIDIA GPU found")
        except:
            self.has_nvidia = False
            logger.info("Could not detect NVIDIA GPU")

    def create_title_card(self, scene_index: int, title: str) -> ImageClip:
        """Create a title card for a scene."""
        try:
            # Create text clip with noir style
            txt_clip = TextClip(
                title,
                fontsize=70,
                color='white',
                font='Arial-Bold',
                kerning=-2,
                interline=-1,
                size=(self.target_width * 0.8, None),  # 80% of screen width
                method='caption',
                align='center'
            )
            
            # Create black background
            bg_clip = ImageClip(
                np.zeros((self.target_height, self.target_width, 3), dtype=np.uint8)
            )
            
            # Center text on background
            txt_clip = txt_clip.set_position('center')
            
            # Composite text over background
            title_clip = concatenate_videoclips([bg_clip, txt_clip])
            
            return title_clip.set_duration(self.title_duration)
            
        except Exception as e:
            logger.error(f"Error creating title card for scene {scene_index + 1}: {str(e)}")
            # Create simple fallback title card
            bg_clip = ImageClip(
                np.zeros((self.target_height, self.target_width, 3), dtype=np.uint8)
            ).set_duration(self.title_duration)
            return bg_clip

    def resize_image_array(self, image_array: np.ndarray) -> np.ndarray:
        """Resize numpy array to target dimensions while maintaining aspect ratio and ensuring full coverage."""
        try:
            image = Image.fromarray(image_array)
            
            # Calculate target size that will cover the frame completely
            target_ratio = self.target_width / self.target_height
            image_ratio = image.width / image.height
            
            if image_ratio > target_ratio:
                # Image is wider than target
                new_height = self.target_height
                new_width = int(new_height * image_ratio)
            else:
                # Image is taller than target
                new_width = self.target_width
                new_height = int(new_width / image_ratio)
            
            # Ensure dimensions are at least 20% larger than target for Ken Burns
            scale_factor = 1.2
            new_width = max(new_width, int(self.target_width * scale_factor))
            new_height = max(new_height, int(self.target_height * scale_factor))
            
            # Resize image
            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to array
            return np.array(resized)
        except Exception as e:
            logger.error(f"Error resizing image array: {str(e)}")
            return image_array

    def apply_ken_burns(self, clip: ImageClip, duration: float, direction: str = 'in') -> ImageClip:
        """Apply Ken Burns effect ensuring image always fills screen."""
        w, h = clip.size
        
        # Calculate zoom range ensuring image always fills screen
        if direction == 'in':
            start_zoom = self.zoom_range[1]  # Start larger
            end_zoom = self.zoom_range[0]    # End smaller but still >100%
        else:
            start_zoom = self.zoom_range[0]  # Start smaller but still >100%
            end_zoom = self.zoom_range[1]    # End larger
        
        def zoom(t):
            # Linear interpolation between start and end zoom
            zoom_factor = start_zoom + (end_zoom - start_zoom) * t / duration
            return zoom_factor
            
        return clip.resize(zoom)

    def get_image_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all generated images."""
        metadata_files = glob.glob(os.path.join(self.images_dir, 'scene_*_shot_*.json'))
        metadata_list = []
        
        for metadata_file in metadata_files:
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    # Get corresponding image file
                    image_file = metadata_file.replace('.json', '.png')
                    if os.path.exists(image_file):
                        metadata['image_path'] = image_file
                        metadata_list.append(metadata)
            except Exception as e:
                logger.error(f"Error reading metadata file {metadata_file}: {str(e)}")
                continue
        
        # Sort by scene index and shot index
        metadata_list.sort(key=lambda x: (x['scene_index'], x['shot_index']))
        return metadata_list

    def create_slideshow(self, audio_file: str) -> str:
        """Create a slideshow video from timestamped images and audio."""
        try:
            # Load audio and get duration
            audio = AudioFileClip(audio_file)
            total_duration = audio.duration
            
            # Get all available images with metadata
            metadata_list = self.get_image_metadata()
            if not metadata_list:
                raise ValueError("No image metadata found")
            
            # Create clips list
            clips = []
            current_time = 0
            
            # Group metadata by scene
            scenes = {}
            for metadata in metadata_list:
                scene_idx = metadata['scene_index']
                if scene_idx not in scenes:
                    scenes[scene_idx] = []
                scenes[scene_idx].append(metadata)
            
            # Process each scene
            for scene_idx in sorted(scenes.keys()):
                scene_metadata = scenes[scene_idx]
                
                # Create and add title card for scene
                title = f"Chapter {scene_idx + 1}"
                title_clip = self.create_title_card(scene_idx, title)
                title_clip = title_clip.set_start(current_time)
                clips.append(title_clip)
                current_time += self.title_duration
                
                # Process shots in scene
                for shot_metadata in scene_metadata:
                    # Load and resize image
                    img = Image.open(shot_metadata['image_path'])
                    img_array = np.array(img)
                    resized_array = self.resize_image_array(img_array)
                    
                    # Create base clip
                    clip = ImageClip(resized_array)
                    
                    # Apply Ken Burns effect alternating between zoom in and out
                    clip = self.apply_ken_burns(
                        clip, 
                        duration=self.shot_duration,
                        direction='in' if shot_metadata['shot_index'] % 2 == 0 else 'out'
                    )
                    
                    # Set timing and transitions
                    clip = (clip
                           .set_start(current_time)
                           .set_duration(self.shot_duration)
                           .crossfadein(self.crossfade_duration)
                           .crossfadeout(self.crossfade_duration))
                    
                    clips.append(clip)
                    current_time += self.shot_duration - self.crossfade_duration
                    logger.debug(f"Added clip for Scene {scene_idx + 1}, Shot {shot_metadata['shot_index'] + 1}: {current_time:.1f}s")
            
            # Combine all clips
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip = final_clip.set_duration(total_duration)
            
            # Add audio
            final_clip = final_clip.set_audio(audio)
            
            # Generate output filename
            output_filename = f"noir_podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            output_path = os.path.join(self.videos_dir, output_filename)
            
            # Optimized encoding settings
            if self.has_nvidia:
                try:
                    write_params = {
                        'fps': 30,
                        'codec': 'h264_nvenc',
                        'audio_codec': 'aac',
                        'audio_bitrate': "192k",
                        'preset': 'fast',
                        'threads': 8,
                        'ffmpeg_params': [
                            '-pix_fmt', 'yuv420p',
                            '-rc:v', 'vbr',
                            '-cq:v', '20',
                            '-b:v', '8M',
                            '-maxrate:v', '10M',
                            '-bufsize:v', '20M',
                            '-profile:v', 'high',
                            '-spatial-aq', '1',
                            '-temporal-aq', '1',
                            '-rc-lookahead', '32'
                        ]
                    }
                    final_clip.write_videofile(output_path, **write_params)
                except Exception as e:
                    logger.warning(f"NVENC encoding failed, falling back to CPU: {str(e)}")
                    self._write_with_cpu(final_clip, output_path)
            else:
                self._write_with_cpu(final_clip, output_path)
            
            # Clean up
            final_clip.close()
            audio.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating slideshow: {str(e)}")
            raise

    def _write_with_cpu(self, clip, output_path):
        """Write video using CPU encoding with optimized settings."""
        write_params = {
            'fps': 30,
            'codec': 'libx264',
            'audio_codec': 'aac',
            'audio_bitrate': "192k",
            'preset': 'ultrafast',
            'threads': 8,
            'ffmpeg_params': [
                '-pix_fmt', 'yuv420p',
                '-crf', '28',
                '-tune', 'film',
                '-profile:v', 'high',
                '-movflags', '+faststart'
            ]
        }
        clip.write_videofile(output_path, **write_params)

def main():
    """Test the VideoGenerator."""
    try:
        scene_config = {
            "num_scenes": 3,
            "scene_duration": 1,
            "shots_per_scene": 12
        }
        generator = VideoGenerator(scene_config)
        audio_path = os.path.join('C:\\', 'appz', 'podcastfy', 'data', 'audio', 'output.mp3')
        output_path = generator.create_slideshow(audio_path)
        print(f"Video generated: {output_path}")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
