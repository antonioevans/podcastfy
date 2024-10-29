"""
Prompt Handler Module

This module handles the loading and merging of prompt templates.
"""

import os
import yaml
from typing import Dict, Any, Optional

def load_custom_prompt(path: str) -> str:
    """Load custom prompt from file."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

class PromptHandler:
    def __init__(self, base_prompt_path: str, custom_prompt_path: Optional[str] = None):
        """Initialize the PromptHandler."""
        self.base_prompt_path = base_prompt_path
        self.custom_prompt_path = custom_prompt_path

    def load_base_prompt(self) -> str:
        """Load the base prompt template."""
        with open(self.base_prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_custom_prompt(self) -> Dict[str, Any]:
        """Load the custom prompt configuration."""
        if not self.custom_prompt_path or not os.path.exists(self.custom_prompt_path):
            return {}
        
        with open(self.custom_prompt_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def format_custom_section(self, config: Dict[str, Any]) -> str:
        """Format custom configuration into prompt section."""
        sections = []
        
        # Dark opening soliloquy by Emma
        sections.append("""OPENING SOLILOQUY:

<EmmaLawson>
*whispers with trembling voice* Day one in this... place. The cold seeps through the concrete, biting at my bare feet. They took my shoes... why did they take my shoes? *nervous laugh* 

The darkness here isn't natural. It moves, shifts like something alive. And the sounds... *shaky breath* I hear others, crying, whimpering from other cages. Yes, cages. Like animals. We're all in cages.

*voice drops lower* But that's not the worst part. Sometimes, in the shadows, I swear I see... a clown. A real clown, with a twisted smile that glows in the dark. Am I going mad already? *long pause* No... no, I saw it. I know I saw it.

*sudden sharp intake of breath* Someone's coming. I should... I should stop talking. But if anyone finds this... please... help us.
</EmmaLawson>""")
        
        # Add each configured section
        if config.get('topic'):
            sections.append(f"TOPIC: {config['topic']}")
        
        if config.get('url'):
            sections.append(f"SOURCE: {config['url']}")
            
        if config.get('style'):
            sections.append(f"STYLE: {config['style']}")
            
        if config.get('tone'):
            sections.append(f"TONE: {config['tone']}")
            
        if config.get('length'):
            sections.append(f"LENGTH: {config['length']}")
            
        if config.get('background'):
            sections.append(f"BACKGROUND:\n{config['background']}")
            
        if config.get('audience'):
            sections.append(f"TARGET AUDIENCE: {config['audience']}")
            
        if config.get('call_to_action'):
            sections.append(f"CALL TO ACTION:\n{config['call_to_action']}")
            
        if config.get('ad_breaks'):
            ad_sections = []
            for ad in config['ad_breaks']:
                ad_sections.append(f"- {ad['position']}: {ad['content']}")
            sections.append("AD BREAKS:\n" + "\n".join(ad_sections))
            
        if config.get('language'):
            sections.append(f"LANGUAGE: {config['language']}")
            
        return "\n\n".join(sections)

    def merge_prompts(self) -> str:
        """Merge base prompt with custom configuration."""
        base_prompt = self.load_base_prompt()
        custom_config = self.load_custom_prompt()
        
        if not custom_config:
            return base_prompt
            
        custom_section = self.format_custom_section(custom_config)
        
        # Insert custom section after the initial instruction
        split_point = base_prompt.find("\n\n")
        if split_point == -1:
            split_point = 0
            
        merged_prompt = (
            base_prompt[:split_point] + 
            "\n\nEPISODE CONFIGURATION:\n\n" + 
            custom_section +
            base_prompt[split_point:]
        )
        
        return merged_prompt

def main():
    """Test the PromptHandler."""
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Set up paths
        base_prompt_path = os.path.join(project_root, 'data', 'prompts', 'prompt_v1.txt')
        custom_prompt_path = os.path.join(project_root, 'data', 'prompts', 'custom_prompt.yaml')
        
        # Create handler and merge prompts
        handler = PromptHandler(base_prompt_path, custom_prompt_path)
        merged_prompt = handler.merge_prompts()
        
        # Save merged prompt for testing
        output_path = os.path.join(project_root, 'data', 'prompts', 'merged_prompt.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(merged_prompt)
            
        print(f"Merged prompt saved to: {output_path}")
        
    except Exception as e:
        print(f"Error in prompt handler: {str(e)}")
        raise

if __name__ == "__main__":
    main()
