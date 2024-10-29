"""Test Webhook - Full Pipeline Test"""
import requests
import aiohttp
import asyncio
import json
from typing import Dict, Any

# Scene configuration - controlled via webhook
SCENE_CONFIG = {
    "num_scenes": 3, # Number of scenes to generate
    "scene_duration": 80, # Duration of each scene in seconds
    "shots_per_scene": 12  # This will generate 36 total images (3 scenes × 12 shots)
}

# Scene and character configurations
SCENE_SETTINGS = {
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
    },
    "interrogation_room": {
        "location": "Police interrogation room",
        "time": "Various",
        "lighting": {
            "main": "Harsh overhead light",
            "accents": "Shadows from light fixture",
            "mood": "Stark, oppressive"
        },
        "elements": [
            "Metal table bolted to floor",
            "Two metal chairs",
            "Two-way mirror",
            "Bare concrete walls",
            "Single door with reinforced frame"
        ],
        "atmosphere": "Claustrophobic, tense"
    }
}

CHARACTER_PROFILES = {
    "DetectiveSarah": {
        "physical": {
            "gender": "Female",
            "age": "Early 40s",
            "ethnicity": "Latina",
            "height": "5'8\"",
            "build": "Athletic",
            "hair": "Dark brown, shoulder-length, slightly messy",
            "eyes": "Dark brown, intense, with slight crow's feet",
            "face": "Angular features, high cheekbones, determined expression"
        },
        "clothing": {
            "style": "Professional but worn",
            "main": "Charcoal grey suit, slightly rumpled",
            "shirt": "White button-up, top button undone",
            "shoes": "Well-worn black oxford shoes",
            "accessories": "Silver watch, detective badge on belt"
        },
        "mannerisms": {
            "posture": "Confident but tired",
            "movement": "Deliberate, measured",
            "expression": "Often stern, rarely smiles"
        }
    },
    "OfficerMike": {
        "physical": {
            "gender": "Male",
            "age": "Mid 20s",
            "ethnicity": "Caucasian",
            "height": "5'10\"",
            "build": "Slim, athletic",
            "hair": "Short blonde, neatly combed",
            "eyes": "Blue, alert, often darting",
            "face": "Boyish features, clean-shaven"
        },
        "clothing": {
            "style": "Rookie detective trying to look seasoned",
            "main": "Navy blue suit, slightly too new",
            "shirt": "Light blue button-up, pressed",
            "shoes": "New black dress shoes",
            "accessories": "Police badge, silver tie clip"
        },
        "mannerisms": {
            "posture": "Slightly tense",
            "movement": "Sometimes fidgety",
            "expression": "Often uncertain, eager to please"
        }
    },
    "EmmaLawson": {
        "physical": {
            "gender": "Female",
            "age": "19",
            "ethnicity": "Pale complexion",
            "height": "5'6\"",
            "build": "Slim, graceful",
            "hair": "Long black, perfectly styled",
            "eyes": "Grey, unnaturally calm",
            "face": "Delicate features, porcelain-like"
        },
        "clothing": {
            "style": "Expensive, gothic elegance",
            "main": "Black designer dress",
            "accessories": "Pearl necklace, silver rings",
            "shoes": "Black stiletto heels",
            "details": "Dark red lipstick, manicured nails"
        },
        "mannerisms": {
            "posture": "Poised, controlled",
            "movement": "Deliberate, almost predatory",
            "expression": "Slight knowing smile"
        }
    }
}

# Visual style configuration
VISUAL_STYLE = {
    "base_prompt": (
        "high-resolution digital photography, Canon EOS 5D Mark IV, "
        "cinematic lighting, dramatic shadows, moody atmosphere, "
        "detailed, 8k, octane render, noir style film"
    ),
    "composition": (
        "rule of thirds, golden ratio, cinematic composition, "
        "film noir aesthetic, dramatic angles"
    ),
    "lighting": (
        "dramatic lighting, deep shadows, high contrast, "
        "rim lighting, atmospheric haze"
    )
}

# Shot types configuration
SHOT_TYPES = [
    {
        "name": "Establishing shot",
        "description": "Set the scene and atmosphere",
        "camera_angles": ["Wide shot", "High angle", "Dutch angle"],
        "focus": "Location and mood"
    },
    {
        "name": "Character shot",
        "description": "Focus on character interactions and emotions",
        "camera_angles": ["Medium shot", "Close-up", "Over-the-shoulder"],
        "focus": "Character dynamics"
    },
    {
        "name": "Detail shot",
        "description": "Highlight key elements and build tension",
        "camera_angles": ["Extreme close-up", "Insert shot", "Low angle"],
        "focus": "Important objects or details"
    }
]

async def test_webhook():
    """Test the webhook endpoint asynchronously."""
    url = "http://127.0.0.1:8000/generate_video"

    # Input prompt that will trigger the scene generation
    payload = {
        "input_text": "A detective investigates a series of mysterious disappearances in New York City. The victims all have one thing in common: they were last seen near an abandoned church. The detective's partner is nervous about the case, citing old rumors about the church's dark history.",
        "scene_config": SCENE_CONFIG,  # Scene configuration controlled via webhook
        "scene_settings": SCENE_SETTINGS,
        "character_profiles": CHARACTER_PROFILES,
        "visual_style": VISUAL_STYLE,
        "shot_types": SHOT_TYPES
    }

    print("\nStarting noir podcast generation with configuration:")
    print(f"Number of scenes: {SCENE_CONFIG['num_scenes']}")
    print(f"Scene duration: {SCENE_CONFIG['scene_duration']} seconds")
    print(f"Shots per scene: {SCENE_CONFIG['shots_per_scene']}")
    print(f"Total expected images: {SCENE_CONFIG['num_scenes'] * SCENE_CONFIG['shots_per_scene']}")
    print("\nThis will trigger the full pipeline:")
    print("1. Generate dialog/scenes with Gemini")
    print("2. Convert to speech with OpenAI + ElevenLabs")
    print("3. Generate noir-style images with Flux")
    print("4. Create final video with synchronized audio/images")
    print("\nThis may take several minutes...\n")

    # Configure timeout and connection settings
    timeout = aiohttp.ClientTimeout(total=None)  # No timeout
    conn = aiohttp.TCPConnector(force_close=True)

    try:
        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Success! Response: {json.dumps(result, indent=2)}")
                else:
                    error = await response.text()
                    print(f"Error: Status {response.status}")
                    print(f"Details: {error}")
    except asyncio.TimeoutError:
        print("Request timed out - but the server is still processing.")
        print("Check the server logs for progress.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_webhook())
