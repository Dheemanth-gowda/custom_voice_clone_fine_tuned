import re
from typing import List, Dict
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class TextProcessingService:
    def __init__(self):
        self.max_text_length = settings.MAX_TEXT_LENGTH
        self.batch_size = settings.BATCH_SIZE

    def clean_text(self, text: str) -> str:
        """
        Clean and format text.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        try:
            # Remove timestamps (e.g., [00:00:00])
            text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)
            
            # Remove special characters
            text = re.sub(r'[^\w\s.,!?-]', '', text)
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            return text.strip()

        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            raise

    def split_into_batches(self, text: str) -> List[str]:
        """
        Split text into batches for processing.
        
        Args:
            text: Input text to split
            
        Returns:
            List of text batches
        """
        try:
            # Clean text first
            text = self.clean_text(text)
            
            # Split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            # Create batches
            batches = []
            current_batch = []
            current_length = 0
            
            for sentence in sentences:
                sentence_length = len(sentence)
                
                if current_length + sentence_length > self.batch_size:
                    if current_batch:
                        batches.append(' '.join(current_batch))
                    current_batch = [sentence]
                    current_length = sentence_length
                else:
                    current_batch.append(sentence)
                    current_length += sentence_length
            
            if current_batch:
                batches.append(' '.join(current_batch))
            
            return batches

        except Exception as e:
            logger.error(f"Error splitting text into batches: {str(e)}")
            raise

    def process_script(self, script: str) -> Dict:
        """
        Process a script for voice generation.
        
        Args:
            script: Input script text
            
        Returns:
            Dict containing processed batches and metadata
        """
        try:
            # Check text length
            if len(script) > self.max_text_length:
                logger.warning(f"Script exceeds maximum length of {self.max_text_length} characters")
            
            # Split into batches
            batches = self.split_into_batches(script)
            
            return {
                "total_batches": len(batches),
                "total_characters": len(script),
                "batches": batches,
                "requires_background_processing": len(script) > self.max_text_length
            }

        except Exception as e:
            logger.error(f"Error processing script: {str(e)}")
            raise

    def format_script(self, script: str) -> str:
        """
        Format a script for better voice generation.
        
        Args:
            script: Input script text
            
        Returns:
            Formatted script text
        """
        try:
            # Clean text
            text = self.clean_text(script)
            
            # Add pauses for punctuation
            text = re.sub(r'([.,!?])', r'\1 ', text)
            
            # Remove multiple spaces
            text = ' '.join(text.split())
            
            return text.strip()

        except Exception as e:
            logger.error(f"Error formatting script: {str(e)}")
            raise 