"""
Conversation Configuration Module

This module handles the loading and management of conversation configuration settings
for the Podcastfy application. It uses a YAML file for conversation-specific configuration settings.
"""

import os
import sys
import logging
from typing import Any, Dict, Optional, List
import yaml

logger = logging.getLogger(__name__)

def get_conversation_config_path(config_file: str = 'conversation_config.yaml'):
    """
    Get the path to the conversation_config.yaml file.
    """
    try:
        # Check if the script is running in a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Look for conversation_config.yaml in the same directory as the script
        config_path = os.path.join(base_path, config_file)
        if os.path.exists(config_path):
            return config_path
        
        # If not found, look in the parent directory (package root)
        config_path = os.path.join(os.path.dirname(base_path), config_file)
        if os.path.exists(config_path):
            return config_path
        
        # If still not found, look in the current working directory
        config_path = os.path.join(os.getcwd(), config_file)
        if os.path.exists(config_path):
            return config_path
        
        raise FileNotFoundError(f"{config_file} not found")
    
    except Exception as e:
        logger.error(f"Error locating {config_file}: {str(e)}")
        return None

class ConversationConfig:
    def __init__(self, config_conversation: Optional[Dict[str, Any]] = None):
        """
        Initialize the ConversationConfig class with a dictionary configuration.
        """
        logger.debug("Initializing ConversationConfig")
        # Load default configuration
        self.config_conversation = self._load_default_config()
        
        # Update with provided config if any
        if config_conversation is not None:
            logger.debug(f"Updating with provided config: {config_conversation}")
            self.configure(config_conversation)
        
        # Set attributes based on the final configuration
        self._set_attributes()
        logger.debug("ConversationConfig initialized")

    def _load_default_config(self) -> Dict[str, Any]:
        """Load the default configuration from conversation_config.yaml."""
        config_path = get_conversation_config_path()
        if config_path:
            logger.debug(f"Loading config from {config_path}")
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.debug(f"Loaded config: {config}")
                return config
        else:
            logger.error("conversation_config.yaml not found")
            raise FileNotFoundError("conversation_config.yaml not found")

    def _set_attributes(self):
        """Set attributes based on the current configuration."""
        logger.debug("Setting attributes")
        for key, value in self.config_conversation.items():
            setattr(self, key, value)

    def configure(self, config_conversation: Dict[str, Any]):
        """
        Configure the conversation settings with the provided dictionary.
        """
        logger.debug(f"Configuring with: {config_conversation}")
        if not isinstance(config_conversation, dict):
            logger.error("Configuration must be a dictionary")
            raise ValueError("Configuration must be a dictionary")
            
        # Update configuration
        self.config_conversation.update(config_conversation)
        logger.debug(f"Updated config: {self.config_conversation}")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value by key.
        """
        value = self.config_conversation.get(key, default)
        logger.debug(f"Getting {key}: {value}")
        return value

    def get_list(self, key: str, default: Optional[List[str]] = None) -> List[str]:
        """
        Get a list configuration value by key.
        """
        if default is None:
            default = []
            
        value = self.config_conversation.get(key, default)
        logger.debug(f"Getting list {key}: {value}")
        
        if isinstance(value, str):
            result = [item.strip() for item in value.split(',')]
        elif isinstance(value, list):
            result = value
        else:
            logger.warning(f"Invalid list value for {key}, using default")
            result = default
            
        logger.debug(f"Returning list for {key}: {result}")
        return result

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ConversationConfig object to a dictionary.
        """
        logger.debug("Converting to dict")
        return self.config_conversation

def load_conversation_config(config_conversation: Optional[Dict[str, Any]] = None) -> ConversationConfig:
    """
    Load and return a ConversationConfig instance.
    """
    logger.debug(f"Loading conversation config with: {config_conversation}")
    return ConversationConfig(config_conversation)

def main() -> None:
    """
    Test the ConversationConfig class and print configuration status.
    """
    try:
        # Create an instance of the ConversationConfig class with default settings
        default_config = load_conversation_config()
        
        print("Default Configuration:")
        for key, value in default_config.config_conversation.items():
            print(f"{key}: {value}")

        # Test with custom configuration
        custom_config = {
            "word_count": 1500,
            "podcast_name": "Custom Podcast",
            "output_language": "Spanish"
        }
        custom_config_instance = load_conversation_config(custom_config)

        print("\nCustom Configuration:")
        for key, value in custom_config_instance.config_conversation.items():
            print(f"{key}: {value}")

        # Test the get method with a default value
        print(f"\nTesting get method with default value:")
        print(f"NON_EXISTENT_KEY: {custom_config_instance.get('NON_EXISTENT_KEY', 'Default Value')}")

    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
