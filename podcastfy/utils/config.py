"""
Configuration Module

This module handles the loading and management of configuration settings for the Podcastfy application.
It uses environment variables to securely store and access API keys and other sensitive information,
and a YAML file for non-sensitive configuration settings.
"""

import os
from dotenv import load_dotenv
from typing import Any, Dict, Optional
import yaml

def get_config_path(config_file: str = 'config.yaml'):
    """
    Get the path to the config.yaml file.
    
    Returns:
        str: The path to the config.yaml file.
    """
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Look for config.yaml in the package root
        config_path = os.path.join(base_path, config_file)
        if os.path.exists(config_path):
            return config_path
        
        # If not found, look in the current working directory
        config_path = os.path.join(os.getcwd(), config_file)
        if os.path.exists(config_path):
            return config_path
        
        raise FileNotFoundError(f"{config_file} not found")
    
    except Exception as e:
        print(f"Error locating {config_file}: {str(e)}")
        return None

class Config:
    # List of protected keys that should only come from environment
    PROTECTED_KEYS = {
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY',
        'GEMINI_API_KEY',
        'FLUX_API_KEY',
        'JINA_API_KEY'
    }

    def __init__(self, config_file: str = 'config.yaml'):
        """
        Initialize the Config class by loading environment variables and YAML configuration.

        Args:
            config_file (str): Path to the YAML configuration file. Defaults to 'config.yaml'.
        """
        # Load .env from project root
        env_path = os.path.join('C:\\', 'appz', 'podcastfy', '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"Loaded environment variables from {env_path}")
        else:
            print(f"Warning: .env file not found at {env_path}")
        
        # Load API keys from environment variables
        self._load_api_keys()
        
        # Load non-sensitive config from YAML
        config_path = get_config_path(config_file)
        if config_path:
            with open(config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
                # Remove API keys from config to prevent overwriting
                for key in self.PROTECTED_KEYS:
                    self.config.pop(key, None)
        else:
            print("Could not locate config.yaml")
            self.config = {}
        
        # Set attributes based on YAML config
        self._set_attributes()

    def _load_api_keys(self):
        """Load API keys from environment variables."""
        # Load each protected key from environment
        for key in self.PROTECTED_KEYS:
            value = os.getenv(key)
            if value:
                setattr(self, key, value)
            else:
                print(f"Warning: {key} not found in environment variables")
                setattr(self, key, "")

    def _set_attributes(self):
        """Set attributes based on the current configuration."""
        # Only set non-protected attributes from config
        for key, value in self.config.items():
            if key.upper() not in self.PROTECTED_KEYS:
                setattr(self, key.upper(), value)

        # Ensure output directories exist
        if 'output_directories' in self.config:
            for dir_type, dir_path in self.config['output_directories'].items():
                os.makedirs(dir_path, exist_ok=True)

    def configure(self, **kwargs):
        """
        Configure the settings by updating the config dictionary and relevant attributes.

        Args:
            **kwargs: Keyword arguments representing configuration keys and values to update.
        """
        for key, value in kwargs.items():
            if key in self.PROTECTED_KEYS:
                # Only update protected keys if they're empty
                if not getattr(self, key, None):
                    setattr(self, key, value)
            elif key in self.config:
                self.config[key] = value
                setattr(self, key.upper(), value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key (str): The configuration key to retrieve.
            default (Optional[Any]): The default value if the key is not found.

        Returns:
            Any: The value associated with the key, or the default value if not found.
        """
        if key.upper() in self.PROTECTED_KEYS:
            return getattr(self, key.upper(), default)
        return self.config.get(key, default)

def load_config() -> Config:
    """
    Load and return a Config instance.

    Returns:
        Config: An instance of the Config class.
    """
    return Config()

def main() -> None:
    """
    Test the Config class and print configuration status.
    """
    # Create an instance of the Config class
    config = load_config()
    
    # Test each configuration value
    print("Testing Config class:")
    print(f"OPENAI_API_KEY: {'Set' if config.OPENAI_API_KEY else 'Not set'}")
    print(f"ELEVENLABS_API_KEY: {'Set' if config.ELEVENLABS_API_KEY else 'Not set'}")
    print(f"GEMINI_API_KEY: {'Set' if config.GEMINI_API_KEY else 'Not set'}")
    print(f"FLUX_API_KEY: {'Set' if config.FLUX_API_KEY else 'Not set'}")
    print(f"JINA_API_KEY: {'Set' if config.JINA_API_KEY else 'Not set'}")

    # Print a warning for any missing configuration
    missing_config = []
    for key in Config.PROTECTED_KEYS:
        if not getattr(config, key):
            missing_config.append(key)

    if missing_config:
        print("\nWarning: The following configuration values are missing:")
        for config_name in missing_config:
            print(f"- {config_name}")
        print("Please ensure these are set in your .env file.")
    else:
        print("\nAll configuration values are set.")

    # Test the get method with a default value
    print(f"\nTesting get method with default value:")
    print(f"NON_EXISTENT_KEY: {config.get('NON_EXISTENT_KEY', 'Default Value')}")

if __name__ == "__main__":
    main()
