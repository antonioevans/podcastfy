"""Content Generator Module"""

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms.llamafile import Llamafile
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from podcastfy.utils.config_conversation import load_conversation_config
from podcastfy.utils.config import load_config
from podcastfy.utils.prompt_handler import PromptHandler, load_custom_prompt
import logging
import re

logger = logging.getLogger(__name__)

# Load .env from project root
env_path = os.path.join('C:\\', 'appz', 'podcastfy', '.env')
load_dotenv(env_path)

# Valid speaker tags
VALID_SPEAKERS = {"DetectiveSarah", "OfficerMike", "EmmaLawson", "Maria"}

class LLMBackend:
    def __init__(
        self,
        is_local: bool,
        temperature: float,
        max_output_tokens: int,
        model_name: str,
    ):
        """Initialize the LLMBackend."""
        self.is_local = is_local
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.model_name = model_name

        if is_local:
            self.llm = Llamafile()
        else:
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                google_api_key=os.getenv('GEMINI_API_KEY')
            )

class ContentGenerator:
    def __init__(
        self, api_key: str, conversation_config: Optional[Dict[str, Any]] = None,
        custom_prompt_path: Optional[str] = None
    ):
        """Initialize the ContentGenerator."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables or constructor")
            
        os.environ["GOOGLE_API_KEY"] = self.api_key
        self.config = load_config()
        self.content_generator_config = self.config.get("content_generator", {})
        
        logger.debug("Loading conversation config")
        self.config_conversation = load_conversation_config()
        if conversation_config:
            logger.debug(f"Updating with provided config: {conversation_config}")
            self.config_conversation.configure(conversation_config)

        # Load base prompt
        self.base_prompt_path = os.path.join('C:\\', 'appz', 'podcastfy', 'data', 'prompts', 'prompt_v1.txt')
        if not os.path.exists(self.base_prompt_path):
            raise FileNotFoundError(f"Base prompt file not found at {self.base_prompt_path}")
            
        with open(self.base_prompt_path, 'r', encoding='utf-8') as f:
            self.base_prompt = f.read()
        logger.debug("Loaded base prompt")

    def validate_dialog(self, text: str) -> str:
        """Validate and clean dialog content."""
        try:
            # Find all speaker tags
            pattern = r'<(\w+)>'
            speakers = set(re.findall(pattern, text))
            
            # Check for invalid speakers
            invalid_speakers = speakers - VALID_SPEAKERS
            if invalid_speakers:
                logger.warning(f"Found invalid speakers: {invalid_speakers}")
                # Remove any structural tags completely
                for invalid in invalid_speakers:
                    text = re.sub(f'<{invalid}>.*?</{invalid}>', '', text, flags=re.DOTALL)
                # Clean up extra newlines
                text = re.sub(r'\n\s*\n', '\n', text)
            
            # Ensure all required speakers are present
            missing_speakers = VALID_SPEAKERS - speakers
            if missing_speakers:
                logger.warning(f"Missing required speakers: {missing_speakers}")
                # Add default lines for missing speakers
                for speaker in missing_speakers:
                    if speaker == "Maria":
                        text = f"<Maria>\n*professional tone* The investigation continues.\n</Maria>\n\n{text}"
                    elif speaker == "DetectiveSarah":
                        text += f"\n\n<DetectiveSarah>\n*determined* We'll get to the bottom of this.\n</DetectiveSarah>"
                    elif speaker == "OfficerMike":
                        text += f"\n\n<OfficerMike>\n*supportive* I'll check the records right away.\n</OfficerMike>"
                    elif speaker == "EmmaLawson":
                        text += f"\n\n<EmmaLawson>\n*cryptic* Some mysteries are better left unsolved.\n</EmmaLawson>"
            
            # Ensure proper XML structure
            lines = text.split('\n')
            current_tag = None
            fixed_lines = []
            
            for line in lines:
                if line.strip():
                    # Check for opening tag
                    open_match = re.match(r'<(\w+)>', line)
                    if open_match:
                        if current_tag:  # Close any open tag
                            fixed_lines.append(f"</{current_tag}>")
                        current_tag = open_match.group(1)
                        fixed_lines.append(line)
                    # Check for closing tag
                    elif re.match(f'</({"|".join(VALID_SPEAKERS)})>', line):
                        current_tag = None
                        fixed_lines.append(line)
                    # Content line
                    else:
                        if current_tag and not line.startswith('*'):
                            line = f"*neutral* {line}"
                        fixed_lines.append(line)
            
            # Close any remaining open tag
            if current_tag:
                fixed_lines.append(f"</{current_tag}>")
            
            return '\n'.join(fixed_lines).strip()
        except Exception as e:
            logger.error(f"Error validating dialog: {str(e)}")
            raise

    def generate_qa_content(
        self,
        input_texts: str = "",
        image_file_paths: List[str] = None,
        output_filepath: Optional[str] = None,
        is_local: bool = False,
    ) -> str:
        """Generate dialog content based on input text."""
        try:
            logger.debug("Starting content generation")
            if image_file_paths is None:
                image_file_paths = []
                
            llmbackend = LLMBackend(
                is_local=is_local,
                temperature=0.7,
                max_output_tokens=8192,
                model_name="gemini-1.5-pro-latest"
            )

            # Format prompt with input text
            dialog_prompt = f"{self.base_prompt}\n\nStory to adapt:\n{input_texts}"

            # Generate dialog
            messages = [
                SystemMessage(content="""You are a noir dialog writer creating character interactions.
CRITICAL: Use ONLY these tags: <DetectiveSarah>, <OfficerMike>, <EmmaLawson>, <Maria>
Start IMMEDIATELY with character dialog - NO structural tags or metadata.
Each character must speak at least twice.
Total dialog should be 3-5 minutes when spoken."""),
                HumanMessage(content=dialog_prompt)
            ]

            logger.debug("Generating dialog")
            response = llmbackend.llm.invoke(messages)
            
            # Validate and clean dialog
            result = self.validate_dialog(response.content)
            
            logger.info("Content generated successfully")

            if output_filepath:
                logger.debug(f"Saving content to {output_filepath}")
                with open(output_filepath, "w", encoding='utf-8') as file:
                    file.write(result)
                logger.info(f"Response content saved to {output_filepath}")

            return result
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise

def main(seed: int = 42, is_local: bool = False) -> None:
    """Main function to test the ContentGenerator."""
    try:
        env_path = os.path.join('C:\\', 'appz', 'podcastfy', '.env')
        load_dotenv(env_path)
        
        config = load_config()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key and not is_local:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        content_generator = ContentGenerator(api_key=api_key)

        input_text = "A detective investigates a series of mysterious disappearances"
        response = content_generator.generate_qa_content(input_text, is_local=is_local)

        print("Generated Content:")
        output_file = os.path.join('C:\\', 'appz', 'podcastfy', 'data', 'transcripts', 'response.txt')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding='utf-8') as file:
            file.write(response)

    except Exception as e:
        logger.error(f"An error occurred while generating content: {str(e)}")
        raise

if __name__ == "__main__":
    main()
