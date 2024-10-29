# Podcastfy 🎙️

A sophisticated system for generating noir-style video podcasts with AI-driven content, visuals, and audio.

## Technical Architecture 🏗️

### System Overview
Podcastfy uses a sophisticated pipeline to transform text prompts into complete video podcasts:

1. **Content Generation Layer**
   - Uses Gemini Pro for initial dialog generation
   - Enforces strict character roles and dialog structure
   - Characters:
     * DetectiveSarah (Lead investigator)
     * OfficerMike (Supporting officer)
     * EmmaLawson (Person of interest)
     * Maria (Professional narrator)
   - Maintains proper XML tagging and scene directions

2. **Scene Analysis Engine**
   - Parallel processing with dedicated Gemini instances per scene
   - Configurable scene structure:
     * Number of scenes (1-20)
     * Scene duration (1-60 seconds)
     * Shots per scene (1-12)
   - Automatic title card generation
   - Tracks:
     * Location changes
     * Emotional shifts
     * Character interactions
     * Scene transitions
   - Creates cinematic flow and pacing

3. **Audio Processing Pipeline**
   - Initial speech generation with OpenAI TTS
   - Character voice enhancement through ElevenLabs
   - Voice assignments:
     * DetectiveSarah: pBZVCk298iJlHAcHQwLr (Deep, authoritative)
     * OfficerMike: JVmMgKJbp4ER2bqrITpV (Young, energetic)
     * EmmaLawson: 9xDZ0uWK4h0mYOKCXBnw (Cold, detached)
     * Maria: IvUzQuODMwxmPUiKQ7DJ (Professional narrator)
   - Audio normalization and crossfading

4. **Visual Generation System**
   - Scene visualization using parallel Gemini Pro instances
   - Image generation through Flux API
   - Configurable shots per scene
   - Automatic title card generation between scenes
   - Noir-style visual consistency

5. **Video Composition**
   - Synchronized audio-visual alignment
   - Scene-based image timing
   - Title cards between scenes (2s duration)
   - Smooth transitions with configurable timing
   - Professional output formatting

### Directory Structure
```
podcastfy/
├── data/
│   ├── audio/      # Generated audio files
│   ├── images/     # Generated scene images
│   ├── prompts/    # System prompts
│   └── videos/     # Final output videos
├── podcastfy/
│   ├── utils/
│   │   ├── config.py
│   │   ├── image_generator.py
│   │   ├── prompt_handler.py
│   │   └── video_generator.py
│   ├── content_generator.py
│   ├── text_to_speech.py
│   └── webhook_handler.py
└── tests/
```

## API Usage 🚀

### Webhook Endpoint
```python
POST /generate_video
{
    "input_text": "Story prompt or scenario",
    "scene_config": {
        "num_scenes": 3,          # Number of scenes to generate (1-20)
        "scene_duration": 10,      # Duration of each scene in seconds (1-60)
        "shots_per_scene": 12      # Number of shots per scene (1-12)
    },
    "scene_settings": {
        "precinct_office": {
            "location": "Detective's precinct office",
            "time": "Night",
            "lighting": {
                "main": "Dim fluorescent overhead",
                "accents": "Desk lamp, venetian blind shadows",
                "mood": "Noir, moody"
            },
            "elements": [
                "Wooden desk with scattered files",
                "Rain-streaked windows",
                "Venetian blinds casting shadows",
                "Cork board with pinned evidence",
                "Half-empty coffee cups"
            ],
            "atmosphere": "Tense, noir detective"
        }
    },
    "character_profiles": {
        "DetectiveSarah": {
            "physical": {
                "gender": "Female",
                "age": "Early 40s",
                "ethnicity": "Latina",
                "height": "5'8\"",
                "build": "Athletic",
                "hair": "Dark brown, shoulder-length",
                "eyes": "Dark brown, intense",
                "face": "Angular features, high cheekbones"
            },
            "clothing": {
                "style": "Professional but worn",
                "main": "Charcoal grey suit",
                "accessories": "Silver watch, detective badge"
            },
            "mannerisms": {
                "posture": "Confident but tired",
                "movement": "Deliberate, measured",
                "expression": "Often stern"
            }
        }
    },
    "visual_style": {
        "base_prompt": "high-resolution digital photography, Canon EOS 5D Mark IV",
        "composition": "rule of thirds, golden ratio, cinematic composition",
        "lighting": "dramatic lighting, deep shadows, high contrast"
    },
    "shot_types": [
        {
            "name": "Establishing shot",
            "description": "Set the scene and atmosphere",
            "camera_angles": ["Wide shot", "High angle", "Dutch angle"],
            "focus": "Location and mood"
        }
    ]
}
```

### Configuration Options

#### Scene Configuration
- **num_scenes**: Control the number of scenes (1-20)
- **scene_duration**: Set duration per scene in seconds (1-60)
- **shots_per_scene**: Define shots per scene (1-12)
- Automatic title card generation between scenes

#### Scene Settings
- Define multiple scene locations with detailed attributes
- Control lighting, atmosphere, and key elements
- Customize time of day and mood settings

#### Character Profiles
- Detailed physical descriptions
- Clothing and accessory details
- Mannerisms and behavioral traits
- Consistent visual representation

#### Visual Style
- Base photography settings
- Composition guidelines
- Lighting preferences
- Overall aesthetic direction

#### Shot Types
- Define different types of shots
- Specify camera angles
- Set focus points
- Control visual progression

### Processing Flow
1. **Input Processing**
   - Story prompt received via webhook
   - Scene configuration validation
   - Resource preparation

2. **Dialog Generation**
   - Character-based dialog creation
   - Scene direction integration
   - Emotional markup inclusion

3. **Scene Analysis**
   - Parallel processing with dedicated Gemini instances
   - Scene structure identification
   - Title card generation
   - Transition planning

4. **Audio Generation**
   - Text-to-speech conversion
   - Voice enhancement
   - Audio normalization

5. **Visual Creation**
   - Parallel scene visualization
   - Title card generation
   - Image generation
   - Visual consistency checks

6. **Final Assembly**
   - Title card integration
   - Audio-visual synchronization
   - Transition implementation
   - Output video creation

## Development Guidelines 🛠️

1. **Code Structure**
   - Clear separation of concerns
   - Modular component design
   - Comprehensive error handling
   - Detailed logging

2. **API Design**
   - RESTful endpoints
   - Clear request/response formats
   - Proper status codes
   - Comprehensive documentation

3. **Testing**
   - Unit tests for components
   - Integration tests for pipeline
   - Performance benchmarks
   - Error case coverage

4. **Deployment**
   - Environment configuration
   - API key management
   - Resource scaling
   - Monitoring setup

## Environment Setup 🌍

Required environment variables:
```bash
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
FLUX_API_KEY=your_flux_api_key
```

## Running the Application 🚀

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python server.py
```

3. Test the webhook:
```bash
python test_webhook.py
```

## Replit Deployment 🚀

### Quick Deploy
1. Fork this repository to your Replit account
2. Add the following secrets in your Replit environment:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   FLUX_API_KEY=your_flux_api_key
   ```
3. Click "Run" - the server will start automatically

### Manual Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/podcastfy.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in Replit Secrets:
   - Add each API key as shown above
   - Keys are automatically loaded into the environment

4. Start the server:
   ```bash
   uvicorn podcastfy.webhook_handler:app --host 0.0.0.0 --port 8000
   ```

### Testing on Replit
1. Use the provided test_webhook.py:
   ```bash
   python test_webhook.py
   ```

2. For quick tests, use shorter scene configurations:
   ```python
   "scene_config": {
       "num_scenes": 3,      # Minimal number of scenes
       "scene_duration": 1,  # 1 second per scene
       "shots_per_scene": 12 # Still generate all shots for testing
   }
   ```

### Replit-Specific Features
- Automatic ImageMagick configuration
- Optimized for Replit's environment
- Parallel scene processing
- Automatic fallbacks for resource constraints

### Common Issues
1. ImageMagick Configuration:
   - Automatically configured via replit.nix
   - No manual setup required

2. Memory Management:
   - Scenes are processed in parallel
   - Images are cleaned up after processing
   - Temporary files are managed automatically

3. Performance Optimization:
   - CPU-optimized video encoding
   - Efficient memory usage
   - Parallel processing where possible

## Contributing 🤝

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.
